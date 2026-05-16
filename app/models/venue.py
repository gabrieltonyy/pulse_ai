"""Venue-related Pydantic models for Pulse AI."""
from pydantic import BaseModel
from typing import Optional


class NearbyPlace(BaseModel):
    """Represents a nearby place of interest."""
    
    name: str
    category: str
    distance_meters: Optional[int] = None
    address: Optional[str] = None


class VenueContext(BaseModel):
    """Context information about a venue and its surroundings."""
    
    venue_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nearby_places: list[NearbyPlace] = []
    area_summary: Optional[str] = None
    transport_context: Optional[str] = None


# Made with Bob