"""
LLM Service for Pulse AI using watsonx.ai
Handles query parsing and explanation generation with fallback mechanisms.
"""

import json
import logging
import re
import time
from datetime import datetime, timedelta, date
from typing import Any, Optional

import httpx
from langchain_ibm import WatsonxLLM

from app.config.settings import settings
from app.models.search import SearchIntent
from app.models.event import Event
from app.models.recommendation import RecommendationScore


logger = logging.getLogger(__name__)

_INTENT_CACHE: dict[str, tuple[float, SearchIntent]] = {}
_CHAT_MODEL_CACHE: tuple[float, list[str]] | None = None
_IAM_TOKEN_CACHE: tuple[float, str] | None = None
_WATSONX_UNAVAILABLE_UNTIL = 0.0


class LLMService:
    """Service for LLM-powered query understanding and explanation generation."""
    
    def __init__(self):
        """Initialize watsonx.ai LLM with credentials from settings."""
        self.llm = None
        self.last_parse_source = "unknown"
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize WatsonxLLM with error handling."""
        # Intent parsing uses the watsonx Chat API directly. Avoid eager SDK
        # authentication here so startup and demo/test paths stay fast and quiet.
        self.llm = None
    
    async def parse_query(self, query: str) -> SearchIntent:
        """
        Parse natural language query into structured SearchIntent.
        Falls back to deterministic parsing if LLM fails.
        
        Args:
            query: Natural language search query
            
        Returns:
            SearchIntent with extracted information
        """
        cache_key = self._normalise_query_key(query)
        cached = _INTENT_CACHE.get(cache_key)
        if cached and time.time() - cached[0] < settings.intent_cache_ttl_seconds:
            self.last_parse_source = "cache"
            return cached[1]

        if not settings.demo_mode:
            try:
                intent = await self._chat_parse_query(query)
                self.last_parse_source = "llm"
                _INTENT_CACHE[cache_key] = (time.time(), intent)
                return intent
            except Exception as exc:
                logger.warning(
                    "LLM intent parsing failed; falling back to deterministic parser",
                    extra={"error_type": type(exc).__name__},
                )
        
        # Fallback to deterministic parser
        self.last_parse_source = "deterministic"
        intent = self._deterministic_fallback(query)
        _INTENT_CACHE[cache_key] = (time.time(), intent)
        return intent

    def _normalise_query_key(self, query: str) -> str:
        return " ".join(query.lower().strip().split())

    async def _chat_parse_query(self, query: str) -> SearchIntent:
        """Use watsonx Chat API for JSON-only intent extraction when available."""
        token = await self._get_iam_token()
        model_id = await self._select_chat_model(token)
        today = date.today().isoformat()

        prompt = f"""Today is {today}.
Extract the event-search intent from the user query.
Return ONLY a valid JSON object with these keys:
city, country, category, keyword, date_from, date_to, budget_max, currency, preferences.
Dates must be YYYY-MM-DD. Use null for unknown values.
For relative date phrases, resolve them against Today.

