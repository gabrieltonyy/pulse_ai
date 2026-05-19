"""MCP tool for retrieving event weather forecasts via OpenWeather."""
from __future__ import annotations

from datetime import datetime
import logging

from app.config.settings import settings
from app.integrations.openweather_client import OpenWeatherClient

logger = logging.getLogger(__name__)


async def pulse_get_weather(
    latitude: float,
    longitude: float,
    date: str,
) -> dict:
    """
    Get a weather forecast for an event's location and date.

    Args:
        latitude:  Event latitude (decimal degrees).
        longitude: Event longitude (decimal degrees).
        date:      Event date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).

    Returns:
        Dictionary with:
        - temperature (float)        – degrees Celsius
        - condition (str)            – e.g. "Clear", "Rain"
        - description (str)          – e.g. "light rain"
        - humidity (int)             – percentage
        - wind_speed (float)         – m/s
        - rain_probability (float)   – 0-1
        - is_outdoor_friendly (bool) – True when conditions are favourable
        - weather_note (str)         – one-sentence advisory for the user
    """
    if settings.demo_mode:
        logger.info("Weather lookup skipped in demo mode")
        return {
            "success": True,
            "temperature": None,
            "condition": "unknown",
            "outdoor_suitability": "unknown",
            "weather_note": "Demo mode: live weather lookup skipped.",
        }

    client = OpenWeatherClient()

    try:
        event_date = datetime.fromisoformat(date).date()
        logger.info("Starting weather lookup", extra={"provider": "openweather"})
        weather = await client.get_weather(
            lat=latitude,
            lon=longitude,
            event_date=event_date,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Weather lookup failed",
            extra={"provider": "openweather", "error_type": type(exc).__name__},
        )
        return {
            "success": False,
            "error": str(exc),
            "temperature": None,
            "outdoor_suitability": "unknown",
        }

    return {"success": True, **weather}
