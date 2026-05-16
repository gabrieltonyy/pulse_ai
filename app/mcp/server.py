"""
MCP (Model Context Protocol) Server for Pulse AI.
Exposes tools for event search, venue enrichment, weather context, and more.
"""
from fastmcp import FastMCP

from app.config import settings

# Initialize FastMCP server
mcp = FastMCP("pulse-ai-mcp")


# Import tool modules (will be implemented in Phase 2)
# from app.mcp.tools import (
#     event_tools,
#     location_tools,
#     weather_tools,
#     ranking_tools,
#     calendar_tools,
#     redirect_tools,
#     demo_tools,
# )


@mcp.tool()
async def health_check() -> dict:
    """
    Health check tool for MCP server.
    
    Returns:
        dict: Server health status
    """
    return {
        "status": "healthy",
        "server": "pulse-ai-mcp",
        "version": "0.1.0",
        "demo_mode": settings.demo_mode,
    }


# Tool registration will happen here in Phase 2
# Example:
# @mcp.tool()
# async def pulse_search_events(...):
#     """Search for events using Ticketmaster API or demo data."""
#     pass


def get_mcp_server() -> FastMCP:
    """
    Get the MCP server instance.
    
    Returns:
        FastMCP: Configured MCP server
    """
    return mcp


if __name__ == "__main__":
    # Run MCP server standalone
    import uvicorn
    
    uvicorn.run(
        "app.mcp.server:mcp",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
    )

# Made with Bob
