"""
Validate Query Node - Validates parsed search intent.
"""
from app.graph.state import PulseGraphState
from app.models.search import SearchValidationResult


async def validate_query_node(state: PulseGraphState) -> PulseGraphState:
    """
    Validate the parsed search intent.
    
    Checks:
    - Required fields are present (city or keyword)
    - Date ranges are valid
    - Budget constraints are reasonable
    - Location is specified
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with validation results
    """
    missing_fields = []
    
    # Check for minimum required information
    if not state.get("city") and not state.get("keyword"):
        missing_fields.append("city or keyword")
    
    # Check if we have at least some search criteria
    if not state.get("category") and not state.get("keyword") and not state.get("city"):
        missing_fields.append("search criteria (category, keyword, or city)")
    
    # Validate date range if provided
    date_from = state.get("date_from")
    date_to = state.get("date_to")
    
    if date_from and date_to:
        # Both are strings in ISO format, compare them
        if date_from > date_to:
            missing_fields.append("valid date range (from date must be before to date)")
    
    # Validate budget if provided
    budget_max = state.get("budget_max")
    if budget_max is not None and budget_max < 0:
        missing_fields.append("positive budget value")
    
    # Determine if query is valid
    is_valid = len(missing_fields) == 0
    
    # Create validation result
    validation = SearchValidationResult(
        is_valid=is_valid,
        missing_fields=missing_fields,
        message=f"Missing: {', '.join(missing_fields)}" if missing_fields else "Query is valid"
    )
    
    validation_result = validation.model_dump()

    return {
        **state,
        "validation": validation_result,
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "validate_query",
                "status": "completed" if is_valid else "failed",
                "tool_called": None,
                "validation_result": validation_result,
            },
        ],
    }

# Made with Bob