User query: {query}"""

        payload = {
            "model_id": model_id,
            "project_id": settings.watsonx_project_id,
            "messages": [
                {"role": "system", "content": "You extract event search intent as strict JSON only."},
                {"role": "user", "content": prompt},
            ],
            "parameters": {
                "temperature": 0,
                "max_tokens": 300,
            },
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            response = await client.post(
                f"{settings.watsonx_url.rstrip('/')}/ml/v1/text/chat",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                params={"version": "2024-10-10"},
                json=payload,
            )
            response.raise_for_status()
            body = response.json()

        choices = body.get("choices") or []
        content = (choices[0].get("message") or {}).get("content") if choices else ""
        data = self._extract_json(content)
        return self._intent_from_data(query, data)

    async def _get_iam_token(self) -> str:
        global _IAM_TOKEN_CACHE, _WATSONX_UNAVAILABLE_UNTIL

        if _IAM_TOKEN_CACHE and time.time() < _IAM_TOKEN_CACHE[0]:
            return _IAM_TOKEN_CACHE[1]
        if time.time() < _WATSONX_UNAVAILABLE_UNTIL:
            raise RuntimeError("watsonx unavailable")

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                response = await client.post(
                    "https://iam.cloud.ibm.com/identity/token",
                    data={
                        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                        "apikey": settings.watsonx_api_key,
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                    },
                )
                response.raise_for_status()
                token = response.json()["access_token"]
        except Exception:
            _WATSONX_UNAVAILABLE_UNTIL = time.time() + 300
            raise

        _IAM_TOKEN_CACHE = (time.time() + 3300, token)
        return token

    async def _select_chat_model(self, token: str) -> str:
        models = await self._list_chat_models(token)

        if settings.watsonx_chat_model and settings.watsonx_chat_model in models:
            return settings.watsonx_chat_model

        preferred_fragments = (
            "granite-3-2b-instruct",
            "granite-3-8b-instruct",
            "granite-13b-chat",
            "granite",
        )
        for fragment in preferred_fragments:
            match = next((model for model in models if fragment in model and "deprecated" not in model), None)
            if match:
                return match

        if models:
            return models[0]

        return settings.watsonx_chat_model or settings.watsonx_model

    async def _list_chat_models(self, token: str) -> list[str]:
        global _CHAT_MODEL_CACHE

        if _CHAT_MODEL_CACHE and time.time() - _CHAT_MODEL_CACHE[0] < 3600:
            return _CHAT_MODEL_CACHE[1]

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.watsonx_url.rstrip('/')}/ml/v1/foundation_model_specs",
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                params={"version": "2024-10-10", "filters": "function_text_chat"},
            )
            response.raise_for_status()
            body = response.json()

        models = [
            item.get("model_id")
            for item in body.get("resources", [])
            if item.get("model_id")
        ]
        _CHAT_MODEL_CACHE = (time.time(), models)
        return models

    def _extract_json(self, content: Any) -> dict:
        if isinstance(content, dict):
            return content

        text = str(content or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in LLM response")
            return json.loads(json_match.group())

    def _intent_from_data(self, query: str, data: dict) -> SearchIntent:
        if not isinstance(data, dict):
            raise ValueError("LLM output was not a JSON object")

        date_from = self._parse_optional_date(data.get("date_from"))
        date_to = self._parse_optional_date(data.get("date_to"))
        preferences = data.get("preferences") if isinstance(data.get("preferences"), list) else []

        return SearchIntent(
            raw_query=query,
            city=self._normalise_optional_str(data.get("city")),
            country=self._normalise_optional_str(data.get("country")),
            category=self._normalise_optional_str(data.get("category")),
            keyword=self._normalise_optional_str(data.get("keyword")),
            date_from=date_from,
            date_to=date_to,
            budget_max=self._parse_optional_float(data.get("budget_max")),
            currency=self._normalise_optional_str(data.get("currency")) or "USD",
            preferences=[str(item) for item in preferences[:8]],
        )

    def _normalise_optional_str(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _parse_optional_date(self, value: Any) -> Optional[date]:
        if not value:
            return None
        if isinstance(value, date):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()

    def _parse_optional_float(self, value: Any) -> Optional[float]:
        if value in (None, ""):
            return None
        return float(value)
    
    async def _llm_parse_query(self, query: str) -> SearchIntent:
        """Use watsonx.ai to parse query into structured format."""
        
        prompt = f"""Extract structured information from this event search query and return ONLY valid JSON.

Query: "{query}"

Return JSON with these fields (use null for missing values):
- city: string (city name)
- country: string (country name, default "United States" if city is US)
- category: string (music, sports, arts, theater, family, etc.)
- keyword: string (specific search terms)
- date_from: string (ISO date YYYY-MM-DD or null)
- date_to: string (ISO date YYYY-MM-DD or null)
- budget_max: number (max price or null)
- currency: string (USD, EUR, GBP)
- preferences: array of strings (user preferences)

Examples:
Query: "Find electronic music in Berlin this weekend under $100"
{{"city": "Berlin", "country": "Germany", "category": "music", "keyword": "electronic", "date_from": "{(datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')}", "date_to": "{(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}", "budget_max": 100, "currency": "USD", "preferences": ["electronic", "music", "nightlife"]}}

Query: "Jazz concerts in New York next month"
{{"city": "New York", "country": "United States", "category": "music", "keyword": "jazz", "date_from": "{(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}", "date_to": "{(datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')}", "budget_max": null, "currency": "USD", "preferences": ["jazz", "concerts"]}}

Now extract from: "{query}"

