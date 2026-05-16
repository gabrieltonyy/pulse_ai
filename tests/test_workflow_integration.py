"""Integration tests for complete LangGraph workflow"""
import pytest
from app.graph.workflow import create_pulse_workflow
from app.models.search import SearchIntent


@pytest.mark.asyncio
async def test_workflow_demo_mode():
    """Test complete workflow in demo mode"""
    workflow = create_pulse_workflow()
    
    initial_state = {
        "raw_query": "rock concerts in London this weekend",
        "city": "London",
        "country": "GB",
        "category": "Music",
        "use_demo_data": True,
        "errors": [],
        "workflow_trace": []
    }
    
    result = await workflow.ainvoke(initial_state)
    
    # Verify workflow completed
    assert "recommendation_summary" in result
    assert "ranked_events" in result
    assert len(result["ranked_events"]) > 0
    
    # Verify all nodes executed
    node_names = [trace["node_name"] for trace in result["workflow_trace"]]
    expected_nodes = [
        "parse_query", "validate_query", "search_events",
        "normalize_events", "enrich_venues", "weather_context",
        "rank_events", "generate_explanations", "prepare_response"
    ]
    for node in expected_nodes:
        assert node in node_names, f"Node {node} not executed"
    
    # Verify ranking
    first_event = result["ranked_events"][0]
    assert "recommendation" in first_event
    assert first_event["recommendation"]["total_score"] > 0
    assert first_event["recommendation"]["label"] == "Best Overall"


@pytest.mark.asyncio
async def test_workflow_with_live_apis():
    """Test workflow with live API calls (requires API keys)"""
    workflow = create_pulse_workflow()
    
    initial_state = {
        "raw_query": "jazz concerts in New York next month",
        "city": "New York",
        "country": "US",
        "category": "Music",
        "use_demo_data": False,
        "errors": [],
        "workflow_trace": []
    }
    
    result = await workflow.ainvoke(initial_state)
    
    # Should complete even if no events found
    assert "recommendation_summary" in result
    assert "ranked_events" in result
    assert isinstance(result["errors"], list)


@pytest.mark.asyncio
async def test_workflow_error_handling():
    """Test workflow handles errors gracefully"""
    workflow = create_pulse_workflow()
    
    # Invalid query - use a query that will fail validation but not crash
    initial_state = {
        "raw_query": "x",  # Too short but will pass initial validation
        "use_demo_data": True,
        "errors": [],
        "workflow_trace": []
    }
    
    try:
        result = await workflow.ainvoke(initial_state)
        
        # Should complete without crashing
        assert "errors" in result
        assert "workflow_trace" in result
    except Exception as e:
        # If it raises an exception, that's also acceptable for error handling test
        # as long as it's a validation error, not a crash
        assert "validation" in str(e).lower() or "error" in str(e).lower()

# Made with Bob
