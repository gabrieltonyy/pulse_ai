"""
Parse Query Node - Extracts structured intent from user query using watsonx.ai LLM.
"""
import logging
import time

from app.graph.state import PulseGraphState
from app.config.settings import settings
from app.services.llm_service import LLMService


logger = logging.getLogger(__name__)


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
    started = time.perf_counter()
    
    try:
        # Use LLM to parse query
        intent = await llm_service.parse_query(state["raw_query"])
        parse_source = getattr(llm_service, "last_parse_source", "unknown")
        fallback_used = parse_source == "deterministic" or settings.demo_mode
        logger.info(
            "Query parsing completed",
            extra={"parse_source": parse_source, "fallback_used": fallback_used},
        )
        
    except Exception as e:
        # Fallback already handled in LLMService, but catch any unexpected errors
        error_message = str(e)
        fallback_used = True
        
        # Use deterministic fallback
        intent = llm_service._deterministic_fallback(state["raw_query"])
        logger.warning(
            "Query parsing failed unexpectedly; deterministic fallback used",
            extra={"parse_source": "deterministic", "fallback_used": True, "error_type": type(e).__name__},
        )

    updated_values = {
        "parsed_intent": intent.model_dump(),
        "city": state.get("city") or intent.city,
        "country": state.get("country") or intent.country,
        "category": state.get("category") or intent.category,
        "keyword": state.get("keyword") or intent.keyword,
        "date_from": state.get("date_from") or (intent.date_from.isoformat() if intent.date_from else None),
        "date_to": state.get("date_to") or (intent.date_to.isoformat() if intent.date_to else None),
        "budget_max": state.get("budget_max") if state.get("budget_max") is not None else intent.budget_max,
        "currency": state.get("currency") or intent.currency,
        "preferences": state.get("preferences") or intent.preferences,
    }
    
    # Add to workflow trace
    trace_entry = {
        "node_name": "parse_query",
        "status": "completed",
        "tool_called": "deterministic_parser" if fallback_used or settings.demo_mode else "watsonx.ai",
        "fallback_used": fallback_used or settings.demo_mode,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
    }
    
    if error_message:
        trace_entry["error_message"] = error_message
    
    return {
        **state,
        **updated_values,
        "workflow_trace": [
            *state.get("workflow_trace", []),
            trace_entry,
        ],
    }

# Made with Bob
