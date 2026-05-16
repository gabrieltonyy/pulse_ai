# Pulse AI — Data Models and Schemas

## 1. Purpose

This document defines the core data models, Pydantic schemas, database tables, LangGraph state, MCP tool contracts, and API response structures for Pulse AI.

Bob should use this document as the single source of truth when creating:

* Python models,
* LangGraph state,
* API clients,
* database schema,
* HTMX response data,
* MCP tool inputs and outputs,
* tests.

---

# 2. Design Principles

All schemas should be:

```text
clear
typed
minimal
extensible
safe for public demo
provider-independent
```

The application must not depend directly on Ticketmaster, Geoapify, or OpenWeather raw response shapes inside the UI or ranking engine.

External API responses must be normalized first.

---

# 3. Core Model Groups

Pulse AI needs these model groups:

```text
Search models
Event models
Venue models
Weather models
Recommendation models
Calendar models
Redirect models
LangGraph state
Database models
MCP tool schemas
API response schemas
```

---

# 4. Search Models

## 4.1 SearchIntent

Represents the structured meaning extracted from the user query.

```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, list

class SearchIntent(BaseModel):
    raw_query: str = Field(..., min_length=2, max_length=300)
    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    keyword: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    budget_max: Optional[float] = None
    currency: str = "USD"
    preferences: list[str] = []
```

---

## 4.2 SearchRequest

Represents the request received from the UI/API.

```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=300)
    demo_mode: bool = False
```

---

## 4.3 SearchValidationResult

```python
class SearchValidationResult(BaseModel):
    is_valid: bool
    missing_fields: list[str] = []
    message: Optional[str] = None
```

---

# 5. Event Models

## 5.1 Event

Normalized event object used across the app.

```python
from datetime import datetime

class Event(BaseModel):
    id: str
    provider_event_id: str
    provider: str

    title: str
    description: Optional[str] = None
    category: Optional[str] = None

    venue_name: Optional[str] = None
    venue_city: Optional[str] = None
    venue_country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: str = "USD"

    provider_event_url: Optional[str] = None
    image_url: Optional[str] = None

    popularity_score: Optional[float] = None
    source_payload_ref: Optional[str] = None
```

---

## 5.2 EventCardViewModel

Used by Jinja2 templates.

```python
class EventCardViewModel(BaseModel):
    id: str
    title: str
    date_label: str
    venue_label: str
    price_label: str
    image_url: Optional[str]
    provider: str
    recommendation_label: str
    explanation: str
    ticket_url: str
    calendar_url: str
    save_url: str
```

---

# 6. Venue Models

## 6.1 NearbyPlace

```python
class NearbyPlace(BaseModel):
    name: str
    category: str
    distance_meters: Optional[int] = None
    address: Optional[str] = None
```

---

## 6.2 VenueContext

```python
class VenueContext(BaseModel):
    venue_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nearby_places: list[NearbyPlace] = []
    area_summary: Optional[str] = None
    transport_context: Optional[str] = None
```

---

# 7. Weather Models

## 7.1 WeatherContext

```python
class WeatherContext(BaseModel):
    temperature_celsius: Optional[float] = None
    condition: Optional[str] = None
    rain_probability: Optional[float] = None
    outdoor_suitability: Optional[str] = None
    weather_note: Optional[str] = None
```

Allowed `outdoor_suitability` values:

```text
good
moderate
poor
unknown
```

---

# 8. Enriched Event Model

## 8.1 EnrichedEvent

Combines event data with location and weather context.

```python
class EnrichedEvent(BaseModel):
    event: Event
    venue_context: Optional[VenueContext] = None
    weather_context: Optional[WeatherContext] = None
```

---

# 9. Recommendation Models

## 9.1 RecommendationScore

```python
class RecommendationScore(BaseModel):
    event_id: str
    total_score: float

    relevance_score: float = 0
    date_match_score: float = 0
    affordability_score: float = 0
    popularity_score: float = 0
    context_score: float = 0
    weather_score: float = 0

    label: str
    explanation: str
```

Allowed labels:

```text
Best Overall
Best Budget Pick
Trending Option
Closest Match
Premium Pick
Great Venue
Outdoor Friendly
```

---

## 9.2 RankedEvent

```python
class RankedEvent(BaseModel):
    event: Event
    recommendation: RecommendationScore
    venue_context: Optional[VenueContext] = None
    weather_context: Optional[WeatherContext] = None
```

---

# 10. Calendar Models

## 10.1 CalendarExportRequest

```python
class CalendarExportRequest(BaseModel):
    event_id: str
```

---

## 10.2 CalendarExportResult

```python
class CalendarExportResult(BaseModel):
    event_id: str
    filename: str
    content_type: str = "text/calendar"
    download_url: str
```

---

# 11. Redirect Models

## 11.1 TicketRedirectRequest

```python
class TicketRedirectRequest(BaseModel):
    event_id: str
```

---

## 11.2 TicketRedirectResult

```python
class TicketRedirectResult(BaseModel):
    event_id: str
    provider: str
    redirect_url: str
    external_url: str
    safe: bool
```

---

# 12. LangGraph State

## 12.1 PulseGraphState

This is the central state passed between LangGraph nodes.

```python
from typing import TypedDict, Any

class PulseGraphState(TypedDict, total=False):
    raw_query: str
    user_session_id: str

    parsed_intent: dict
    validation: dict

    city: str
    country: str
    category: str
    keyword: str
    date_from: str
    date_to: str
    budget_max: float
    currency: str
    preferences: list[str]

    events_raw: list[dict]
    events_normalized: list[dict]
    enriched_events: list[dict]
    ranked_events: list[dict]

    recommendation_summary: str
    selected_event: dict

    calendar_export: dict
    redirect_url: str

    errors: list[dict]
    fallback_used: bool
    demo_mode: bool

    workflow_trace: list[dict]
```

