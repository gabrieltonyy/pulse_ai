"""MCP server exposing Pulse AI tools via stdio transport."""
from __future__ import annotations

import asyncio
import json
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server

from app.mcp.tools.pulse_enrich_venue import pulse_enrich_venue
from app.mcp.tools.pulse_get_weather import pulse_get_weather
from app.mcp.tools.pulse_search_events import pulse_search_events

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------
server = Server("pulse-ai")


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------
@server.list_tools()
async def list_tools():
    """Return the list of tools this MCP server exposes."""
    return [
        {
            "name": "pulse_search_events",
            "description": (
                "Search for events using the Pulse AI recommendation engine. "
                "Runs the full LangGraph pipeline: parse → validate → search → "
                "normalize → enrich → weather → rank → explain → prepare."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (required).",
                    },
                    "city": {
                        "type": "string",
                        "description": "City name – optional, can be inferred from query.",
                    },
                    "country": {
                        "type": "string",
                        "description": "ISO 3166-1 alpha-2 country code (default: US).",
                    },
                    "category": {
                        "type": "string",
                        "description": "Event category, e.g. Music, Sports, Arts.",
                    },
                    "date_from": {
                        "type": "string",
                        "description": "Start date YYYY-MM-DD.",
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date YYYY-MM-DD.",
                    },
                    "budget_max": {
                        "type": "number",
                        "description": "Maximum ticket price in USD.",
                    },
                    "use_demo": {
                        "type": "boolean",
                        "description": "Use bundled demo data instead of live APIs.",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "pulse_enrich_venue",
            "description": (
                "Get nearby places and contextual information (restaurants, transport, "
                "parking, entertainment) for a venue location using Geoapify."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Venue latitude (decimal degrees).",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Venue longitude (decimal degrees).",
                    },
                    "radius": {
                        "type": "number",
                        "description": "Search radius in metres (default 1000).",
                    },
                },
                "required": ["latitude", "longitude"],
            },
        },
        {
            "name": "pulse_get_weather",
            "description": (
                "Get a weather forecast for an event location and date via OpenWeather. "
                "Returns temperature, conditions, rain probability, and outdoor suitability."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Event latitude (decimal degrees).",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Event longitude (decimal degrees).",
                    },
                    "date": {
                        "type": "string",
                        "description": "Event date in ISO 8601 format (YYYY-MM-DD).",
                    },
                },
                "required": ["latitude", "longitude", "date"],
            },
        },
    ]


# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Dispatch an incoming tool call to the correct handler."""
    logger.info("MCP tool called: %s | args: %s", name, arguments)

    try:
        if name == "pulse_search_events":
            result = await pulse_search_events(**arguments)
        elif name == "pulse_enrich_venue":
            result = await pulse_enrich_venue(**arguments)
        elif name == "pulse_get_weather":
            result = await pulse_get_weather(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name!r}")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Tool %r raised an error", name)
        result = {"success": False, "error": str(exc)}

    return [{"type": "text", "text": json.dumps(result, default=str)}]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())