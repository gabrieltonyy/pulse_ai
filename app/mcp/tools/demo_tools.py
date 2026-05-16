"""
Demo mode tools for MCP - provides fallback data when APIs are unavailable.
"""
from typing import Any


async def get_demo_events(
    city: str,
    category: str = "music",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Get demo event data for testing and fallback.
    
    Args:
        city: City name
        category: Event category
        limit: Maximum number of events
        
    Returns:
        list: Demo events
    """
    # TODO: Implement in Phase 2
    return []


async def get_demo_venue_context() -> dict[str, Any]:
    """
    Get demo venue context data.
    
    Returns:
        dict: Demo venue context
    """
    # TODO: Implement in Phase 2
    return {}


async def get_demo_weather_context() -> dict[str, Any]:
    """
    Get demo weather context data.
    
    Returns:
        dict: Demo weather context
    """
    # TODO: Implement in Phase 2
    return {}

# Made with Bob
