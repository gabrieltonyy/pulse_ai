"""
Normalize Events Node - Normalizes raw event data to standard format.
"""
from app.graph.state import PulseGraphState


async def normalize_events_node(state: PulseGraphState) -> PulseGraphState:
    """
    Normalize raw event data from various providers to standard format.
    
    Transforms provider-specific event structures into our unified Event model.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with events_normalized
    """
    # TODO: Implement normalization logic
    # This will be implemented in Phase 2
    
    return {
        **state,
        "events_normalized": [],
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "normalize_events",
                "status": "completed",
                "tool_called": None,
            }
        ]
    }

# Made with Bob
