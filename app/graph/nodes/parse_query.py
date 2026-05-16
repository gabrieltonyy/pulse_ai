"""
Parse Query Node - Extracts structured intent from user query.
"""
from app.graph.state import PulseGraphState


async def parse_query_node(state: PulseGraphState) -> PulseGraphState:
    """
    Parse the user's raw query and extract structured search intent.
    
    This node will use the LLM to understand the user's query and extract:
    - City/location
    - Event category
    - Date range
    - Budget constraints
    - Other preferences
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with parsed_intent
    """
    # TODO: Implement query parsing logic
    # This will be implemented in Phase 2
    
    return {
        **state,
        "parsed_intent": {},
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "parse_query",
                "status": "completed",
                "tool_called": None,
            }
        ]
    }

# Made with Bob
