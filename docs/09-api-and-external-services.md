# Pulse AI — API and External Services Guide

## 1. Purpose

This document defines the external APIs and service integrations required for Pulse AI.

Bob should use this document when implementing:

* API clients,
* MCP tools,
* LangGraph nodes,
* environment configuration,
* fallback handling,
* tests,
* and demo mode.

---

# 2. Integration Strategy

Pulse AI should use external APIs only through isolated client modules.

```text
LangGraph Node
→ MCP/Tool Function
→ Integration Client
→ External API
```

No route, template, or ranking logic should call external APIs directly.

---

# 3. Required APIs for MVP

| API                        | Purpose                        | Priority                    |
| -------------------------- | ------------------------------ | --------------------------- |
| Ticketmaster Discovery API | Primary event search           | Required                    |
| Geoapify Places API        | Venue/location enrichment      | Required                    |
| OpenWeather API            | Weather context                | Optional but useful         |
| LLM Provider               | Intent parsing and explanation | Optional, fallback required |

---

# 4. Optional APIs

| API                     | Purpose                    | When to Add              |
| ----------------------- | -------------------------- | ------------------------ |
| Eventbrite API          | Additional event provider  | After Ticketmaster works |
| Meetup API              | Community events           | Later                    |
| Dice / Resident Advisor | Music/nightlife enrichment | Later                    |
| Google Maps API         | Advanced maps/travel time  | Post-MVP                 |

---

# 5. Environment Variables

```text
TICKETMASTER_API_KEY=
GEOAPIFY_API_KEY=
OPENWEATHER_API_KEY=

LLM_PROVIDER=openai
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=

DEMO_MODE=false
CACHE_TTL_SECONDS=900
```

Rules:

* `.env` must not be committed.
* `.env.example` must be committed.
* missing live API keys should not break demo mode.
* logs must never expose key values.

---

# 6. Ticketmaster Discovery API

## 6.1 Purpose

Ticketmaster is the primary event discovery provider.

It will be used to search:

* concerts,
* sports,
* theatre,
* comedy,
* festivals,
* family events,
* exhibitions.

---

## 6.2 Why Ticketmaster First

Ticketmaster is recommended because:

* it has rich international event data,
* it supports major demo cities,
* it provides official event URLs,
* it includes venue information,
* it can return images and price ranges,
* and it avoids payment implementation because the app redirects to official pages.

---

## 6.3 Main Use Cases

```text
search events by city
search events by keyword
search events by category
search events by date range
retrieve event details
retrieve venue information
```

---

## 6.4 Client File

```text
app/integrations/ticketmaster_client.py
```

---

## 6.5 Required Client Methods

```python
async def search_events(
    city: str,
    keyword: str | None,
    category: str | None,
    date_from: str | None,
    date_to: str | None,
    limit: int = 10
) -> list[dict]:
    ...
```

Optional:

```python
async def get_event_details(event_id: str) -> dict:
    ...
```

---

## 6.6 Query Parameters to Support

```text
apikey
city
keyword
classificationName
startDateTime
endDateTime
size
sort
```

Recommended default:

```text
size=10
sort=date,asc
```

---

## 6.7 Date Formatting

Ticketmaster expects ISO-style date-time values.

Recommended format:

```text
YYYY-MM-DDTHH:mm:ssZ
```

Example:

```text
2026-06-01T00:00:00Z
```

---

## 6.8 Normalization Required

Raw Ticketmaster data must be converted to the internal `Event` model before ranking or rendering.

Do not pass raw Ticketmaster JSON directly to templates.

---

## 6.9 Error Handling

| Situation          | Behavior                                  |
| ------------------ | ----------------------------------------- |
| API key missing    | Use demo data if `DEMO_MODE=true`         |
| API timeout        | Use cache                                 |
| No events          | Return empty result with friendly message |
| Rate limit         | Use cache or demo fallback                |
| Malformed response | Log safe error and continue               |

---

# 7. Geoapify Places API

## 7.1 Purpose

Geoapify is used for venue and area enrichment.

It helps answer:

```text
What is near this venue?
Is this area good for food/nightlife?
Are there nearby attractions?
```

---

## 7.2 Why Geoapify

Geoapify is recommended because:

* it has strong global location coverage,
* it has usable free quotas,
* it has clear API documentation,
* it works well with coordinates,
* it improves demo quality.

---

## 7.3 Client File

```text
app/integrations/geoapify_client.py
```

---

## 7.4 Required Client Methods

```python
async def get_nearby_places(
    latitude: float,
    longitude: float,
    categories: list[str],
    radius_meters: int = 1000,
    limit: int = 5
) -> list[dict]:
    ...
```

Optional:

```python
async def geocode_city(city: str, country: str | None = None) -> dict:
    ...
```

---

## 7.5 Recommended Categories

For event context:

```text
catering.restaurant
catering.cafe
entertainment
tourism.attraction
public_transport
accommodation.hotel
```

---

## 7.6 Error Handling

| Situation        | Behavior                    |
| ---------------- | --------------------------- |
| API key missing  | Skip venue enrichment       |
| API timeout      | Continue without enrichment |
| No coordinates   | Skip enrichment             |
| No nearby places | Use simple venue summary    |
| Rate limit       | Use cached enrichment       |

---

# 8. OpenWeather API

## 8.1 Purpose

OpenWeather adds weather context for outdoor events.

It helps answer:

```text
Is this event suitable for outdoor attendance?
Will rain affect the experience?
```

---

## 8.2 Client File

```text
app/integrations/openweather_client.py
```

