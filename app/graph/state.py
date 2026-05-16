"""
LangGraph State Definition for Pulse AI.
Defines the central state passed between workflow nodes.
"""
from typing import TypedDict, Any


class PulseGraphState(TypedDict, total=False):
    """
    Central state for the Pulse AI LangGraph workflow.
    
    This state is passed between all nodes in the workflow and accumulates
    data as the search progresses through parsing, validation, enrichment,
    ranking, and response generation.
    """
    
    # Input
    raw_query: str
    user_session_id: str
    
    # Parsed Intent
    parsed_intent: dict[str, Any]
    validation: dict[str, Any]
    
    # Search Parameters
    city: str
    country: str
    category: str
    keyword: str
    date_from: str
    date_to: str
    budget_max: float
    currency: str
    preferences: list[str]
    
    # Event Data at Various Stages
    events_raw: list[dict[str, Any]]
    events_normalized: list[dict[str, Any]]
    enriched_events: list[dict[str, Any]]
    ranked_events: list[dict[str, Any]]
    
    # Recommendations
    recommendation_summary: str
    selected_event: dict[str, Any]
    
    # Calendar & Redirect
    calendar_export: dict[str, Any]
    redirect_url: str
    
    # Error Handling & Fallbacks
    errors: list[dict[str, Any]]
    fallback_used: bool
    demo_mode: bool
    
    # Workflow Tracking
    workflow_trace: list[dict[str, Any]]

# Made with Bob
