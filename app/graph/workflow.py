"""
LangGraph Workflow Definition for Pulse AI.
Defines the main workflow graph and node connections.
"""
from langgraph.graph import StateGraph, END

from app.graph.state import PulseGraphState
from app.graph.nodes import (
    parse_query,
    validate_query,
    search_events,
    normalize_events,
    enrich_venues,
    weather_context,
    rank_events,
    generate_explanations,
    prepare_response,
)


def create_workflow() -> StateGraph:
    """
    Create and configure the Pulse AI workflow graph.
    
    Returns:
        StateGraph: Configured workflow graph
    """
    # Initialize the graph with our state
    workflow = StateGraph(PulseGraphState)
    
    # Add nodes to the graph
    workflow.add_node("parse_query", parse_query.parse_query_node)
    workflow.add_node("validate_query", validate_query.validate_query_node)
    workflow.add_node("search_events", search_events.search_events_node)
    workflow.add_node("normalize_events", normalize_events.normalize_events_node)
    workflow.add_node("enrich_venues", enrich_venues.enrich_venues_node)
    workflow.add_node("weather_context", weather_context.weather_context_node)
    workflow.add_node("rank_events", rank_events.rank_events_node)
    workflow.add_node("generate_explanations", generate_explanations.generate_explanations_node)
    workflow.add_node("prepare_response", prepare_response.prepare_response_node)
    
    # Define the workflow edges (node connections)
    workflow.set_entry_point("parse_query")
    
    workflow.add_edge("parse_query", "validate_query")
    workflow.add_edge("validate_query", "search_events")
    workflow.add_edge("search_events", "normalize_events")
    workflow.add_edge("normalize_events", "enrich_venues")
    workflow.add_edge("enrich_venues", "weather_context")
    workflow.add_edge("weather_context", "rank_events")
    workflow.add_edge("rank_events", "generate_explanations")
    workflow.add_edge("generate_explanations", "prepare_response")
    workflow.add_edge("prepare_response", END)
    
    return workflow


def create_pulse_workflow():
    """
    Create and compile the Pulse AI workflow graph.
    This is an alias for get_workflow() for compatibility.

    Returns:
        Compiled workflow graph
    """
    return get_workflow()


def get_compiled_workflow():
    """
    Get a compiled version of the workflow ready for execution.
    
    Returns:
        Compiled workflow graph
    """
    workflow = create_workflow()
    return workflow.compile()


# Global compiled workflow instance
compiled_workflow = None


def get_workflow():
    """
    Get or create the global compiled workflow instance.
    
    Returns:
        Compiled workflow graph
    """
    global compiled_workflow
    
    if compiled_workflow is None:
        compiled_workflow = get_compiled_workflow()
    
    return compiled_workflow


def reset_workflow() -> None:
    """Clear the global compiled workflow instance for tests."""
    global compiled_workflow

    compiled_workflow = None

# Made with Bob
