# Pulse AI — Technical Architecture Document

## 1. Architecture Goal

Pulse AI will be built as a **Python-first, LangGraph-powered AI event discovery platform**.

The system will use LangGraph from the start to coordinate the main AI workflow:

```text
understand request → search events → enrich context → rank → explain → save/export → redirect
```

The architecture must support:

* conversational event discovery
* LangGraph orchestration
* MCP-style tool integration
* external event APIs
* explainable event ranking
* ticket provider redirection
* calendar export
* reliable hackathon demo execution

Important rule:

```text
Do not use React.
Do not use npm.
Do not use Node-based frontend build tooling.
```

---

## 2. Recommended Stack

| Layer       | Technology                                       |
| ----------- | ------------------------------------------------ |
| Backend     | Python 3.12+, FastAPI                            |
| Frontend    | Jinja2 templates, HTMX, vanilla JavaScript       |
| Styling     | Vanilla CSS                                      |
| AI Workflow | LangGraph                                        |
| LLM Layer   | OpenAI / Claude / watsonx.ai                     |
| MCP Layer   | Python MCP SDK / FastMCP                         |
| Database    | SQLite for MVP                                   |
| Cache       | SQLite cache table or in-memory TTL cache        |
| Testing     | pytest, Playwright Python                        |
| Deployment  | Docker, Render/Railway/VPS/IBM Cloud Code Engine |

---

## 3. High-Level Architecture

```text
User Browser
   ↓
FastAPI Web App
   ↓
Jinja2 + HTMX UI
   ↓
LangGraph AI Workflow
   ↓
Agent Nodes
   ↓
MCP Tool Layer
   ↓
External APIs
```

Expanded:

```text
┌──────────────────────────────────────┐
│ User Browser                         │
│ - Search form                        │
│ - Event cards                        │
│ - AI explanations                    │
│ - Save/export actions                │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ FastAPI Application                  │
│ - Web routes                         │
│ - HTMX partial responses             │
│ - Session handling                   │
│ - Error handling                     │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ LangGraph Workflow Engine            │
│ - StateGraph                         │
│ - Conditional routing                │
│ - Agent node execution               │
│ - Tool calling                       │
│ - Workflow state management          │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ MCP / Tool Layer                     │
│ - Event search tool                  │
│ - Venue enrichment tool              │
│ - Weather tool                       │
│ - Ranking tool                       │
│ - Calendar export tool               │
│ - Ticket redirect tool               │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ External APIs                        │
│ - Ticketmaster Discovery API         │
│ - Geoapify Places API                │
│ - OpenWeather API                    │
│ - Optional Eventbrite / Meetup       │
└──────────────────────────────────────┘
```

---

## 4. Core Architectural Principle

The system should be built around a LangGraph state machine.

Instead of writing one large service function, the workflow should be broken into clear nodes:

```text
parse_query_node
search_events_node
enrich_events_node
weather_context_node
rank_events_node
generate_explanations_node
prepare_response_node
```

Each node should:

* receive shared workflow state
* perform one focused responsibility
* update the state
* pass control to the next node

---

## 5. LangGraph Workflow Design

## 5.1 Workflow State

The central workflow state should carry all information across nodes.

Example state fields:

```text
PulseGraphState
- raw_query
- parsed_intent
- city
- country
- category
- date_from
- date_to
- budget_max
- currency
- preferences
- events_raw
- events_normalized
- enriched_events
- ranked_events
- recommendation_summary
- errors
- fallback_used
```

---

## 5.2 Main Graph Flow

```text
START
  ↓
parse_query_node
  ↓
validate_query_node
  ↓
search_events_node
  ↓
normalize_events_node
  ↓
enrich_venues_node
  ↓
weather_context_node
  ↓
rank_events_node
  ↓
generate_explanations_node
  ↓
prepare_response_node
  ↓
END
```

---

## 5.3 Conditional Routing

LangGraph should handle decision points.

Examples:

