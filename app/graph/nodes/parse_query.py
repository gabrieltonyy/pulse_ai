"""
Parse Query Node - Extracts structured intent from user query using watsonx.ai LLM.
"""
from app.graph.state import PulseGraphState
from app.services.llm_service import LLMService


async def parse_query_node(state: PulseGraphState) -> PulseGraphState:
    """
    Parse the user's raw query and extract structured search intent using watsonx.ai.
    Falls back to deterministic parsing if LLM fails.
    
    This node uses the LLM to understand the user's query and extract:
    - City/location
    - Event category
    - Date range
    - Budget constraints
    - Other preferences
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with parsed_intent and extracted fields
    """
    llm_service = LLMService()
    fallback_used = False
    error_message = None
    
    try:
        # Use LLM to parse query
        intent = await llm_service.parse_query(state["raw_query"])
        
        # Update state with parsed intent
        state["parsed_intent"] = intent.model_dump()
        state["city"] = intent.city
        state["country"] = intent.country
        state["category"] = intent.category
        state["keyword"] = intent.keyword
        state["date_from"] = intent.date_from.isoformat() if intent.date_from else None
        state["date_to"] = intent.date_to.isoformat() if intent.date_to else None
        state["budget_max"] = intent.budget_max
        state["currency"] = intent.currency
        state["preferences"] = intent.preferences
        
    except Exception as e:
        # Fallback already handled in LLMService, but catch any unexpected errors
        error_message = str(e)
        fallback_used = True
        
        # Use deterministic fallback
        intent = llm_service._deterministic_fallback(state["raw_query"])
        state["parsed_intent"] = intent.model_dump()
        state["city"] = intent.city
        state["country"] = intent.country
        state["category"] = intent.category
        state["keyword"] = intent.keyword
        state["date_from"] = intent.date_from.isoformat() if intent.date_from else None
        state["date_to"] = intent.date_to.isoformat() if intent.date_to else None
        state["budget_max"] = intent.budget_max
        state["currency"] = intent.currency
        state["preferences"] = intent.preferences
    
    # Add to workflow trace
    trace_entry = {
        "node_name": "parse_query",
        "status": "completed",
        "tool_called": "deterministic_parser" if fallback_used else "watsonx.ai",
        "fallback_used": fallback_used
    }
    
    if error_message:
        trace_entry["error_message"] = error_message
    
    state["workflow_trace"] = [
        *state.get("workflow_trace", []),
        trace_entry
    ]
    
    return state

# Made with Bob
