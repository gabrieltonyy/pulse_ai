# Pulse AI — Development Tasks

## Completed - Phase 1: Foundation ✅
- [x] Project structure setup (directories created)
- [x] Requirements.txt with all dependencies
- [x] Configuration system (settings.py with Pydantic)
- [x] Database setup (PostgreSQL with SQLAlchemy 2.x + asyncpg)
- [x] Alembic configuration and initial migration
- [x] FastAPI application bootstrap (main.py)
- [x] Health check endpoint
- [x] Database models (SavedEvent, SearchHistory, APICache, OutboundClick)
- [x] LangGraph state definition (PulseGraphState)
- [x] LangGraph workflow scaffold
- [x] LangGraph node placeholders (9 nodes)
- [x] MCP server scaffold (FastMCP)
- [x] MCP tool stubs (7 tool modules)
- [x] Docker setup (Dockerfile, docker-compose.yml)
- [x] Operational files (TASKS.md, HAND_OVER.md, ARCHITECTURE_NOTES.md, KNOWN_ISSUES.md)
- [x] .gitignore and README.md
- [x] Import verification test (all modules load successfully)
- [x] **CRITICAL FIX:** Alembic async driver configuration
- [x] Docker Compose version attribute removed
- [x] Database credentials aligned (.env updated)
- [x] Alembic migrations tested successfully

## Completed - Phase 2: Core Data Models & Demo Provider ✅
- [x] **Pydantic Models (Phase 2.1)**
  - [x] SearchIntent, SearchRequest, SearchValidationResult (app/models/search.py)
  - [x] Event, EventCardViewModel (app/models/event.py)
  - [x] NearbyPlace, VenueContext (app/models/venue.py)
  - [x] WeatherContext (app/models/weather.py)
  - [x] RecommendationScore, EnrichedEvent, RankedEvent (app/models/recommendation.py)
  - [x] CalendarExportRequest, CalendarExportResult (app/models/calendar.py)
  - [x] TicketRedirectRequest, TicketRedirectResult (app/models/redirect.py)
  - [x] WorkflowTraceItem (app/models/trace.py)
  - [x] Updated app/models/__init__.py with all exports

- [x] **Demo Data Provider (Phase 2.2)**
  - [x] Created app/data/demo_events.json with 14 realistic events
  - [x] Demo cities: Berlin, London, New York, Paris, Amsterdam, Los Angeles, San Francisco
  - [x] Implemented app/services/demo_provider.py with DemoProvider class
  - [x] Support for filtering by city, category, date range, budget
  - [x] Returns normalized Event objects

- [x] **Database Repositories (Phase 2.3)**
  - [x] Created app/db/repositories.py with async repository pattern
  - [x] SavedEventsRepository (save, get, delete, exists methods)
  - [x] SearchHistoryRepository (create, get by session, get recent)
  - [x] ApiCacheRepository (set, get, delete expired, clear by tool)
  - [x] OutboundClicksRepository (record, get by event/session, count)

---

## Completed - Phase 3: Query Understanding & Validation ✅
- [x] **API Connection Testing**
  - [x] Created tests/test_api_connections.py with comprehensive API tests
  - [x] Tested watsonx.ai LLM connection (using ibm/granite-8b-code-instruct)
  - [x] Tested Ticketmaster API connection (✅ Working)
  - [x] Tested Geoapify API connection (✅ Working)
  - [x] Tested OpenWeather API connection (✅ Working)
  - [x] All 8 tests passing (4 credential checks + 4 API calls)
  - [x] Documented model deprecation in KNOWN_ISSUES.md

- [x] **LLM Service Implementation**
  - [x] Created app/services/llm_service.py with WatsonxLLM integration
  - [x] Implemented parse_query() method with watsonx.ai
  - [x] Implemented generate_explanation() method for recommendations
  - [x] Implemented deterministic fallback parser (regex-based)
  - [x] Added comprehensive error handling and retry logic
  - [x] Automatic fallback to deterministic parser on LLM failure

- [x] **API Client Implementation**
  - [x] Created app/integrations/ticketmaster_client.py
    - Search events with filters (city, category, dates, budget)
    - Get event by ID
    - Retry logic (3 attempts with exponential backoff)
    - Rate limit handling (429 status)
    - Country code mapping
  - [x] Created app/integrations/geoapify_client.py
    - Get nearby places around coordinates
    - Geocode city names to coordinates
    - Category mapping for place types
    - Retry logic and error handling
  - [x] Created app/integrations/openweather_client.py
    - Get current weather by coordinates
    - Get 5-day forecast
    - Outdoor-friendly weather detection
    - Retry logic and timeout handling

- [x] **LangGraph Nodes Updated**
  - [x] parse_query.py - Now uses watsonx.ai LLM with fallback
  - [x] validate_query.py - Validates required fields and constraints
  - [x] search_events.py - Integrated Ticketmaster API with demo fallback
  - [x] normalize_events.py - Normalizes Ticketmaster responses to Event model

---

## In Progress
None currently - Phase 3 complete!

---

## Next Priority (Phase 4)
- [ ] Implement enrich_venues node (Geoapify integration)
- [ ] Implement weather_context node (OpenWeather integration)
- [ ] Implement rank_events node
- [ ] Implement generate_explanations node
- [ ] Implement prepare_response node

---

## Phase 3 - MCP Tools Implementation
- [ ] pulse_search_events tool
- [ ] pulse_enrich_venue tool
- [ ] pulse_get_weather_context tool
- [ ] pulse_rank_events tool
- [ ] pulse_export_to_calendar tool
- [ ] pulse_get_ticket_redirect tool
- [ ] Demo mode fallback data

---

## Phase 4 - Frontend & Routes
- [ ] Create web routes
- [ ] Create search form (HTMX)
- [ ] Create results display
- [ ] Create event detail view
- [ ] Calendar export functionality
- [ ] Ticket redirect tracking

---

## Phase 5 - Testing & Polish
- [ ] Unit tests for nodes
- [ ] Integration tests for workflow
- [ ] API endpoint tests
- [ ] Demo mode testing
- [ ] Performance optimization
- [ ] Documentation updates

---

## Future Enhancements
- [ ] User preferences storage
- [ ] Event itinerary planning
- [ ] Redis caching layer
- [ ] Advanced filtering options
- [ ] Social sharing features

---

## Blockers
None currently.

---

## Notes
- Using PostgreSQL (not SQLite) per master.md requirements
- All API keys configured in .env
- watsonx.ai configured as LLM provider
- Demo mode available for testing without API calls