```text
If city is missing:
  → clarification_node

If event API fails:
  → fallback_cache_node

If no events found:
  → broaden_search_node

If outdoor events exist:
  → weather_context_node

If user asks for planning:
  → itinerary_node
```

---

## 5.4 Recommended Graph Diagram

```text
                    ┌────────────────────┐
                    │ START              │
                    └─────────┬──────────┘
                              ▼
                    ┌────────────────────┐
                    │ Parse Query         │
                    └─────────┬──────────┘
                              ▼
                    ┌────────────────────┐
                    │ Validate Intent     │
                    └──────┬───────┬─────┘
                           │       │
                    valid  │       │ missing fields
                           ▼       ▼
              ┌────────────────┐  ┌────────────────────┐
              │ Search Events   │  │ Clarification Node │
              └───────┬────────┘  └────────────────────┘
                      ▼
              ┌────────────────┐
              │ Normalize Data  │
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ Enrich Venues   │
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ Weather Context │
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ Rank Events     │
              └───────┬────────┘
                      ▼
              ┌──────────────────────┐
              │ Generate Explanation │
              └───────┬──────────────┘
                      ▼
              ┌────────────────┐
              │ Prepare Response│
              └───────┬────────┘
                      ▼
                    ┌─────┐
                    │ END │
                    └─────┘
```

---

## 6. FastAPI Application Layer

FastAPI is responsible for:

* serving HTML pages
* receiving search requests
* calling the LangGraph workflow
* returning HTMX partials
* managing saved events
* exporting calendar files
* handling ticket redirects
* serving static assets

Suggested routes:

```text
GET  /
POST /search
GET  /events/{event_id}
POST /events/{event_id}/save
GET  /events/{event_id}/calendar.ics
GET  /redirect/{event_id}
GET  /health
```

---

## 7. Frontend Architecture

Frontend must remain simple and Python-friendly.

Use:

```text
Jinja2 + HTMX + vanilla JavaScript + vanilla CSS
```

No React, no npm, no frontend build process.

Frontend responsibilities:

* display search input
* show loading indicators
* render results from HTMX partials
* display ranked event cards
* display “why recommended” explanations
* provide save/export/ticket actions

Suggested folders:

```text
app/templates/
  base.html
  index.html
  partials/
    event_results.html
    event_card.html
    empty_state.html
    error.html

app/static/
  css/
    styles.css
  js/
    app.js
```

---

## 8. MCP / Tool Layer Architecture

The MCP layer should expose reusable tools used by LangGraph nodes.

For MVP, the tool layer can first be implemented as Python functions and exposed through FastMCP as the project matures.

Recommended tools:

| Tool Name                      | Purpose                                |
| ------------------------------ | -------------------------------------- |
| pulse_search_events            | Search Ticketmaster or other providers |
| pulse_enrich_venue             | Add venue/location context             |
| pulse_get_weather_context      | Add weather information                |
| pulse_rank_events              | Rank normalized events                 |
| pulse_create_calendar_file     | Generate `.ics` calendar file          |
| pulse_generate_ticket_redirect | Create safe outbound provider link     |

---

## 9. External API Integration Layer

External API clients should be isolated from business logic.

Suggested structure:

```text
app/integrations/
  ticketmaster_client.py
  geoapify_client.py
  openweather_client.py
```

Each client should:

* use async HTTP calls
* read secrets from environment variables
* normalize provider-specific responses
* handle failures gracefully
* support retries
* avoid logging API keys

---

## 10. LangGraph Node Responsibilities

## 10.1 Parse Query Node

Responsible for extracting:

* city
* country
* category
* date range
* budget
* currency
* preferences

Fallback should use deterministic parsing if LLM is unavailable.

---

## 10.2 Validate Query Node

Checks whether enough information exists to search.

Required fields:

```text
city
date range or default date range
category or keyword
```

If missing:

```text
route to clarification_node
```

---

## 10.3 Search Events Node

Calls:

```text
pulse_search_events
```

Primary provider:

```text
Ticketmaster Discovery API
```

Optional providers:

```text
Eventbrite
Meetup
Dice
Resident Advisor
```

