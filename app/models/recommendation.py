"""Recommendation-related Pydantic models for Pulse AI."""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from app.models.event import Event
from app.models.venue import VenueContext
from app.models.weather import WeatherContext


class RecommendationScore(BaseModel):
    """Scoring breakdown for event recommendations."""
    
    event_id: str
    total_score: float

    relevance_score: float = 0
    date_match_score: float = 0
    affordability_score: float = 0
    popularity_score: float = 0
    context_score: float = 0
    weather_score: float = 0

    label: Literal[
        "Best Overall",
        "Best Budget Pick",
        "Trending Option",
        "Closest Match",
        "Premium Pick",
        "Great Venue",
        "Outdoor Friendly"
    ]
    explanation: str


class EnrichedEvent(BaseModel):
    """Event combined with location and weather context."""
    
    event: Event
    venue_context: Optional[VenueContext] = None
    weather_context: Optional[WeatherContext] = None


class RankedEvent(BaseModel):
    """Event with recommendation score and enrichment data."""
    
    event: Event
    recommendation: RecommendationScore
    venue_context: Optional[VenueContext] = None
    weather_context: Optional[WeatherContext] = None


# Made with Bob