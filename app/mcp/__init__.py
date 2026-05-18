"""MCP (Model Context Protocol) module for Pulse AI."""
from app.mcp.server import server as mcp


def get_mcp_server():
    """Return the configured Pulse AI MCP server instance."""
    return mcp

__all__ = [
    "get_mcp_server",
    "mcp",
]

# Made with Bob
