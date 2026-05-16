"""Performance tests"""
import pytest
import time
from app.graph.workflow import create_pulse_workflow


@pytest.mark.asyncio
async def test_workflow_performance_demo():
    """Test workflow completes in reasonable time (demo mode)"""
    workflow = create_pulse_workflow()
    
    initial_state = {
        "raw_query": "concerts in London",
        "city": "London",
        "use_demo_data": True,
        "errors": [],
        "workflow_trace": []
    }
    
    start = time.time()
    result = await workflow.ainvoke(initial_state)
    duration = time.time() - start
    
    # Should complete in under 5 seconds in demo mode
    assert duration < 5.0, f"Workflow took {duration}s (expected < 5s)"
    assert len(result["ranked_events"]) > 0


@pytest.mark.asyncio
async def test_ranking_performance():
    """Test ranking service performance"""
    from app.services.ranking_service import RankingService
    from app.models.search import SearchIntent
    
    # Create mock enriched events
    enriched_events = [
        {
            "event": {
                "id": f"evt_{i}",
                "title": f"Event {i}",
                "category": "Music",
                "price_min": 20,
                "start_datetime": "2026-05-20T19:00:00Z"
            },
            "venue_context": None,
            "weather_context": None
        }
        for i in range(100)
    ]
    
    intent = SearchIntent(
        raw_query="concerts",
        city="London",
        category="Music"
    )
    
    ranking_service = RankingService()
    
    start = time.time()
    ranked = ranking_service.rank_events(enriched_events, intent)
    duration = time.time() - start
    
    # Should rank 100 events in under 1 second
    assert duration < 1.0, f"Ranking took {duration}s (expected < 1s)"
    assert len(ranked) == 100


@pytest.mark.asyncio
async def test_demo_data_loading_performance():
    """Test demo data loads quickly"""
    from app.services.demo_provider import DemoProvider
    
    provider = DemoProvider()
    
    start = time.time()
    events = provider.search_events(city="London", category="Music")
    duration = time.time() - start
    
    # Should load demo data in under 0.1 seconds
    assert duration < 0.1, f"Demo data loading took {duration}s (expected < 0.1s)"
    assert len(events) > 0


@pytest.mark.asyncio
@pytest.mark.slow
async def test_multiple_concurrent_workflows():
    """Test multiple workflows can run concurrently"""
    import asyncio
    
    workflow = create_pulse_workflow()
    
    async def run_workflow(query: str):
        initial_state = {
            "raw_query": query,
            "city": "London",
            "use_demo_data": True,
            "errors": [],
            "workflow_trace": []
        }
        return await workflow.ainvoke(initial_state)
    
    queries = [
        "rock concerts",
        "jazz events",
        "sports games",
        "theater shows",
        "comedy nights"
    ]
    
    start = time.time()
    results = await asyncio.gather(*[run_workflow(q) for q in queries])
    duration = time.time() - start
    
    # Should complete 5 concurrent workflows in under 10 seconds
    assert duration < 10.0, f"Concurrent workflows took {duration}s (expected < 10s)"
    assert len(results) == 5
    assert all("ranked_events" in r for r in results)


@pytest.mark.asyncio
async def test_llm_service_performance():
    """Test LLM service response time"""
    from app.services.llm_service import LLMService
    
    llm_service = LLMService()
    
    # Test query parsing
    start = time.time()
    result = await llm_service.parse_query("rock concerts in London this weekend")
    duration = time.time() - start
    
    # Should complete in under 3 seconds
    assert duration < 3.0, f"LLM parsing took {duration}s (expected < 3s)"
    assert result is not None

# Made with Bob
