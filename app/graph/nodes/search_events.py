"""
Search Events Node - Searches for events using Ticketmaster API or demo data.
"""
from datetime import datetime
from app.graph.state import PulseGraphState
from app.integrations.ticketmaster_client import TicketmasterClient
from app.services.demo_provider import DemoProvider
from app.config.settings import settings


async def search_events_node(state: PulseGraphState) -> PulseGraphState:
    """
    Search for events using Ticketmaster API or demo data.
    
    Falls back to demo provider if:
    - Demo mode is enabled
    - Ticketmaster API key is not configured
    - Ticketmaster API call fails
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with events_raw
    """
    fallback_used = False
    provider = "ticketmaster"
    error_message = None
    
    # Check if demo mode or no API key
    if state.get("demo_mode") or not settings.ticketmaster_api_key:
        fallback_used = True
        provider = "demo"
        events_raw = await _search_demo_events(state)
    else:
        # Try Ticketmaster API
        try:
            events_raw = await _search_ticketmaster_events(state)
        except Exception as e:
            # Fallback to demo on error
            error_message = str(e)
            fallback_used = True
            provider = "demo"
            events_raw = await _search_demo_events(state)
            
            # Add error to state
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append({
                "node": "search_events",
                "error": error_message
            })
    
    state["events_raw"] = events_raw
    state["fallback_used"] = fallback_used
    
    # Add to workflow trace
    trace_entry = {
        "node_name": "search_events",
        "status": "completed",
        "tool_called": "pulse_search_events",
        "provider": provider,
        "fallback_used": fallback_used,
        "events_count": len(events_raw)
    }
    
    if error_message:
        trace_entry["error_message"] = error_message
    
    state["workflow_trace"] = [
        *state.get("workflow_trace", []),
        trace_entry
    ]
    
    return state


async def _search_ticketmaster_events(state: PulseGraphState) -> list[dict]:
    """Search events using Ticketmaster API."""
    client = TicketmasterClient()
    
    # Convert date strings back to date objects if present
    date_from = None
    date_to = None
    
    if state.get("date_from"):
        date_from = datetime.fromisoformat(state["date_from"]).date()
    if state.get("date_to"):
        date_to = datetime.fromisoformat(state["date_to"]).date()
    
    events = await client.search_events(
        city=state.get("city"),
        country=state.get("country"),
        category=state.get("category"),
        keyword=state.get("keyword"),
        date_from=date_from,
        date_to=date_to,
        size=10
    )
    
    return events


async def _search_demo_events(state: PulseGraphState) -> list[dict]:
    """Search events using demo provider."""
    demo_provider = DemoProvider()
    
    # Convert date strings back to date objects if present
    date_from = None
    date_to = None
    
    if state.get("date_from"):
        date_from = datetime.fromisoformat(state["date_from"]).date()
    if state.get("date_to"):
        date_to = datetime.fromisoformat(state["date_to"]).date()
    
    events = demo_provider.search_events(
        city=state.get("city"),
        category=state.get("category"),
        date_from=date_from,
        date_to=date_to,
        budget_max=state.get("budget_max")
    )
    
    # Convert Event objects to dicts
    return [event.model_dump() for event in events]

# Made with Bob