---

## 10.4 Normalize Events Node

Converts provider response into internal event schema.

This prevents the UI and ranking logic from depending on provider-specific fields.

---

## 10.5 Enrich Venues Node

Calls:

```text
pulse_enrich_venue
```

Adds:

* coordinates
* nearby restaurants
* nearby attractions
* local area context
* travel-related metadata

---

## 10.6 Weather Context Node

Calls:

```text
pulse_get_weather_context
```

Adds:

* forecast
* indoor/outdoor suitability
* rain risk
* temperature context

Can be skipped if:

* event is indoor
* weather API key is unavailable
* no date is available

---

## 10.7 Rank Events Node

Calls:

```text
pulse_rank_events
```

Uses deterministic scoring.

Ranking dimensions:

```text
relevance_score
date_match_score
affordability_score
popularity_score
venue_context_score
weather_score
```

---

## 10.8 Generate Explanations Node

Creates short explanations for recommendations.

Example:

```text
Recommended because it matches your electronic music preference,
is within your budget, happens this weekend, and is hosted at a popular venue.
```

---

## 10.9 Prepare Response Node

Formats final output for:

* HTMX partial rendering
* JSON API response
* saved event workflow

---

## 11. Data Layer

Use SQLite for MVP.

Tables:

```text
saved_events
search_history
api_cache
outbound_clicks
```

---

## 12. Data Models

## 12.1 Event

```text
Event
- id
- title
- description
- category
- venue_name
- venue_city
- venue_country
- latitude
- longitude
- start_datetime
- end_datetime
- price_min
- price_max
- currency
- provider
- provider_event_url
- image_url
- popularity_score
```

---

## 12.2 Recommendation

```text
Recommendation
- event_id
- total_score
- relevance_score
- affordability_score
- popularity_score
- context_score
- weather_score
- explanation
```

---

## 12.3 Search Intent

```text
SearchIntent
- raw_query
- city
- country
- category
- date_from
- date_to
- budget_max
- currency
- preferences
```

---

## 13. Ranking Formula

Use deterministic scoring for transparency.

```text
total_score =
  relevance_score * 0.35 +
  date_match_score * 0.20 +
  affordability_score * 0.20 +
  popularity_score * 0.15 +
  context_score * 0.10
```

If weather is used:

```text
total_score =
  relevance_score * 0.30 +
  date_match_score * 0.20 +
  affordability_score * 0.20 +
  popularity_score * 0.15 +
  context_score * 0.10 +
  weather_score * 0.05
```

---

## 14. Caching Strategy

Caching is required for demo reliability.

Cache:

* event API responses
* venue enrichment results
* weather results
* final ranked responses

Cache keys:

```text
city + category + date_range + budget
```

Benefits:

* faster repeated demos
* fewer rate-limit issues
* fallback if an API fails

---

## 15. Error Handling Strategy

| Situation                | System Behavior               |
| ------------------------ | ----------------------------- |
| Missing city             | Ask clarification             |
| No results               | Broaden search suggestion     |
| API timeout              | Use cache or fallback data    |
| Missing API key          | Show setup warning            |
| LLM failure              | Use deterministic parser      |
| Weather API failure      | Continue without weather      |
| Venue enrichment failure | Continue with base event data |

---

## 16. Security Architecture

Security requirements:

* keep secrets in `.env`
* commit only `.env.example`
* do not log credentials
* sanitize user input
* validate outbound ticket URLs
* rate-limit search requests
* avoid storing personal data
* avoid payment processing
* avoid scraping protected sites

---

## 17. Testing Architecture

Use Python-only tooling.

Testing stack:

```text
pytest
httpx AsyncClient
Playwright Python
```

Test areas:

```text
Unit tests:
- parse query node
- ranking node
- calendar export
- normalization

Integration tests:
- FastAPI routes
- API client mocks
- LangGraph workflow

Browser tests:
- search form
- event cards
- redirect links
```

No npm-based tests.

---

## 18. Recommended Project Structure

