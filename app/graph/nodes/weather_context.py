"""
Weather Context Node - Adds weather context to events.
"""
import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Literal

from app.config.settings import settings
from app.db.database import get_session_context
from app.db.repositories import ApiCacheRepository
from app.graph.state import PulseGraphState
from app.integrations.openweather_client import OpenWeatherClient
from app.models.weather import WeatherContext


logger = logging.getLogger(__name__)


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
    enriched = [
        {**enriched_event, "weather_context": None}
        for enriched_event in state.get("enriched_events", [])
    ]
    errors = list(state.get("errors", []))
    weather_added_count = 0
    cache_hits = 0
    started = time.perf_counter()

    candidates = [
        (idx, enriched_event["event"])
        for idx, enriched_event in enumerate(enriched[:settings.context_enrichment_limit])
        if not settings.demo_mode and _should_add_weather(enriched_event["event"])
    ]
    tasks = [_get_weather_context(client=client, event=event) for _, event in candidates]
    results = await asyncio.gather(*tasks, return_exceptions=True) if tasks else []

    for (idx, event), result in zip(candidates, results):
        if isinstance(result, Exception):
            errors.append({
                "node": "weather_context",
                "event_id": event.get("id"),
                "error": str(result),
            })
        elif result and result["weather_context"]:
            enriched[idx]["weather_context"] = result["weather_context"]
            weather_added_count += 1
            if result["cache_hit"]:
                cache_hits += 1
    
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
                "weather_added": weather_added_count,
                "events_considered": len(candidates),
                "cache_hits": cache_hits,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
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
    
    if _event_date_outside_forecast_horizon(event):
        return False

    # Check if likely outdoor event. Generic music/concerts are often indoor, so only
    # enrich when outdoor intent is explicit.
    text = f"{event.get('title', '')} {event.get('description', '')} {event.get('category', '')}".lower()
    outdoor_terms = ["outdoor", "open air", "festival", "park", "stadium", "football", "soccer", "fair"]
    return any(term in text for term in outdoor_terms)


def _event_date_outside_forecast_horizon(event: dict) -> bool:
    try:
        event_datetime = event["start_datetime"]
        if isinstance(event_datetime, str):
            event_datetime = datetime.fromisoformat(event_datetime.replace("Z", "+00:00"))
        days_ahead = (event_datetime.date() - datetime.now().date()).days
        return days_ahead < 0 or days_ahead > settings.weather_forecast_horizon_days
    except Exception:
        return True


async def _get_weather_context(
    client: OpenWeatherClient,
    event: dict
) -> dict[str, Any]:
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
        
        cache_key, request_hash = _build_weather_cache_key(lat=lat, lon=lon, event_date=event_date)
        weather_data = await _get_cached_weather(cache_key)
        cache_hit = weather_data is not None

        if cache_hit:
            logger.info(
                "OpenWeather cache hit",
                extra={"provider": "openweather", "cache_hit": cache_hit},
            )
        else:
            logger.info(
                "OpenWeather cache miss",
                extra={"provider": "openweather", "cache_hit": cache_hit},
            )
            # Get weather data
            weather_data = await client.get_weather(
                lat=lat,
                lon=lon,
                event_date=event_date
            )
        
        if not weather_data:
            return {"weather_context": None, "cache_hit": cache_hit}

        if not cache_hit:
            await _cache_weather(
                cache_key=cache_key,
                request_hash=request_hash,
                weather_data=weather_data,
            )
        
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
        
        return {"weather_context": weather_context.model_dump(), "cache_hit": cache_hit}
        
    except Exception:
        return {"weather_context": None, "cache_hit": False}


def _build_weather_cache_key(lat: float, lon: float, event_date) -> tuple[str, str]:
    """Build a stable cache key from location and event date rounded to day."""
    payload = {
        "lat": lat,
        "lon": lon,
        "date": event_date.isoformat() if event_date else None,
    }
    request_hash = _hash_cache_payload(payload)
    return f"openweather:weather:{request_hash}", request_hash


def _hash_cache_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


async def _get_cached_weather(cache_key: str) -> dict[str, Any] | None:
    try:
        async with get_session_context() as session:
            cache = await ApiCacheRepository(session).get_cache(cache_key)
            if not cache:
                return None
            return json.loads(cache.response_json)
    except Exception:
        return None


async def _cache_weather(
    cache_key: str,
    request_hash: str,
    weather_data: dict[str, Any],
) -> None:
    try:
        async with get_session_context() as session:
            await ApiCacheRepository(session).set_cache(
                cache_key=cache_key,
                tool_name="openweather",
                provider="openweather",
                request_hash=request_hash,
                response_json=json.dumps(weather_data, default=str),
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.cache_ttl_weather),
            )
    except Exception:
        pass


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
