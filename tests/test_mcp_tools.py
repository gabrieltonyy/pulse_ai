"""Tests for MCP tools"""
import pytest
from app.mcp.tools.pulse_search_events import pulse_search_events
from app.mcp.tools.pulse_enrich_venue import pulse_enrich_venue
from app.mcp.tools.pulse_get_weather import pulse_get_weather


@pytest.mark.asyncio
async def test_pulse_search_events_demo():
    """Test pulse_search_events in demo mode"""
    result = await pulse_search_events(
        query="rock concerts in London",
        city="London",
        country="GB",
        use_demo=True
    )
    
    assert result["success"] is True
    assert len(result["events"]) > 0
    assert "summary" in result


@pytest.mark.asyncio
async def test_pulse_search_events_with_category():
    """Test pulse_search_events with category filter"""
    result = await pulse_search_events(
        query="sports events",
        city="London",
        country="GB",
        category="Sports",
        use_demo=True
    )
    
    assert result["success"] is True
    assert "events" in result


@pytest.mark.asyncio
async def test_pulse_search_events_with_date_range():
    """Test pulse_search_events with date range"""
    result = await pulse_search_events(
        query="concerts",
        city="London",
        country="GB",
        date_from="2026-06-01",
        date_to="2026-06-30",
        use_demo=True
    )
    
    assert result["success"] is True
    assert "events" in result


@pytest.mark.asyncio
async def test_pulse_enrich_venue():
    """Test pulse_enrich_venue"""
    # London coordinates
    result = await pulse_enrich_venue(
        latitude=51.5074,
        longitude=-0.1278,
        radius=1000
    )
    
    assert "nearby_places" in result
    assert isinstance(result["nearby_places"], list)


@pytest.mark.asyncio
async def test_pulse_enrich_venue_invalid_coords():
    """Test pulse_enrich_venue with invalid coordinates"""
    result = await pulse_enrich_venue(
        latitude=999.0,  # Invalid latitude
        longitude=-0.1278,
        radius=1000
    )
    
    # Should handle gracefully
    assert "error" in result or "nearby_places" in result


@pytest.mark.asyncio
async def test_pulse_get_weather():
    """Test pulse_get_weather"""
    from datetime import datetime, timedelta
    
    # Future date
    future_date = (datetime.now() + timedelta(days=3)).isoformat()
    
    result = await pulse_get_weather(
        latitude=51.5074,
        longitude=-0.1278,
        date=future_date
    )
    
    assert "temperature" in result
    assert "outdoor_suitability" in result


@pytest.mark.asyncio
async def test_pulse_get_weather_current():
    """Test pulse_get_weather for current date"""
    from datetime import datetime
    
    current_date = datetime.now().isoformat()
    
    result = await pulse_get_weather(
        latitude=51.5074,
        longitude=-0.1278,
        date=current_date
    )
    
    assert "temperature" in result or "error" in result


@pytest.mark.asyncio
async def test_pulse_search_events_error_handling():
    """Test pulse_search_events handles errors gracefully"""
    result = await pulse_search_events(
        query="",  # Empty query
        city="",
        country="",
        use_demo=True
    )
    
    # Should return error or empty results
    assert "success" in result
    if not result["success"]:
        assert "error" in result or "message" in result

# Made with Bob
