"""
Weather Context Node - Adds weather context to events.
"""
from app.graph.state import PulseGraphState
from app.integrations.openweather_client import OpenWeatherClient
from app.models.weather import WeatherContext
from datetime import datetime
from typing import Optional, Literal


async def weather_context_node(state: PulseGraphState) -> PulseGraphState:
    """
    Add weather context to events using OpenWeather API.
    
    For each event, fetches:
    - Temperature forecast
    - Weather conditions
    - Rain probability
    - Outdoor suitability assessment
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with weather context
    """
    client = OpenWeatherClient()
    enriched = state.get("enriched_events", [])
    errors = list(state.get("errors", []))
    weather_added_count = 0
    
    for enriched_event in enriched:
        event = enriched_event["event"]
        
        try:
            # Only add weather for outdoor events with coordinates and dates
            if _should_add_weather(event):
                weather_context = await _get_weather_context(
                    client=client,
                    event=event
                )
                
                if weather_context:
                    enriched_event["weather_context"] = weather_context
                    weather_added_count += 1
                else:
                    enriched_event["weather_context"] = None
            else:
                enriched_event["weather_context"] = None
                
        except Exception as e:
            # Continue without weather on error
            enriched_event["weather_context"] = None
            errors.append({
                "node": "weather_context",
                "event_id": event.get("id"),
                "error": str(e)
            })
    
    return {
        **state,
        "enriched_events": enriched,
        "errors": errors,
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "weather_context",
                "status": "completed",
                "tool_called": "openweather",
                "weather_added": weather_added_count
            }
        ]
    }


def _should_add_weather(event: dict) -> bool:
    """
    Determine if weather context should be added for an event.
    
    Weather is added for:
    - Outdoor events (Sports, Festival, Music)
    - Events with coordinates
    - Events with valid dates
    """
    # Must have coordinates
    if not event.get("latitude") or not event.get("longitude"):
        return False
    
    # Must have start date
    if not event.get("start_datetime"):
        return False
    
    # Check if likely outdoor event
    category = event.get("category", "").lower()
    outdoor_categories = ["sports", "festival", "music", "outdoor", "concert", "fair"]
    
    return any(cat in category for cat in outdoor_categories)


async def _get_weather_context(
    client: OpenWeatherClient,
    event: dict
) -> Optional[dict]:
    """
    Get weather context for an event.
    
    Args:
        client: OpenWeatherClient instance
        event: Event data dictionary
        
    Returns:
        WeatherContext dictionary or None
    """
    try:
        lat = event["latitude"]
        lon = event["longitude"]
        
        # Parse event date
        event_datetime = event["start_datetime"]
        if isinstance(event_datetime, str):
            event_datetime = datetime.fromisoformat(event_datetime.replace("Z", "+00:00"))
        event_date = event_datetime.date()
        
        # Get weather data
        weather_data = await client.get_weather(
            lat=lat,
            lon=lon,
            event_date=event_date
        )
        
        if not weather_data:
            return None
        
        # Extract weather information
        main_data = weather_data.get("main", {})
        weather_list = weather_data.get("weather", [])
        
        temperature = main_data.get("temp")
        condition = weather_list[0].get("main") if weather_list else None
        
        # Calculate rain probability (from clouds or weather condition)
        rain_prob = _calculate_rain_probability(weather_data)
        
        # Determine outdoor suitability
        suitability = _determine_outdoor_suitability(
            weather_data=weather_data,
            client=client
        )
        
        # Generate weather note
        weather_note = _generate_weather_note(
            temperature=temperature,
            condition=condition,
            suitability=suitability
        )
        
        # Create weather context
        weather_context = WeatherContext(
            temperature_celsius=temperature,
            condition=condition,
            rain_probability=rain_prob,
            outdoor_suitability=suitability,
            weather_note=weather_note
        )
        
        return weather_context.model_dump()
        
    except Exception as e:
        return None


def _calculate_rain_probability(weather_data: dict) -> Optional[float]:
    """Calculate rain probability from weather data."""
    # Check if rain data is available
    if "rain" in weather_data:
        rain_data = weather_data["rain"]
        if "3h" in rain_data and rain_data["3h"] > 0:
            return min(rain_data["3h"] / 10 * 100, 100)  # Convert to percentage
    
    # Check weather condition
    weather_list = weather_data.get("weather", [])
    if weather_list:
        main_condition = weather_list[0].get("main", "").lower()
        if main_condition in ["rain", "drizzle"]:
            return 80.0
        elif main_condition == "thunderstorm":
            return 90.0
    
    # Check clouds
    clouds_data = weather_data.get("clouds", {})
    cloud_coverage = clouds_data.get("all", 0)
    
    if cloud_coverage > 80:
        return 40.0
    elif cloud_coverage > 50:
        return 20.0
    
    return 10.0


def _determine_outdoor_suitability(
    weather_data: dict,
    client: OpenWeatherClient
) -> Literal["good", "moderate", "poor", "unknown"]:
    """
    Determine outdoor suitability rating.
    
    Returns: "good", "moderate", "poor", or "unknown"
    """
    if not weather_data:
        return "unknown"
    
    # Use client's built-in method
    is_friendly = client.is_outdoor_friendly(weather_data)
    
    if is_friendly:
        # Check if it's really good or just moderate
        weather_list = weather_data.get("weather", [])
        main_data = weather_data.get("main", {})
        temp = main_data.get("temp")
        
        if weather_list:
            condition = weather_list[0].get("main", "").lower()
            if condition in ["clear", "clouds"] and temp and 15 <= temp <= 28:
                return "good"
        
        return "moderate"
    else:
        return "poor"


def _generate_weather_note(
    temperature: Optional[float],
    condition: Optional[str],
    suitability: str
) -> Optional[str]:
    """Generate a human-readable weather note."""
    if not temperature or not condition:
        return None
    
    temp_str = f"{int(temperature)}°C"
    
    if suitability == "good":
        return f"Great weather expected - {temp_str}, {condition.lower()}"
    elif suitability == "moderate":
        return f"Fair weather - {temp_str}, {condition.lower()}"
    elif suitability == "poor":
        return f"Challenging weather - {temp_str}, {condition.lower()}"
    else:
        return f"Weather: {temp_str}, {condition.lower()}"


# Made with Bob
