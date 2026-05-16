# Pulse AI — MCP Integration Specification

## 1. Purpose

This document defines how Pulse AI will use MCP-style tools to power event discovery, venue enrichment, ranking, calendar export, and ticket redirection.

The goal is to make the application feel like an AI concierge that can use tools, not just answer questions.

---

## 2. MCP Strategy

Pulse AI will use a **Python-first MCP architecture**.

The system will start with Python tool functions used by LangGraph nodes, then expose those tools through **FastMCP**.

```text
LangGraph Node
   ↓
Python Tool Function
   ↓
FastMCP Tool Exposure
   ↓
External API / Internal Service
```

This keeps development simple while still demonstrating MCP clearly.

---

## 3. Core MCP Tools

| Tool                             | Purpose                                   |
| -------------------------------- | ----------------------------------------- |
| `pulse_search_events`            | Search global event providers             |
| `pulse_enrich_venue`             | Add venue and location context            |
| `pulse_get_weather_context`      | Add weather suitability                   |
| `pulse_rank_events`              | Score and rank events                     |
| `pulse_create_calendar_file`     | Generate `.ics` calendar export           |
| `pulse_generate_ticket_redirect` | Validate and prepare outbound ticket link |
| `pulse_get_demo_events`          | Provide fallback demo data                |

---

# 4. Tool Specifications

## 4.1 `pulse_search_events`

### Purpose

Searches event providers using parsed user intent.

### Primary Provider

Ticketmaster Discovery API

### Optional Providers

* Eventbrite
* Meetup
* Dice
* Resident Advisor

### Input

```json
{
  "city": "Berlin",
  "country": "Germany",
  "category": "electronic music",
  "date_from": "2026-06-01",
  "date_to": "2026-06-03",
  "budget_max": 100,
  "currency": "USD",
  "limit": 10
}
```

### Output

```json
{
  "provider": "ticketmaster",
  "events": [
    {
      "provider_event_id": "abc123",
      "title": "Electronic Night Berlin",
      "description": "Live electronic music event",
      "category": "music",
      "venue_name": "Berlin Arena",
      "city": "Berlin",
      "country": "Germany",
      "latitude": 52.52,
      "longitude": 13.405,
      "start_datetime": "2026-06-01T20:00:00Z",
      "price_min": 40,
      "price_max": 95,
      "currency": "USD",
      "provider_event_url": "https://example.com/tickets",
      "image_url": "https://example.com/event.jpg"
    }
  ]
}
```

### Failure Handling

| Failure          | Behavior                          |
| ---------------- | --------------------------------- |
| Provider timeout | Return cached result              |
| API key missing  | Return developer setup error      |
| No events found  | Return empty list with suggestion |
| Rate limit       | Use cache/demo fallback           |

---

## 4.2 `pulse_enrich_venue`

### Purpose

Adds venue and location context to event results.

### Provider

Geoapify Places API

### Input

```json
{
  "venue_name": "Berlin Arena",
  "city": "Berlin",
  "latitude": 52.52,
  "longitude": 13.405,
  "radius_meters": 1000
}
```

### Output

```json
{
  "venue_name": "Berlin Arena",
  "nearby_places": [
    {
      "name": "Central Cafe",
      "category": "restaurant",
      "distance_meters": 250
    }
  ],
  "area_summary": "The venue is close to restaurants, nightlife, and public transport.",
  "transport_context": "Public transport is available within walking distance."
}
```

### Usage

Used after event discovery to make recommendations richer and more demo-friendly.

---

## 4.3 `pulse_get_weather_context`

### Purpose

Checks weather suitability for events.

### Provider

OpenWeather API

### Input

```json
{
  "latitude": 52.52,
  "longitude": 13.405,
  "event_datetime": "2026-06-01T20:00:00Z",
  "event_type": "outdoor festival"
}
```

### Output

```json
{
  "temperature_celsius": 22,
  "condition": "Clear",
  "rain_probability": 0.1,
  "outdoor_suitability": "good",
  "weather_note": "Clear weather expected, suitable for outdoor events."
}
```

### Optional Rule

If weather API is unavailable, the workflow continues without weather scoring.

---

## 4.4 `pulse_rank_events`

### Purpose

Ranks normalized events using deterministic scoring.

### Input

```json
{
  "events": [],
  "preferences": {
    "category": "electronic music",
    "budget_max": 100,
    "date_from": "2026-06-01",
    "date_to": "2026-06-03"
  }
}
```

### Scoring Formula

```text
total_score =
  relevance_score * 0.30 +
  date_match_score * 0.20 +
  affordability_score * 0.20 +
  popularity_score * 0.15 +
  context_score * 0.10 +
  weather_score * 0.05
```

### Output

```json
{
  "ranked_events": [
    {
      "event_id": "abc123",
      "total_score": 88,
      "ranking_label": "Best Overall",
      "explanation": "Matches your electronic music preference, fits your budget, and is happening this weekend."
    }
  ]
}
```

---

## 4.5 `pulse_create_calendar_file`

