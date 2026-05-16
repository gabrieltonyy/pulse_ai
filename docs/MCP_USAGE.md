# MCP Tool Usage Guide

## Overview

Pulse AI exposes 3 Model Context Protocol (MCP) tools that allow AI assistants like Claude to search events, enrich venues, and get weather forecasts.

## Available Tools

### 1. pulse_search_events

Search for events using the complete Pulse AI recommendation workflow.

**Tool Name:** `pulse_search_events`

**Description:** Search for events using natural language and get AI-powered recommendations with context-aware ranking.

**Input Schema:**
```json
{
  "query": "string (required)",
  "city": "string (optional)",
  "country": "string (optional, default: US)",
  "category": "string (optional)",
  "date_from": "string (optional, ISO 8601)",
  "date_to": "string (optional, ISO 8601)",
  "budget_max": "number (optional)",
  "use_demo": "boolean (optional, default: false)"
}
```

**Output:**
```json
{
  "success": true,
  "summary": "Found 5 Music events in London...",
  "events": [
    {
      "event": {...},
      "recommendation": {
        "total_score": 85.5,
        "label": "Best Overall",
        "explanation": "..."
      },
      "venue_context": {...},
      "weather_context": {...}
    }
  ],
  "workflow_trace": [...],
  "errors": []
}
```

**Example Usage:**
```python
# Search for rock concerts in London
result = await pulse_search_events(
    query="rock concerts this weekend",
    city="London",
    country="GB",
    category="Music"
)

# Demo mode (no API calls)
result = await pulse_search_events(
    query="concerts in London",
    use_demo=True
)
```

### 2. pulse_enrich_venue

Get nearby places and context for a venue location.

**Tool Name:** `pulse_enrich_venue`

**Description:** Retrieve nearby restaurants, entertainment venues, and public transport for a given location.

**Input Schema:**
```json
{
  "latitude": "number (required)",
  "longitude": "number (required)",
  "radius": "number (optional, default: 1000, in meters)"
}
```

**Output:**
```json
{
  "nearby_places": [
    {
      "name": "Restaurant Name",
      "category": "catering.restaurant",
      "distance": 250
    }
  ],
  "area_summary": "Vibrant area with 5 restaurants...",
  "transport_context": "Well-connected with..."
}
```

**Example Usage:**
```python
# Get context for London venue
result = await pulse_enrich_venue(
    latitude=51.5074,
    longitude=-0.1278,
    radius=1000
)
```

### 3. pulse_get_weather

Get weather forecast for an event location and date.

**Tool Name:** `pulse_get_weather`

**Description:** Retrieve weather forecast and outdoor suitability assessment for an event.

**Input Schema:**
```json
{
  "latitude": "number (required)",
  "longitude": "number (required)",
  "date": "string (required, ISO 8601)"
}
```

**Output:**
```json
{
  "temperature": 18.5,
  "conditions": "partly cloudy",
  "rain_probability": 20,
  "outdoor_suitability": "good",
  "weather_note": "Pleasant weather expected..."
}
```

**Example Usage:**
```python
# Get weather for event
from datetime import datetime, timedelta

future_date = (datetime.now() + timedelta(days=3)).isoformat()
result = await pulse_get_weather(
    latitude=51.5074,
    longitude=-0.1278,
    date=future_date
)
```

## Running the MCP Server

### Standalone Mode

```bash
# Run MCP server with stdio transport
python -m app.mcp.server
```

### Claude Desktop Configuration

Add to Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "pulse-ai": {
      "command": "python",
      "args": ["-m", "app.mcp.server"],
      "cwd": "/path/to/pulse_ai",
      "env": {
        "WATSONX_API_KEY": "your_key",
        "TICKETMASTER_API_KEY": "your_key",
        "GEOAPIFY_API_KEY": "your_key",
        "OPENWEATHER_API_KEY": "your_key"
      }
    }
  }
}
```

### VSCode MCP Configuration

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "pulse-ai": {
      "command": "python",
      "args": ["-m", "app.mcp.server"],
      "env": {
        "WATSONX_API_KEY": "${env:WATSONX_API_KEY}",
        "TICKETMASTER_API_KEY": "${env:TICKETMASTER_API_KEY}",
        "GEOAPIFY_API_KEY": "${env:GEOAPIFY_API_KEY}",
        "OPENWEATHER_API_KEY": "${env:OPENWEATHER_API_KEY}"
      }
    }
  }
}
```

## Testing MCP Tools

```bash
# Run MCP tool tests
pytest tests/test_mcp_tools.py -v

# Test specific tool
pytest tests/test_mcp_tools.py::test_pulse_search_events_demo -v
```

## Troubleshooting

### Server Won't Start

**Issue:** `ImportError: cannot import name 'create_pulse_workflow'`

**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Tool Returns Errors

**Issue:** API errors in tool responses

**Solution:** 
1. Verify API keys in environment
2. Check API rate limits
3. Use `use_demo=True` for testing

### Claude Desktop Not Finding Tools

**Issue:** Tools not appearing in Claude

**Solution:**
1. Verify MCP config path is correct
2. Check `cwd` points to project root
3. Restart Claude Desktop
4. Check Claude logs: `~/Library/Logs/Claude/mcp*.log`

### Slow Response Times

**Issue:** Tools taking >10 seconds

**Solution:**
1. Use demo mode for testing
2. Check network connectivity
3. Verify API endpoints are responsive
4. Consider caching strategies

## Best Practices

1. **Use Demo Mode for Development**
   - Faster responses
   - No API rate limits
   - Consistent test data

2. **Handle Errors Gracefully**
   - Check `success` field in responses
   - Review `errors` array for issues
   - Implement retry logic for transient failures

3. **Optimize Queries**
   - Be specific with search parameters
   - Use date ranges to limit results
   - Specify category when known

4. **Monitor API Usage**
   - Track API calls in logs
   - Implement rate limiting
   - Use caching for repeated queries

## Examples

### Complete Event Search Workflow

```python
# 1. Search for events
search_result = await pulse_search_events(
    query="jazz concerts in New York next weekend",
    city="New York",
    country="US",
    category="Music",
    budget_max=100
)

# 2. Get top event
top_event = search_result["events"][0]

# 3. Enrich venue if needed
if top_event["event"]["latitude"]:
    venue_context = await pulse_enrich_venue(
        latitude=top_event["event"]["latitude"],
        longitude=top_event["event"]["longitude"]
    )

# 4. Check weather
weather = await pulse_get_weather(
    latitude=top_event["event"]["latitude"],
    longitude=top_event["event"]["longitude"],
    date=top_event["event"]["start_datetime"]
)
```

### Demo Mode Testing

```python
# Quick demo search
demo_result = await pulse_search_events(
    query="rock concerts",
    use_demo=True
)

# Verify results
assert demo_result["success"]
assert len(demo_result["events"]) > 0
```

## Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/mcp)
- [Pulse AI API Documentation](http://localhost:8000/docs)