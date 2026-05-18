"""
Generate Explanations Node - Generates natural language explanations for recommendations.
"""
from app.graph.state import PulseGraphState
from app.config.settings import settings
from app.services.llm_service import LLMService
from app.models.event import Event
from app.models.recommendation import RecommendationScore
import time


async def generate_explanations_node(state: PulseGraphState) -> PulseGraphState:
    """
    Generate natural language explanations for event recommendations.
    
    Uses LLM to create:
    - Overall recommendation summary
    - Individual event explanations
    - Reasoning for rankings
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with recommendation_summary
    """
    llm_service = LLMService()
    errors = list(state.get("errors", []))
    explanations_generated = 0
    started = time.perf_counter()
    
    for ranked_event in state.get("ranked_events", []):
        event_data = ranked_event["event"]
        score_data = ranked_event["recommendation"]
        
        try:
            # Convert to Pydantic models for type safety
            event = Event(**event_data)
            score = RecommendationScore(**score_data)
            
            # Generate explanation using LLM
            explanation = await llm_service.generate_explanation(event, score)
            ranked_event["recommendation"]["explanation"] = explanation
            explanations_generated += 1
            
        except Exception as e:
            # Fallback to template-based explanation
            explanation = _generate_fallback_explanation(
                event_data=event_data,
                score_data=score_data,
                state=state
            )
            ranked_event["recommendation"]["explanation"] = explanation
            errors.append({
                "node": "generate_explanations",
                "event_id": event_data.get("id"),
                "error": str(e)
            })
    
    return {
        **state,
        "errors": errors,
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "generate_explanations",
                "status": "completed",
                "tool_called": "template",
                "explanations_generated": explanations_generated,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        ]
    }


def _generate_fallback_explanation(
    event_data: dict,
    score_data: dict,
    state: PulseGraphState
) -> str:
    """
    Generate a simple template-based explanation as fallback.
    
    Args:
        event_data: Event dictionary
        score_data: Recommendation score dictionary
        state: Current workflow state
        
    Returns:
        Explanation string
    """
    reasons = []
    
    # Check relevance
    if score_data.get("relevance_score", 0) > 70:
        category = state.get("category", "event")
        reasons.append(f"matches your {category} preference")
    
    # Check affordability
    if score_data.get("affordability_score", 0) > 80:
        reasons.append("fits your budget")
    
    # Check date match
    if score_data.get("date_match_score", 0) > 80:
        reasons.append("happens during your selected dates")
    
    # Check venue context
    if score_data.get("context_score", 0) > 70:
        reasons.append("has great venue location")
    
    # Check weather
    if score_data.get("weather_score", 0) > 80:
        reasons.append("has favorable weather")
    
    # Build explanation
    if reasons:
        explanation = "Recommended because it " + ", ".join(reasons[:3]) + "."
    else:
        explanation = f"This event matches your search criteria. Score: {score_data.get('total_score', 0):.0f}/100."
    
    return explanation


# Made with Bob
