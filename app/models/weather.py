"""Weather-related Pydantic models for Pulse AI."""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class WeatherContext(BaseModel):
    """Weather context information for an event."""
    
    temperature_celsius: Optional[float] = None
    condition: Optional[str] = None
    rain_probability: Optional[float] = None
    outdoor_suitability: Optional[Literal["good", "moderate", "poor", "unknown"]] = None
    weather_note: Optional[str] = None


# Made with Bob