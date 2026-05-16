"""
Normalize Events Node - Normalizes raw event data to standard format.
"""
from app.graph.state import PulseGraphState
from app.models.event import Event


async def normalize_events_node(state: PulseGraphState) -> PulseGraphState:
    """
    Normalize raw event data from various providers to standard format.
    
    Transforms provider-specific event structures (Ticketmaster or demo)
    into our unified Event model.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with events_normalized
    """
    normalized = []
    errors = []
    
    for raw_event in state.get("events_raw", []):
        try:
            # Check if already normalized (from demo provider)
            if "provider" in raw_event and raw_event["provider"] == "demo":
                # Already in Event format
                event = Event(**raw_event)
                normalized.append(event.model_dump())
            else:
                # Normalize Ticketmaster response
                event = _normalize_ticketmaster_event(raw_event)
                normalized.append(event.model_dump())
                
        except Exception as e:
            errors.append({
                "event_id": raw_event.get("id", "unknown"),
                "error": str(e)
            })
    
    state["events_normalized"] = normalized
    
    # Add errors to state if any
    if errors:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].extend([{"node": "normalize_events", **err} for err in errors])
    
    # Add to workflow trace
    state["workflow_trace"] = [
        *state.get("workflow_trace", []),
        {
            "node_name": "normalize_events",
            "status": "completed",
            "tool_called": None,
            "normalized_count": len(normalized),
            "error_count": len(errors)
        }
    ]
    
    return state


def _normalize_ticketmaster_event(raw_event: dict) -> Event:
    """
    Normalize a Ticketmaster event to our Event model.
    
    Args:
        raw_event: Raw event data from Ticketmaster API
        
    Returns:
        Normalized Event object
    """
    # Extract venue information
    venues = raw_event.get("_embedded", {}).get("venues", [{}])
    venue = venues[0] if venues else {}
    
    # Extract location
    location = venue.get("location", {})
    latitude = float(location.get("latitude", 0)) if location.get("latitude") else None
    longitude = float(location.get("longitude", 0)) if location.get("longitude") else None
    
    # Extract price range
    price_ranges = raw_event.get("priceRanges", [{}])
    price_range = price_ranges[0] if price_ranges else {}
    
    # Extract classification (category)
    classifications = raw_event.get("classifications", [{}])
    classification = classifications[0] if classifications else {}
    segment = classification.get("segment", {})
    category = segment.get("name", "").lower() if segment else None
    
    # Extract images
    images = raw_event.get("images", [{}])
    image = images[0] if images else {}
    
    # Extract dates
    dates = raw_event.get("dates", {})
    start = dates.get("start", {})
    start_datetime = start.get("dateTime")
    
    return Event(
        id=raw_event.get("id"),
        provider_event_id=raw_event.get("id"),
        provider="ticketmaster",
        title=raw_event.get("name", "Untitled Event"),
        description=raw_event.get("info") or raw_event.get("pleaseNote"),
        category=category,
        venue_name=venue.get("name"),
        venue_city=venue.get("city", {}).get("name"),
        venue_country=venue.get("country", {}).get("name"),
        latitude=latitude,
        longitude=longitude,
        start_datetime=start_datetime,
        price_min=price_range.get("min"),
        price_max=price_range.get("max"),
        currency=price_range.get("currency", "USD"),
        provider_event_url=raw_event.get("url"),
        image_url=image.get("url")
    )

# Made with Bob
