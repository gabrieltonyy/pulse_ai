"""
Prepare Response Node - Prepares final response for the user.
"""
from app.graph.state import PulseGraphState


async def prepare_response_node(state: PulseGraphState) -> PulseGraphState:
    """
    Prepare the final response with all results.
    
    Formats:
    - Ranked events
    - Recommendation summary
    - Workflow trace
    - Error information if any
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state ready for response
    """
    ranked_events = state.get("ranked_events", [])
    
    # Create recommendation summary
    summary = _generate_recommendation_summary(state, ranked_events)
    
    return {
        **state,
        "recommendation_summary": summary,
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "prepare_response",
                "status": "completed",
                "events_returned": len(ranked_events)
            }
        ]
    }


def _generate_recommendation_summary(
    state: PulseGraphState,
    ranked_events: list[dict]
) -> str:
    """
    Generate a summary of the recommendations.
    
    Args:
        state: Current workflow state
        ranked_events: List of ranked events
        
    Returns:
        Summary string
    """
    if not ranked_events:
        return _generate_no_results_message(state)
    
    count = len(ranked_events)
    city = state.get("city", "your area")
    category = state.get("category", "events")
    
    # Start with basic summary
    summary = f"Found {count} {category} event{'s' if count != 1 else ''} in {city}. "
    
    # Add top recommendation info
    if count > 0:
        best = ranked_events[0]["recommendation"]
        total_score = best.get("total_score", 0)
        summary += f"Top recommendation has a {total_score:.0f}% match score. "
    
    # Highlight special picks
    labels = [e["recommendation"].get("label", "") for e in ranked_events]
    
    if "Best Budget Pick" in labels:
        summary += "Budget-friendly options available. "
    
    if "Trending Option" in labels:
        summary += "Popular events included. "
    
    if "Great Venue" in labels:
        summary += "Events with excellent venue locations. "
    
    # Add weather note if applicable
    weather_events = [
        e for e in ranked_events
        if e.get("weather_context") and e["weather_context"].get("outdoor_suitability") == "good"
    ]
    if weather_events:
        summary += f"{len(weather_events)} event{'s' if len(weather_events) != 1 else ''} with favorable weather. "
    
    return summary.strip()


def _generate_no_results_message(state: PulseGraphState) -> str:
    """
    Generate a helpful message when no events are found.
    
    Args:
        state: Current workflow state
        
    Returns:
        No results message
    """
    city = state.get("city")
    category = state.get("category")
    
    message = "No events found matching your criteria. "
    
    # Provide helpful suggestions
    suggestions = []
    
    if state.get("budget_max"):
        suggestions.append("try increasing your budget")
    
    if state.get("date_from") and state.get("date_to"):
        suggestions.append("expand your date range")
    
    if category:
        suggestions.append(f"try a different category instead of {category}")
    
    if city:
        suggestions.append(f"search in nearby cities around {city}")
    
    if suggestions:
        message += "Try: " + ", or ".join(suggestions) + "."
    else:
        message += "Try broadening your search criteria."
    
    return message


# Made with Bob
