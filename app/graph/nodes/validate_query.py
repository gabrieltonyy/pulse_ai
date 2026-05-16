"""
Validate Query Node - Validates parsed search intent.
"""
from app.graph.state import PulseGraphState


async def validate_query_node(state: PulseGraphState) -> PulseGraphState:
    """
    Validate the parsed search intent.
    
    Checks:
    - Required fields are present
    - Date ranges are valid
    - Budget constraints are reasonable
    - Location is valid
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with validation results
    """
    # TODO: Implement validation logic
    # This will be implemented in Phase 2
    
    return {
        **state,
        "validation": {"is_valid": True},
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "validate_query",
                "status": "completed",
                "tool_called": None,
            }
        ]
    }

# Made with Bob