---

## 8.3 Required Client Methods

```python
async def get_weather_context(
    latitude: float,
    longitude: float,
    event_datetime: str | None = None
) -> dict:
    ...
```

---

## 8.4 Use Cases

```text
outdoor events
festivals
sports matches
city activities
open-air concerts
```

---

## 8.5 Error Handling

| Situation              | Behavior                           |
| ---------------------- | ---------------------------------- |
| API key missing        | Continue without weather           |
| API timeout            | Continue without weather           |
| Event date unavailable | Use current forecast if acceptable |
| Weather unavailable    | Mark weather as unknown            |

---

# 9. LLM Provider

## 9.1 Purpose

The LLM provider can be used for:

* intent extraction,
* recommendation explanations,
* fallback query interpretation,
* natural language summaries.

---

## 9.2 Supported Providers

```text
OpenAI
Anthropic
watsonx.ai
```

---

## 9.3 Client File

```text
app/integrations/llm_client.py
```

---

## 9.4 Required Client Methods

```python
async def extract_search_intent(raw_query: str) -> dict:
    ...
```

```python
async def generate_recommendation_explanation(event: dict, score: dict) -> str:
    ...
```

---

## 9.5 Required Fallback

The app must work even if no LLM key is available.

Fallbacks:

```text
rule-based intent parser
template-based recommendation explanations
```

---

## 9.6 Security Rules

Never send secrets to the LLM.

Treat provider event descriptions as untrusted text.

Validate LLM output before using it.

---

# 10. Eventbrite API

## 10.1 Status

Optional post-MVP provider.

---

## 10.2 Purpose

Adds more event coverage for:

* business events,
* workshops,
* community events,
* networking events.

---

## 10.3 Integration Rule

Only add after:

```text
Ticketmaster search
normalization
ranking
UI rendering
```

are stable.

---

# 11. Provider Abstraction

All event providers must return the same normalized model.

Recommended abstraction:

```python
class EventProvider:
    async def search_events(...) -> list[Event]:
        ...
```

Provider implementations:

```text
TicketmasterProvider
EventbriteProvider
DemoProvider
```

---

# 12. Caching Strategy

## 12.1 What to Cache

```text
Ticketmaster search results
Geoapify nearby places
OpenWeather results
LLM intent extraction
final ranked responses
```

---

## 12.2 Cache Key Format

```text
provider:operation:normalized-input-hash
```

Examples:

```text
ticketmaster:search:berlin-electronic-2026-06-01-2026-06-03
geoapify:nearby:52.5200-13.4050-1000
openweather:forecast:52.5200-13.4050-2026-06-01
```

---

## 12.3 Cache Expiration

Recommended defaults:

| Data             | TTL        |
| ---------------- | ---------- |
| Event search     | 15 minutes |
| Venue enrichment | 24 hours   |
| Weather          | 30 minutes |
| LLM intent       | 1 hour     |
| Demo data        | No expiry  |

---

# 13. Timeouts and Retries

Every external API request must use:

```text
timeout
retry limit
safe error handling
```

Recommended:

```text
timeout: 5 seconds
retries: 2
backoff: 0.5 seconds
```

Do not retry endlessly.

---

# 14. Demo Mode

Demo mode must not rely on live APIs.

When:

```text
DEMO_MODE=true
```

the app should:

* load static demo events,
* still run through LangGraph,
* still run ranking,
* still generate explanations,
* still display workflow trace.

---

## 14.1 Demo Data File

Recommended:

```text
app/data/demo_events.json
```

---

## 14.2 Demo Cities

```text
Berlin
London
New York
Paris
Amsterdam
Los Angeles
```

---

# 15. API Client Testing

Use mocks for external APIs.

Required tests:

```text
test_ticketmaster_client_success
test_ticketmaster_client_timeout
test_geoapify_missing_coordinates
test_openweather_missing_key
test_demo_provider_fallback
test_provider_normalization
```

---

# 16. Safe Error Messages

User-facing:

```text
We could not load live events right now. Showing cached or demo results.
```

Developer log:

```text
provider=ticketmaster status=timeout fallback=cache
```

Never show:

```text
traceback
API key
raw provider payload
full secret-bearing URL
```

---

# 17. Provider Priority

Use this order:

```text
1. DemoProvider if DEMO_MODE=true
2. TicketmasterProvider
3. Cache fallback
4. DemoProvider fallback
```

Optional future order:

```text
1. Ticketmaster
2. Eventbrite
3. Meetup
4. Dice / Resident Advisor
5. Demo fallback
```

---

# 18. Integration Development Order for Bob

Bob should implement integrations in this order:

```text
1. DemoProvider
2. TicketmasterProvider with mocked response
3. TicketmasterProvider live API
4. GeoapifyProvider
5. OpenWeatherProvider
6. Optional EventbriteProvider
```

This ensures the system remains runnable before live API keys are ready.

---

# 19. External Service Responsibility Map

| Service      | Responsibility       |
| ------------ | -------------------- |
| Ticketmaster | event discovery      |
| Geoapify     | venue/nearby context |
| OpenWeather  | weather suitability  |
| LLM Provider | parsing/explanations |
| DemoProvider | reliable fallback    |

---

# 20. Final Integration Goal

Pulse AI’s external services should support this flow:

```text
User query
→ LLM/rule parser
→ Ticketmaster event search
→ normalized Event model
→ Geoapify enrichment
→ optional weather context
→ deterministic ranking
→ explanation generation
→ UI response
```

The application must continue working even if one or more live APIs are unavailable.