```text
pulse-ai/
  app/
    main.py
    config.py
    dependencies.py

    routes/
      web.py
      health.py
      events.py

    graph/
      state.py
      workflow.py
      nodes/
        parse_query.py
        validate_query.py
        search_events.py
        normalize_events.py
        enrich_venues.py
        weather_context.py
        rank_events.py
        generate_explanations.py
        prepare_response.py

    tools/
      event_tools.py
      location_tools.py
      weather_tools.py
      ranking_tools.py
      calendar_tools.py
      redirect_tools.py

    mcp/
      server.py

    integrations/
      ticketmaster_client.py
      geoapify_client.py
      openweather_client.py

    services/
      calendar_service.py
      cache_service.py
      event_service.py

    models/
      event.py
      search.py
      recommendation.py

    db/
      database.py
      schema.sql
      repositories.py

    templates/
      base.html
      index.html
      partials/
        event_results.html
        event_card.html
        empty_state.html
        error.html

    static/
      css/
        styles.css
      js/
        app.js

  tests/
    test_graph_workflow.py
    test_parse_query_node.py
    test_ranking_node.py
    test_calendar_service.py
    test_web_routes.py

  docs/
    01-project-brief.md
    02-product-requirements.md
    03-technical-architecture.md

  bob_sessions/

  .env.example
  .gitignore
  Dockerfile
  docker-compose.yml
  requirements.txt
  README.md
  AGENTS.md
```

---

## 19. Environment Variables

```text
APP_NAME=Pulse AI
APP_ENV=development
DEBUG=true

SECRET_KEY=change_me
DATABASE_URL=sqlite:///./pulse_ai.db

TICKETMASTER_API_KEY=
GEOAPIFY_API_KEY=
OPENWEATHER_API_KEY=

LLM_PROVIDER=openai
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=

CACHE_TTL_SECONDS=900
```

---

## 20. LangGraph Implementation Notes for Bob

Bob should implement the LangGraph workflow from the start.

Initial implementation order:

```text
1. Define PulseGraphState
2. Implement parse_query_node
3. Implement search_events_node with mocked data
4. Implement normalize_events_node
5. Implement rank_events_node
6. Implement prepare_response_node
7. Wire StateGraph
8. Connect FastAPI /search route
9. Add real Ticketmaster integration
10. Add enrichment and weather nodes
```

This allows incremental development while keeping LangGraph as the core architecture.

---

## 21. Demo Mode Architecture

Add a demo mode to avoid live API failure during presentation.

```text
DEMO_MODE=true
```

When enabled:

* use cached event responses
* avoid live API dependence
* still run LangGraph nodes
* still show MCP/tool orchestration
* still render realistic event cards

---

## 22. Bob Development Usage

Bob should be used to:

* create `AGENTS.md`
* scaffold the LangGraph workflow
* generate node files
* create API clients
* implement MCP tools
* generate tests
* refactor code
* write documentation
* review security

Required folder:

```text
bob_sessions/
```

---

## 23. Architecture Decision Summary

| Decision              | Reason                                     |
| --------------------- | ------------------------------------------ |
| LangGraph from start  | Makes orchestration visible and structured |
| FastAPI               | Python-native and simple                   |
| Jinja2 + HTMX         | No React/npm required                      |
| SQLite                | Fast hackathon setup                       |
| MCP Python SDK        | Python-first MCP implementation            |
| Ticketmaster first    | Rich international event data              |
| Geoapify              | Reliable international location context    |
| OpenWeather optional  | Useful event-day context                   |
| No payment processing | Keeps scope safe                           |
| Demo mode             | Protects final presentation                |
| Calendar export       | Strong demo value                          |

---

## 24. Final Architecture Vision

Pulse AI should be a clean, modular, LangGraph-powered application where:

* FastAPI handles web traffic,
* Jinja2 and HTMX provide a lightweight UI,
* LangGraph controls the AI workflow,
* MCP tools expose reusable capabilities,
* API integrations provide event/location/weather data,
* ranking logic explains recommendations,
* and Bob accelerates the development process from architecture to implementation.