### Purpose

Creates an `.ics` calendar file for a selected event.

### Input

```json
{
  "event_id": "abc123",
  "title": "Electronic Night Berlin",
  "start_datetime": "2026-06-01T20:00:00Z",
  "end_datetime": "2026-06-01T23:00:00Z",
  "venue_name": "Berlin Arena",
  "provider_event_url": "https://example.com/tickets"
}
```

### Output

```json
{
  "filename": "electronic-night-berlin.ics",
  "content_type": "text/calendar",
  "download_url": "/events/abc123/calendar.ics"
}
```

---

## 4.6 `pulse_generate_ticket_redirect`

### Purpose

Generates a safe outbound ticket provider link.

### Input

```json
{
  "event_id": "abc123",
  "provider": "ticketmaster",
  "provider_event_url": "https://ticketmaster.com/example-event"
}
```

### Output

```json
{
  "redirect_url": "/redirect/abc123",
  "external_url": "https://ticketmaster.com/example-event",
  "provider": "ticketmaster",
  "safe": true
}
```

### Safety Rules

The tool must:

* allow only approved domains
* block suspicious URLs
* log outbound clicks without personal data
* never rewrite links into unsafe targets

Approved provider domains:

* ticketmaster.com
* eventbrite.com
* meetup.com
* dice.fm
* residentadvisor.net

---

## 4.7 `pulse_get_demo_events`

### Purpose

Provides stable fallback demo data.

### Usage

Used when:

```text
DEMO_MODE=true
```

or when:

```text
external API fails
```

### Demo Cities

```text
Berlin
London
New York
Los Angeles
Paris
Amsterdam
```

### Output

Same normalized schema as `pulse_search_events`.

---

# 5. LangGraph + MCP Interaction

## Main Flow

```text
parse_query_node
   ↓
validate_query_node
   ↓
search_events_node → pulse_search_events
   ↓
normalize_events_node
   ↓
enrich_venues_node → pulse_enrich_venue
   ↓
weather_context_node → pulse_get_weather_context
   ↓
rank_events_node → pulse_rank_events
   ↓
prepare_response_node
```

---

# 6. MCP Server Structure

```text
app/mcp/
  server.py
  tools/
    event_tools.py
    location_tools.py
    weather_tools.py
    ranking_tools.py
    calendar_tools.py
    redirect_tools.py
    demo_tools.py
```

---

# 7. Example FastMCP Tool Pattern

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pulse-ai")

@mcp.tool()
async def pulse_search_events(
    city: str,
    category: str,
    date_from: str,
    date_to: str,
    budget_max: float | None = None,
    currency: str = "USD",
    limit: int = 10
) -> dict:
    """
    Search global event providers for matching events.
    """
    ...
```

---

# 8. External APIs

## Required

| API                        | Usage                     |
| -------------------------- | ------------------------- |
| Ticketmaster Discovery API | Primary event search      |
| Geoapify Places API        | Venue and area enrichment |

## Optional

| API             | Usage            |
| --------------- | ---------------- |
| OpenWeather API | Weather context  |
| Eventbrite API  | Secondary events |
| Meetup API      | Community events |

---

# 9. Environment Variables

```text
TICKETMASTER_API_KEY=
GEOAPIFY_API_KEY=
OPENWEATHER_API_KEY=

DEMO_MODE=false
CACHE_TTL_SECONDS=900
```

---

# 10. Caching Rules

Cache results for:

```text
event searches
venue enrichment
weather lookups
ranked responses
```

Recommended cache key:

```text
tool_name + normalized_input_hash
```

Example:

```text
pulse_search_events:berlin:electronic:2026-06-01:2026-06-03:100
```

---

# 11. Security Rules

The MCP tools must:

* read credentials only from environment variables
* never expose API keys in logs
* validate user input
* sanitize provider URLs
* avoid storing personal information
* avoid payment handling
* avoid scraping protected websites
* return safe errors

---

# 12. Error Response Format

All MCP tools should return consistent errors.

```json
{
  "success": false,
  "error_code": "PROVIDER_TIMEOUT",
  "message": "Ticketmaster did not respond in time.",
  "fallback_available": true
}
```

---

# 13. Observability

Each tool call should log:

```text
tool name
execution time
success/failure
provider used
cache hit/miss
fallback used
```

Do not log:

```text
API keys
raw secrets
personal user data
```

---

# 14. MVP MCP Scope

## Must Have

```text
pulse_search_events
pulse_rank_events
pulse_generate_ticket_redirect
pulse_get_demo_events
```

## Should Have

```text
pulse_enrich_venue
pulse_create_calendar_file
```

## Nice to Have

```text
pulse_get_weather_context
```

---

# 15. Final Integration Goal

The final implementation should allow Bob and the application workflow to clearly demonstrate:

```text
AI request understanding
→ LangGraph orchestration
→ MCP tool calls
→ external event data
→ contextual enrichment
→ explainable ranking
→ ticket provider handoff
```

This is the core technical story for the hackathon demo.
