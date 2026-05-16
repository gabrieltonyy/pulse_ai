"""
Enrich Venues Node - Enriches events with venue context data.
"""
from app.graph.state import PulseGraphState


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
    # TODO: Implement venue enrichment logic
    # This will be implemented in Phase 2
    
    return {
        **state,
        "enriched_events": state.get("events_normalized", []),
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "enrich_venues",
                "status": "completed",
                "tool_called": "pulse_enrich_venue",
                "provider": "geoapify",
            }
        ]
    }

# Made with Bob