---

# 13. Workflow Trace Model

## 13.1 WorkflowTraceItem

```python
class WorkflowTraceItem(BaseModel):
    node_name: str
    status: str
    tool_called: Optional[str] = None
    provider: Optional[str] = None
    fallback_used: bool = False
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
```

Allowed status values:

```text
pending
running
completed
failed
skipped
```

---

# 14. MCP Tool Schemas

## 14.1 pulse_search_events Input

```python
class PulseSearchEventsInput(BaseModel):
    city: str
    country: Optional[str] = None
    category: Optional[str] = None
    keyword: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    budget_max: Optional[float] = None
    currency: str = "USD"
    limit: int = 10
```

---

## 14.2 pulse_search_events Output

```python
class PulseSearchEventsOutput(BaseModel):
    success: bool
    provider: str
    events: list[Event] = []
    fallback_used: bool = False
    error: Optional[str] = None
```

---

## 14.3 pulse_enrich_venue Input

```python
class PulseEnrichVenueInput(BaseModel):
    venue_name: Optional[str] = None
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: int = 1000
```

---

## 14.4 pulse_enrich_venue Output

```python
class PulseEnrichVenueOutput(BaseModel):
    success: bool
    venue_context: Optional[VenueContext] = None
    fallback_used: bool = False
    error: Optional[str] = None
```

---

## 14.5 pulse_get_weather_context Input

```python
class PulseWeatherInput(BaseModel):
    latitude: float
    longitude: float
    event_datetime: Optional[str] = None
    event_type: Optional[str] = None
```

---

## 14.6 pulse_get_weather_context Output

```python
class PulseWeatherOutput(BaseModel):
    success: bool
    weather_context: Optional[WeatherContext] = None
    error: Optional[str] = None
```

---

## 14.7 pulse_rank_events Input

```python
class PulseRankEventsInput(BaseModel):
    events: list[EnrichedEvent]
    intent: SearchIntent
```

---

## 14.8 pulse_rank_events Output

```python
class PulseRankEventsOutput(BaseModel):
    success: bool
    ranked_events: list[RankedEvent] = []
    error: Optional[str] = None
```

---

# 15. API Response Schemas

## 15.1 SearchResponse

```python
class SearchResponse(BaseModel):
    success: bool
    query: str
    ranked_events: list[RankedEvent] = []
    recommendation_summary: Optional[str] = None
    workflow_trace: list[WorkflowTraceItem] = []
    fallback_used: bool = False
    message: Optional[str] = None
```

---

## 15.2 ErrorResponse

```python
class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    fallback_available: bool = False
```

---

# 16. Database Tables

## 16.1 saved_events

```sql
CREATE TABLE IF NOT EXISTS saved_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    title TEXT NOT NULL,
    event_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

---

## 16.2 search_history

```sql
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    raw_query TEXT NOT NULL,
    parsed_intent_json TEXT,
    result_count INTEGER DEFAULT 0,
    fallback_used INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);
```

---

## 16.3 api_cache

```sql
CREATE TABLE IF NOT EXISTS api_cache (
    cache_key TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    provider TEXT,
    request_hash TEXT NOT NULL,
    response_json TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

---

## 16.4 outbound_clicks

```sql
CREATE TABLE IF NOT EXISTS outbound_clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    event_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    clicked_at TEXT NOT NULL
);
```

---

# 17. Provider Normalization Rules

Raw provider data must be transformed into the `Event` model.

## Ticketmaster Mapping

| Ticketmaster Field                       | Pulse Event Field    |
| ---------------------------------------- | -------------------- |
| `id`                                     | `provider_event_id`  |
| `name`                                   | `title`              |
| `info` / `pleaseNote`                    | `description`        |
| `classifications[0].segment.name`        | `category`           |
| `_embedded.venues[0].name`               | `venue_name`         |
| `_embedded.venues[0].city.name`          | `venue_city`         |
| `_embedded.venues[0].country.name`       | `venue_country`      |
| `_embedded.venues[0].location.latitude`  | `latitude`           |
| `_embedded.venues[0].location.longitude` | `longitude`          |
| `dates.start.dateTime`                   | `start_datetime`     |
| `priceRanges[0].min`                     | `price_min`          |
| `priceRanges[0].max`                     | `price_max`          |
| `priceRanges[0].currency`                | `currency`           |
| `url`                                    | `provider_event_url` |
| `images[0].url`                          | `image_url`          |

---

# 18. Validation Rules

## Search Query

```text
min length: 2
max length: 300
```

## City

```text
must be text
max length: 100
```

## Budget

```text
must be positive
max suggested: 10000
```

## Limit

```text
min: 1
max: 50
default: 10
```

---

# 19. Safe Defaults

Use these defaults when fields are missing:

```text
currency = USD
limit = 10
date range = upcoming weekend
fallback_used = false
demo_mode = false
```

---

# 20. File Structure

Recommended schema files:

```text
app/models/
  search.py
  event.py
  venue.py
  weather.py
  recommendation.py
  calendar.py
  redirect.py
  trace.py

app/graph/
  state.py
```

---

# 21. Final Schema Goal

Every part of Pulse AI should communicate using typed internal models.

The final data flow should be:

```text
Raw user query
→ SearchIntent
→ Provider API request
→ Raw provider response
→ Event
→ EnrichedEvent
→ RankedEvent
→ EventCardViewModel
→ Jinja2 rendered UI
```

This prevents provider lock-in, reduces bugs, and gives Bob a stable structure to build from.
