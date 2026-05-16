"""
LLM Service for Pulse AI using watsonx.ai
Handles query parsing and explanation generation with fallback mechanisms.
"""

import json
import re
from datetime import datetime, timedelta, date
from typing import Optional
from langchain_ibm import WatsonxLLM

from app.config.settings import settings
from app.models.search import SearchIntent
from app.models.event import Event
from app.models.recommendation import RecommendationScore


class LLMService:
    """Service for LLM-powered query understanding and explanation generation."""
    
    def __init__(self):
        """Initialize watsonx.ai LLM with credentials from settings."""
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize WatsonxLLM with error handling."""
        try:
            self.llm = WatsonxLLM(
                model_id="ibm/granite-8b-code-instruct",
                url=settings.watsonx_url,
                apikey=settings.watsonx_api_key,
                project_id=settings.watsonx_project_id,
                params={
                    "max_new_tokens": 500,
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "top_k": 50,
                }
            )
        except Exception as e:
            print(f"Warning: Failed to initialize watsonx.ai LLM: {e}")
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
        if self.llm:
            try:
                return await self._llm_parse_query(query)
            except Exception as e:
                print(f"LLM parsing failed: {e}, falling back to deterministic parser")
        
        # Fallback to deterministic parser
        return self._deterministic_fallback(query)
    
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
        if self.llm:
            try:
                return await self._llm_generate_explanation(event, score)
            except Exception as e:
                print(f"LLM explanation generation failed: {e}, using template")
        
        # Fallback to template-based explanation
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