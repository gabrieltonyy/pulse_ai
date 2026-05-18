"""MCP tool for enriching venue information via Geoapify."""
from __future__ import annotations

from app.config.settings import settings
from app.integrations.geoapify_client import GeoapifyClient

# Default categories covering the most relevant POIs near an event venue
_DEFAULT_CATEGORIES = [
    "catering.restaurant",
    "entertainment",
    "public_transport",
    "parking",
]


async def pulse_enrich_venue(
    latitude: float,
    longitude: float,
    radius: int = 1000,
) -> dict:
    """
    Get nearby places and contextual information for a venue location.

    Args:
        latitude:  Venue latitude (decimal degrees).
        longitude: Venue longitude (decimal degrees).
        radius:    Search radius in metres (default 1 000 m).

    Returns:
        Dictionary with:
        - nearby_places (list)  – places returned by Geoapify
        - area_summary (str)    – short human-readable area description
        - transport_info (str)  – nearest public-transport options
        - categories_found (list[str]) – categories that had results
    """
    if settings.demo_mode:
        return {
            "nearby_places": [],
            "area_summary": "Demo mode: live venue enrichment skipped.",
            "transport_info": None,
            "categories_found": [],
        }

    client = GeoapifyClient()

    try:
        venue_context = await client.get_nearby_places(
            lat=latitude,
            lon=longitude,
            radius=radius,
            categories=_DEFAULT_CATEGORIES,
        )
    except Exception as exc:  # noqa: BLE001
        return {"nearby_places": [], "error": str(exc)}

    return venue_context
