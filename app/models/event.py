"""Event-related Pydantic models for Pulse AI."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Event(BaseModel):
    """Normalized event object used across the app."""
    
    id: str
    provider_event_id: str
    provider: str

    title: str
    description: Optional[str] = None
    category: Optional[str] = None

    venue_name: Optional[str] = None
    venue_city: Optional[str] = None
    venue_country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: str = "USD"

    provider_event_url: Optional[str] = None
    image_url: Optional[str] = None

    popularity_score: Optional[float] = None
    source_payload_ref: Optional[str] = None


class EventCardViewModel(BaseModel):
    """View model used by Jinja2 templates for event cards."""
    
    id: str
    title: str
    date_label: str
    venue_label: str
    price_label: str
    image_url: Optional[str]
    provider: str
    recommendation_label: str
    explanation: str
    ticket_url: str
    calendar_url: str
    save_url: str


# Made with Bob