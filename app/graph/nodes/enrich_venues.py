"""
Enrich Venues Node - Enriches events with venue context data.
"""
from app.graph.state import PulseGraphState
from app.config.settings import settings
from app.integrations.geoapify_client import GeoapifyClient
from app.models.venue import VenueContext, NearbyPlace
from typing import Optional
import asyncio
import time


async def enrich_venues_node(state: PulseGraphState) -> PulseGraphState:
    """
    Enrich events with venue context using Geoapify API.
    
    For each event, fetches:
    - Nearby points of interest
    - Transit accessibility
    - Parking information
    - Neighborhood context
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with enriched venue data
    """
    enriched = []
    client = GeoapifyClient()
    errors = list(state.get("errors", []))
    started = time.perf_counter()
    events = state.get("events_normalized", [])
    limit = settings.context_enrichment_limit
    enriched = [{"event": event_data, "venue_context": None} for event_data in events]

    candidates = [
        (idx, event_data)
        for idx, event_data in enumerate(events[:limit])
        if (
            not settings.demo_mode
            and event_data.get("latitude")
            and event_data.get("longitude")
        )
    ]

    tasks = [_get_venue_context(client=client, event=event_data) for _, event_data in candidates]
    results = await asyncio.gather(*tasks, return_exceptions=True) if tasks else []

    for (idx, event_data), result in zip(candidates, results):
        if isinstance(result, Exception):
            errors.append({
                "node": "enrich_venues",
                "event_id": event_data.get("id"),
                "error": str(result),
            })
        else:
            enriched[idx]["venue_context"] = result
    
    return {
        **state,
        "enriched_events": enriched,
        "errors": errors,
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "enrich_venues",
                "status": "completed",
                "tool_called": "geoapify",
                "events_enriched": len([e for e in enriched if e.get("venue_context")]),
                "events_considered": len(candidates),
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        ]
    }


async def _get_venue_context(
    client: GeoapifyClient,
    event: dict
) -> Optional[dict]:
    """
    Get venue context for an event using Geoapify.
    
    Args:
        client: GeoapifyClient instance
        event: Event data dictionary
        
    Returns:
        VenueContext dictionary or None
    """
    try:
        lat = event["latitude"]
        lon = event["longitude"]
        
        # Get nearby places (restaurants, transport, entertainment)
        places_raw = await client.get_nearby_places(
            lat=lat,
            lon=lon,
            radius=1000,
            categories="catering.restaurant,entertainment,public_transport.station",
            limit=10
        )
        
        # Parse nearby places
        nearby_places = []
        for place_feature in places_raw:
            properties = place_feature.get("properties", {})
            geometry = place_feature.get("geometry", {})
            
            # Calculate distance if coordinates available
            distance = None
            if geometry.get("coordinates"):
                place_coords = geometry["coordinates"]
                # Simple distance calculation (not precise but good enough)
                distance = int(
                    ((place_coords[0] - lon) ** 2 + (place_coords[1] - lat) ** 2) ** 0.5 * 111000
                )
            
            nearby_place = NearbyPlace(
                name=properties.get("name", "Unknown"),
                category=properties.get("categories", ["unknown"])[0] if properties.get("categories") else "unknown",
                distance_meters=distance,
                address=properties.get("formatted", None)
            )
            nearby_places.append(nearby_place)
        
        # Create venue context
        venue_context = VenueContext(
            venue_name=event.get("venue_name"),
            city=event.get("venue_city"),
            country=event.get("venue_country"),
            latitude=lat,
            longitude=lon,
            nearby_places=nearby_places,
            area_summary=_generate_area_summary(nearby_places),
            transport_context=_generate_transport_context(nearby_places)
        )
        
        return venue_context.model_dump()
        
    except Exception as e:
        # Return None if enrichment fails
        return None


def _generate_area_summary(nearby_places: list[NearbyPlace]) -> Optional[str]:
    """Generate a brief summary of the area around the venue."""
    if not nearby_places:
        return None
    
    categories = {}
    for place in nearby_places:
        cat = place.category.split(".")[0] if "." in place.category else place.category
        categories[cat] = categories.get(cat, 0) + 1
    
    if not categories:
        return None
    
    # Create summary
    parts = []
    if categories.get("catering", 0) > 0:
        parts.append(f"{categories['catering']} dining options")
    if categories.get("entertainment", 0) > 0:
        parts.append(f"{categories['entertainment']} entertainment venues")
    if categories.get("public_transport", 0) > 0:
        parts.append("public transport nearby")
    
    if parts:
        return "Area features: " + ", ".join(parts)
    
    return None


def _generate_transport_context(nearby_places: list[NearbyPlace]) -> Optional[str]:
    """Generate transport accessibility context."""
    transport_places = [
        p for p in nearby_places
        if "transport" in p.category.lower() or "station" in p.category.lower()
    ]
    
    if not transport_places:
        return None
    
    closest = min(transport_places, key=lambda p: p.distance_meters or 9999)
    
    if closest.distance_meters and closest.distance_meters < 500:
        return f"Excellent transport access - {closest.name} within 500m"
    elif closest.distance_meters and closest.distance_meters < 1000:
        return f"Good transport access - {closest.name} nearby"
    else:
        return "Public transport available in the area"


# Made with Bob
