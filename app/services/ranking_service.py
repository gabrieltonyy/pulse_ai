"""
Ranking Service for Pulse AI.
Implements deterministic scoring algorithm for event recommendations.
"""
from app.models.recommendation import RecommendationScore
from app.models.search import SearchIntent
from datetime import datetime, date
from typing import Optional
import re


class RankingService:
    """Service for ranking and scoring events using deterministic algorithm."""
    
    def rank_events(
        self,
        enriched_events: list[dict],
        intent: SearchIntent
    ) -> list[dict]:
        """
        Rank events using deterministic scoring algorithm.
        
        Args:
            enriched_events: List of events with venue and weather context
            intent: User's search intent
            
        Returns:
            List of ranked events sorted by total score (descending)
        """
        scored_events = []
        
        for enriched_event in enriched_events:
            event = enriched_event["event"]
            venue_context = enriched_event.get("venue_context")
            weather_context = enriched_event.get("weather_context")
            
            # Calculate individual scores
            relevance = self._calculate_relevance_score(event, intent)
            date_match = self._calculate_date_match_score(event, intent)
            affordability = self._calculate_affordability_score(event, intent)
            popularity = self._calculate_popularity_score(event)
            context = self._calculate_context_score(venue_context)
            weather = self._calculate_weather_score(weather_context, event)
            
            # Calculate total score with weights (per docs/10-ranking-and-recommendation-logic.md)
            total = (
                relevance * 0.30 +
                date_match * 0.20 +
                affordability * 0.20 +
                popularity * 0.15 +
                context * 0.10 +
                weather * 0.05
            )
            
            # Create recommendation score (label will be assigned after sorting)
            score = RecommendationScore(
                event_id=event["id"],
                total_score=round(total, 2),
                relevance_score=round(relevance, 2),
                date_match_score=round(date_match, 2),
                affordability_score=round(affordability, 2),
                popularity_score=round(popularity, 2),
                context_score=round(context, 2),
                weather_score=round(weather, 2),
                label="Best Overall",  # Temporary, will be reassigned
                explanation=""  # Will be generated later
            )
            
            scored_events.append({
                "event": event,
                "recommendation": score.model_dump(),
                "venue_context": venue_context,
                "weather_context": weather_context
            })
        
        # Sort by total score descending
        scored_events.sort(key=lambda x: x["recommendation"]["total_score"], reverse=True)
        
        # Assign labels
        self._assign_labels(scored_events)
        
        return scored_events
    
    def _calculate_relevance_score(self, event: dict, intent: SearchIntent) -> float:
        """
        Calculate how well event matches user intent.
        
        Scoring:
        - Exact category match: 50 points
        - Keyword in title/description: 30 points
        - Preferences match: up to 20 points
        """
        score = 0.0
        
        # Category match
        if intent.category and event.get("category"):
            event_category = event["category"].lower()
            intent_category = intent.category.lower()
            
            if intent_category in event_category or event_category in intent_category:
                score += 50
        
        # Keyword match in title/description
        if intent.keyword:
            text = f"{event.get('title', '')} {event.get('description', '')}".lower()
            keyword_lower = intent.keyword.lower()
            
            if keyword_lower in text:
                # Boost if in title
                if keyword_lower in event.get('title', '').lower():
                    score += 35
                else:
                    score += 30
        
        # Preferences match
        if intent.preferences:
            text = f"{event.get('title', '')} {event.get('description', '')}".lower()
            matches = sum(1 for pref in intent.preferences if pref.lower() in text)
            score += min(matches * 10, 20)
        
        return min(score, 100.0)
    
    def _calculate_date_match_score(self, event: dict, intent: SearchIntent) -> float:
        """
        Calculate how well event date matches requested range.
        
        Scoring:
        - Inside requested range: 100
        - Within 1 day: 75
        - Within 3 days: 50
        - Same month: 30
        - No valid date: 10
        """
        if not event.get("start_datetime"):
            return 10.0
        
        try:
            # Parse event date
            event_datetime = event["start_datetime"]
            if isinstance(event_datetime, str):
                event_datetime = datetime.fromisoformat(event_datetime.replace("Z", "+00:00"))
            event_date = event_datetime.date()
            
            # If user provided date range
            if intent.date_from and intent.date_to:
                date_from = intent.date_from if isinstance(intent.date_from, date) else datetime.fromisoformat(str(intent.date_from)).date()
                date_to = intent.date_to if isinstance(intent.date_to, date) else datetime.fromisoformat(str(intent.date_to)).date()
                
                # Inside range
                if date_from <= event_date <= date_to:
                    return 100.0
                
                # Within 1 day
                days_from_start = abs((event_date - date_from).days)
                days_from_end = abs((event_date - date_to).days)
                min_days = min(days_from_start, days_from_end)
                
                if min_days <= 1:
                    return 75.0
                elif min_days <= 3:
                    return 50.0
                elif event_date.month == date_from.month or event_date.month == date_to.month:
                    return 30.0
                else:
                    return 10.0
            else:
                # No date range specified - prefer upcoming events
                today = date.today()
                days_away = (event_date - today).days
                
                if 0 <= days_away <= 7:
                    return 90.0
                elif 8 <= days_away <= 30:
                    return 70.0
                else:
                    return 50.0
        except Exception:
            return 10.0
    
    def _calculate_affordability_score(self, event: dict, intent: SearchIntent) -> float:
        """
        Calculate affordability based on budget.
        
        Scoring:
        - Free event: 100
        - Price max <= budget: 100
        - Price min <= budget: 75
        - Up to 20% above budget: 55
        - More than 20% above: 20
        - Price unknown: 60
        """
        price_min = event.get("price_min")
        price_max = event.get("price_max")
        
        # Free event
        if price_min == 0 or (price_min is None and price_max == 0):
            return 100.0
        
        # No price info
        if price_min is None and price_max is None:
            return 60.0
        
        # No budget specified
        if not intent.budget_max:
            return 70.0
        
        budget = intent.budget_max
        
        # Price max within budget
        if price_max and price_max <= budget:
            return 100.0
        
        # Price min within budget
        if price_min and price_min <= budget:
            return 75.0
        
        # Up to 20% above budget
        if price_min and price_min <= budget * 1.2:
            return 55.0
        
        # More than 20% above budget
        return 20.0
    
    def _calculate_popularity_score(self, event: dict) -> float:
        """
        Calculate popularity based on event metadata quality.
        
        Scoring:
        - Base score: 50
        - Has image: +20
        - Has description: +15
        - Has venue: +15
        """
        score = 50.0  # Base score
        
        # Has image
        if event.get("image_url"):
            score += 20
        
        # Has description
        if event.get("description"):
            score += 15
        
        # Has venue
        if event.get("venue_name"):
            score += 15
        
        return min(score, 100.0)
    
    def _calculate_context_score(self, venue_context: Optional[dict]) -> float:
        """
        Calculate score based on venue context richness.
        
        Scoring:
        - 5+ nearby places: 90
        - 3-4 nearby places: 70
        - 1-2 nearby places: 50
        - No context: 30
        """
        if not venue_context:
            return 30.0
        
        nearby_places = venue_context.get("nearby_places", [])
        place_count = len(nearby_places)
        
        if place_count >= 5:
            return 90.0
        elif place_count >= 3:
            return 70.0
        elif place_count >= 1:
            return 50.0
        else:
            return 30.0
    
    def _calculate_weather_score(self, weather_context: Optional[dict], event: dict) -> float:
        """
        Calculate score based on weather suitability.
        
        Scoring:
        - Good weather: 100
        - Moderate weather: 60
        - Poor weather: 25
        - Indoor event: 70
        - Unknown: 50
        """
        # If clearly indoor event
        category = event.get("category", "").lower()
        indoor_categories = ["theater", "museum", "exhibition", "conference", "comedy"]
        if any(cat in category for cat in indoor_categories):
            return 70.0
        
        if not weather_context:
            return 50.0
        
        suitability = weather_context.get("outdoor_suitability", "unknown")
        
        if suitability == "good":
            return 100.0
        elif suitability == "moderate":
            return 60.0
        elif suitability == "poor":
            return 25.0
        else:
            return 50.0
    
    def _assign_labels(self, scored_events: list[dict]) -> None:
        """
        Assign recommendation labels to events.
        
        Labels:
        - Best Overall: Highest total score
        - Best Budget Pick: Best affordability + decent relevance
        - Trending Option: High popularity
        - Closest Match: Highest relevance
        """
        if not scored_events:
            return
        
        # Track which events have been labeled
        labeled_ids = set()
        
        # Best Overall - highest total score
        scored_events[0]["recommendation"]["label"] = "Best Overall"
        labeled_ids.add(scored_events[0]["event"]["id"])
        
        # Find best budget pick (high affordability, decent relevance)
        budget_candidates = [
            e for e in scored_events
            if e["event"]["id"] not in labeled_ids
            and e["recommendation"]["affordability_score"] >= 75
            and e["recommendation"]["relevance_score"] >= 50
        ]
        if budget_candidates and len(scored_events) > 1:
            # Pick the one with highest affordability
            budget_candidates.sort(key=lambda x: x["recommendation"]["affordability_score"], reverse=True)
            budget_candidates[0]["recommendation"]["label"] = "Best Budget Pick"
            labeled_ids.add(budget_candidates[0]["event"]["id"])
        
        # Find trending option (high popularity)
        if len(scored_events) > 2:
            popularity_candidates = [
                e for e in scored_events
                if e["event"]["id"] not in labeled_ids
                and e["recommendation"]["popularity_score"] >= 70
            ]
            if popularity_candidates:
                popularity_candidates.sort(key=lambda x: x["recommendation"]["popularity_score"], reverse=True)
                popularity_candidates[0]["recommendation"]["label"] = "Trending Option"
                labeled_ids.add(popularity_candidates[0]["event"]["id"])
        
        # Find closest match (high relevance)
        if len(scored_events) > 3:
            relevance_candidates = [
                e for e in scored_events
                if e["event"]["id"] not in labeled_ids
                and e["recommendation"]["relevance_score"] >= 70
            ]
            if relevance_candidates:
                relevance_candidates.sort(key=lambda x: x["recommendation"]["relevance_score"], reverse=True)
                relevance_candidates[0]["recommendation"]["label"] = "Closest Match"
                labeled_ids.add(relevance_candidates[0]["event"]["id"])


# Made with Bob