Return ONLY the JSON object, no other text:"""

        response = self.llm.invoke(prompt)
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in LLM response")
        
        data = json.loads(json_match.group())
        
        # Convert date strings to date objects
        if data.get('date_from'):
            data['date_from'] = datetime.fromisoformat(data['date_from']).date()
        if data.get('date_to'):
            data['date_to'] = datetime.fromisoformat(data['date_to']).date()
        
        return SearchIntent(
            raw_query=query,
            city=data.get('city'),
            country=data.get('country'),
            category=data.get('category'),
            keyword=data.get('keyword'),
            date_from=data.get('date_from'),
            date_to=data.get('date_to'),
            budget_max=data.get('budget_max'),
            currency=data.get('currency', 'USD'),
            preferences=data.get('preferences', [])
        )
    
    def _deterministic_fallback(self, query: str) -> SearchIntent:
        """
        Deterministic regex-based query parser as fallback.
        Extracts basic information when LLM is unavailable.
        """
        query_lower = query.lower()
        
        # Extract city (common patterns)
        city = None
        city_patterns = [
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'near\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        ]
        for pattern in city_patterns:
            match = re.search(pattern, query)
            if match:
                city = match.group(1)
                break
        
        # Extract category
        category = None
        category_keywords = {
            'music': ['music', 'concert', 'band', 'singer', 'dj', 'festival'],
            'sports': ['sports', 'game', 'match', 'football', 'basketball', 'baseball'],
            'arts': ['art', 'gallery', 'exhibition', 'museum'],
            'theater': ['theater', 'theatre', 'play', 'musical', 'show'],
            'family': ['family', 'kids', 'children'],
        }
        for cat, keywords in category_keywords.items():
            if any(kw in query_lower for kw in keywords):
                category = cat
                break
        
        # Extract date hints
        date_from = None
        date_to = None
        today = datetime.now().date()
        
        if 'today' in query_lower:
            date_from = today
            date_to = today
        elif 'tomorrow' in query_lower:
            date_from = today + timedelta(days=1)
            date_to = today + timedelta(days=1)
        elif 'this weekend' in query_lower or 'weekend' in query_lower:
            # Next Saturday
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7
            date_from = today + timedelta(days=days_until_saturday)
            date_to = date_from + timedelta(days=1)
        elif 'next week' in query_lower:
            date_from = today + timedelta(days=7)
            date_to = today + timedelta(days=14)
        elif 'next month' in query_lower:
            date_from = today + timedelta(days=30)
            date_to = today + timedelta(days=60)
        
        # Extract budget
        budget_max = None
        budget_patterns = [
            r'under\s+\$?(\d+)',
            r'below\s+\$?(\d+)',
            r'less than\s+\$?(\d+)',
            r'max\s+\$?(\d+)',
        ]
        for pattern in budget_patterns:
            match = re.search(pattern, query_lower)
            if match:
                budget_max = float(match.group(1))
                break
        
        # Extract keywords (remove common words)
        stop_words = {'in', 'at', 'near', 'find', 'show', 'me', 'the', 'a', 'an', 'for', 'to', 'under', 'below'}
        words = query_lower.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        keyword = ' '.join(keywords[:3]) if keywords else None
        
        return SearchIntent(
            raw_query=query,
            city=city,
            country="United States" if city else None,
            category=category,
            keyword=keyword,
            date_from=date_from,
            date_to=date_to,
            budget_max=budget_max,
            currency="USD",
            preferences=keywords[:5]
        )
    
    async def generate_explanation(
        self, 
        event: Event, 
        score: RecommendationScore
    ) -> str:
        """
        Generate natural language explanation for why an event was recommended.
        
        Args:
            event: The recommended event
            score: The recommendation score with component breakdown
            
        Returns:
            Human-readable explanation string
        """
        # Keep explanations deterministic in the hot path; watsonx is reserved for intent parsing.
        return self._template_explanation(event, score)
    
    async def _llm_generate_explanation(
        self, 
        event: Event, 
        score: RecommendationScore
    ) -> str:
        """Use watsonx.ai to generate personalized explanation."""
        
        prompt = f"""Generate a brief, friendly explanation (2-3 sentences) for why this event is recommended.

Event: {event.title}
Category: {event.category}
Venue: {event.venue_name}, {event.venue_city}
Date: {event.start_datetime}
Price: {event.price_min}-{event.price_max} {event.currency}

Recommendation Score: {score.total_score:.2f}/100
- Relevance: {score.relevance_score:.1f}
- Popularity: {score.popularity_score:.1f}
- Affordability: {score.affordability_score:.1f}
- Date Match: {score.date_match_score:.1f}
- Context: {score.context_score:.1f}

Write a natural, conversational explanation focusing on the strongest matching factors. Keep it under 50 words:"""

        response = self.llm.invoke(prompt)
        return response.strip()
    
    def _template_explanation(
        self, 
        event: Event, 
        score: RecommendationScore
    ) -> str:
        """Generate template-based explanation as fallback."""
        
        reasons = []
        
        if score.relevance_score > 80:
            reasons.append(f"highly relevant to your search")
        elif score.relevance_score > 60:
            reasons.append(f"matches your interests")
        
        if score.popularity_score > 70:
            reasons.append("popular event")
        
        if score.affordability_score > 80:
            reasons.append("within your budget")
        
        if score.date_match_score > 80:
            reasons.append("perfect timing")
        
        if score.context_score > 70:
            reasons.append("great location")
        
        if not reasons:
            reasons.append("good match for your search")
        
        reason_text = ", ".join(reasons[:3])
        
        return f"This {event.category} event is recommended because it's {reason_text}. Score: {score.total_score:.0f}/100."


# Made with Bob
