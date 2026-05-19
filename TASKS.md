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

## Completed - Phase 4: Event Search & Normalization ✅
- [x] **Ranking Service Implementation**
  - [x] Created app/services/ranking_service.py with deterministic scoring algorithm
  - [x] Implemented relevance_score (0-100) - category, keyword, preferences matching
  - [x] Implemented date_match_score (0-100) - date range matching with fallback
  - [x] Implemented affordability_score (0-100) - budget-based scoring
  - [x] Implemented popularity_score (0-100) - metadata quality scoring
  - [x] Implemented context_score (0-100) - venue context richness
  - [x] Implemented weather_score (0-100) - outdoor suitability
  - [x] Weighted total score calculation (30% relevance, 20% date, 20% affordability, 15% popularity, 10% context, 5% weather)
  - [x] Label assignment (Best Overall, Best Budget Pick, Trending Option, Closest Match)
  - [x] Event sorting by total score descending

- [x] **LangGraph Nodes Completed**
  - [x] enrich_venues.py - Geoapify integration for nearby places
    - Fetches restaurants, entertainment, transport within 1km radius
    - Generates area summary and transport context
    - Graceful handling of missing coordinates
  - [x] weather_context.py - OpenWeather integration for forecasts
    - Adds weather context to outdoor events (Sports, Festival, Music)
    - Calculates rain probability and outdoor suitability
    - Generates weather notes for users
  - [x] rank_events.py - Ranking service integration
    - Reconstructs SearchIntent from state
    - Calls RankingService to score and sort events
    - Updates state with ranked_events
  - [x] generate_explanations.py - LLM-powered explanations
    - Uses watsonx.ai to generate personalized explanations
    - Template-based fallback for reliability
    - Explains why each event was recommended
  - [x] prepare_response.py - Final response preparation
    - Generates recommendation summary
    - Highlights special picks (budget, trending, venue)
    - Provides helpful suggestions when no results found

- [x] **Testing**
  - [x] Created tests/test_ranking_service.py with 20+ unit tests
  - [x] Tests for all scoring components
  - [x] Tests for label assignment logic
  - [x] Tests for edge cases (missing data, empty results)
  - [x] Tests for sorting and ranking behavior

---

## Completed - Phase 5: MCP Tools & Web Interface ✅
- [x] **MCP Server Implementation**
  - [x] FastMCP server with stdio transport (app/mcp/server.py)
  - [x] Tool registration system
  - [x] Integration with LangGraph workflow
  - [x] Error handling and logging
  - [x] Runnable via `python -m app.mcp.server`

- [x] **MCP Tools Implementation**
  - [x] pulse_search_events tool - Complete workflow execution
    - Accepts natural language queries
    - Returns ranked events with explanations
    - Demo mode and API fallback support
  - [x] pulse_enrich_venue tool - Venue enrichment
    - Geoapify integration for nearby places
    - Area summary and transport context generation
    - Graceful handling of missing coordinates
  - [x] pulse_get_weather tool - Weather context
    - OpenWeather integration for forecasts
    - Outdoor suitability calculation
    - Weather notes generation

- [x] **Web Routes Implementation (app/api/routes/)**
  - [x] search.py - Search interface routes
    - GET `/` - Search form with HTMX
    - POST `/search` - Execute search, return HTMX partial
  - [x] events.py - Event detail routes
    - GET `/events/{event_id}` - Event details
    - GET `/events/{event_id}/calendar` - RFC 5545 calendar export
    - POST `/events/{event_id}/track-click` - Silent-fail click tracking

- [x] **HTMX Templates (app/templates/)**
  - [x] base.html - Base layout with HTMX integration
    - Custom CSS with loading states
    - Responsive design
    - Navigation structure
  - [x] search.html - Search form
    - Natural language input
    - City, category, date range, budget filters
    - HTMX-powered submission (no page reload)
    - Loading indicators
  - [x] results.html - Results display
    - Event cards with scores and explanations
    - Venue context and weather information
    - Calendar export buttons
    - Click tracking on ticket links
    - Empty state handling

- [x] **Custom CSS (app/static/css/style.css)**
  - [x] Modern, clean design
  - [x] Loading states and animations
  - [x] Responsive grid layout
  - [x] Event card styling
  - [x] Form styling with focus states
  - [x] HTMX indicator styling

- [x] **Calendar Export Functionality**
  - [x] RFC 5545 compliant iCalendar format
  - [x] Event details, location, description included
  - [x] Proper timezone handling with VTIMEZONE
  - [x] Content-Disposition header for download

- [x] **Click Tracking Implementation**
  - [x] Silent-fail pattern (no user disruption)
  - [x] Records event_id, session_id, timestamp
  - [x] Stores in outbound_clicks table
  - [x] Returns 204 No Content on success
  - [x] Graceful error handling

**Implementation Notes:**
- MCP server uses stdio transport for Claude Desktop integration
- HTMX pattern: form submission returns partial HTML, no full page reloads
- Calendar export follows RFC 5545 specification exactly
- Click tracking uses silent-fail: errors logged but don't affect user experience
- All routes integrated with existing LangGraph workflow
- Demo mode fully supported across all tools and routes

---

## Completed - Phase 6: Testing & Integration ✅
- [x] **Integration Tests (tests/test_workflow_integration.py)**
  - [x] test_workflow_demo_mode - Complete workflow execution in demo mode
  - [x] test_workflow_with_live_apis - Workflow with live API calls
  - [x] test_workflow_error_handling - Error handling and recovery
  - [x] Verifies all 9 nodes execute correctly
  - [x] Validates ranking and scoring logic
  - [x] Tests workflow trace generation

- [x] **API Route Tests (tests/test_api_routes.py)**
  - [x] test_home_page - Home page loads correctly
  - [x] test_health_endpoint - Health check endpoint
  - [x] test_demo_search - Demo search endpoint
  - [x] test_search_endpoint - POST /api/search/ endpoint
  - [x] test_search_htmx_endpoint - HTMX search endpoint
  - [x] test_invalid_search_request - Error handling
  - [x] test_search_with_category_filter - Category filtering
  - [x] test_cors_headers - CORS configuration

- [x] **MCP Tool Tests (tests/test_mcp_tools.py)**
  - [x] test_pulse_search_events_demo - Search tool in demo mode
  - [x] test_pulse_search_events_with_category - Category filtering
  - [x] test_pulse_search_events_with_date_range - Date range filtering
  - [x] test_pulse_enrich_venue - Venue enrichment tool
  - [x] test_pulse_enrich_venue_invalid_coords - Error handling
  - [x] test_pulse_get_weather - Weather context tool
  - [x] test_pulse_get_weather_current - Current weather
  - [x] test_pulse_search_events_error_handling - Error recovery

- [x] **Performance Tests (tests/test_performance.py)**
  - [x] test_workflow_performance_demo - Workflow completes in <5s
  - [x] test_ranking_performance - Ranks 100 events in <1s
  - [x] test_demo_data_loading_performance - Demo data loads in <0.1s
  - [x] test_multiple_concurrent_workflows - 5 concurrent workflows in <10s
  - [x] test_llm_service_performance - LLM parsing in <3s

- [x] **E2E Test Placeholders (tests/test_e2e_frontend.py)**
  - [x] Created test stubs for Playwright MCP integration
  - [x] test_search_form_interaction - Form submission flow
  - [x] test_demo_link - Demo link functionality
  - [x] test_event_card_interaction - Event card interactions
  - [x] test_responsive_design - Responsive layout testing
  - [x] test_error_handling_ui - Error message display

- [x] **Test Configuration**
  - [x] Updated pytest.ini with test markers (asyncio, slow, integration, e2e)
  - [x] Created run_tests.sh script for comprehensive test execution
  - [x] Script includes coverage reporting (htmlcov/index.html)
  - [x] All test dependencies documented

- [x] **Test Results**
  - [x] Unit tests: 20/20 passing (test_ranking_service.py)
  - [x] API connection tests: 8/8 passing (test_api_connections.py)
  - [x] Integration tests: 3/3 passing (test_workflow_integration.py)
  - [x] Test coverage: >70% of app/ directory
  - [x] All critical paths tested and verified

**Test Suite Summary:**
- Total test files: 6 (unit, integration, API, MCP, performance, E2E)
- Total tests: 50+ tests across all categories
- Test execution time: ~10 minutes for full suite
- Coverage report: htmlcov/index.html
- Run command: `./run_tests.sh` or `pytest tests/ -v`

---

## Completed - Phase 7: Documentation & Polish ✅
- [x] **README.md Enhancement (7.1)**
  - [x] Comprehensive project overview with key features
  - [x] Architecture section with technology stack
  - [x] Workflow architecture diagram (9 LangGraph nodes)
  - [x] Ranking algorithm documentation (6 components)
  - [x] Quick start guide (Docker + local development)
  - [x] Demo mode documentation
  - [x] MCP tools overview
  - [x] API documentation links
  - [x] Security notes
  - [x] Bob AI Assistant usage section
  - [x] Hackathon submission highlights
  - [x] Troubleshooting guide
  - [x] Documentation index

- [x] **MCP Usage Documentation (7.2)**
  - [x] Created docs/MCP_USAGE.md
  - [x] Detailed tool documentation (pulse_search_events, pulse_enrich_venue, pulse_get_weather)
  - [x] Input/output schemas with examples
  - [x] Running MCP server instructions
  - [x] Claude Desktop configuration guide
  - [x] VSCode MCP configuration
  - [x] Testing MCP tools guide
  - [x] Troubleshooting section
  - [x] Best practices
  - [x] Complete workflow examples

- [x] **Bob Session Proof Documentation (7.3)**
  - [x] Created bob_sessions/README.md
  - [x] Session export guidelines
  - [x] Screenshot capture guidelines
  - [x] Security notes (no API keys)
  - [x] Verification checklist
  - [x] Bob's development approach documentation
  - [x] Evidence of Bob usage indicators
  - [x] Questions and resources section

- [x] **Operational Documentation Updates (7.4)**
  - [x] Updated TASKS.md with Phase 7 completion
  - [x] Updated HAND_OVER.md with Phase 7 status
  - [x] Documented all Phase 7 deliverables
  - [x] Updated project completion status (7/8 phases)

---

## Completed - Post-Phase 7 Stabilization & Hardening ✅
- [x] **Stage 1: Critical Bug Fixes & Security Hardening**
  - [x] Required `SECRET_KEY` and rejected insecure placeholder value
  - [x] Replaced unsafe exception details in API/HTMX responses
  - [x] Added HTMX query length validation
  - [x] Added `event_id` path validation
  - [x] Removed no-session `EventRepository` fallback
  - [x] Replaced deprecated UTC timestamp usage in touched paths
  - [x] Switched click counting to SQL `COUNT(*)`
  - [x] Removed duplicate `httpx` dependency entry
  - [x] Fixed `.env.example` dotenv syntax

- [x] **Stage 2: FastAPI App Wiring & Middleware**
  - [x] Replaced deprecated startup/shutdown events with lifespan function
  - [x] Added CORS middleware from `settings.cors_origins`
  - [x] Disabled docs/redoc when not in debug mode
  - [x] Compiled LangGraph once at startup and stored it on `app.state.workflow`
  - [x] Updated search routes to reuse app-state workflow
  - [x] Added `reset_workflow()` for tests

- [x] **Stage 3: Dependency Injection & Repository Cleanup**
  - [x] Event routes use `db: AsyncSession = Depends(get_db)`
  - [x] `EventRepository` consistently requires and uses injected session
  - [x] Cleaned `get_engine()` pool args for dev/test `NullPool`

- [x] **Stage 4: Logging Standardization**
  - [x] Added module loggers to LLM service, API clients, and selected graph nodes
  - [x] Replaced remaining `print()` usage
  - [x] Added API call start/success/rate-limit/failure logs
  - [x] Kept LLM fallback log redacted

- [x] **Stage 5: LangGraph State Mutation Consistency**
  - [x] Audited all 9 graph nodes
  - [x] Standardized mutation-heavy nodes to return fresh state dicts
  - [x] Ensured `workflow_trace` is extended from existing trace
  - [x] Avoided nested input-state mutation for weather context and explanations

- [x] **Stage 6: API Response Caching Integration**
  - [x] Added `get_session_context()` for graph-node DB sessions
  - [x] Wired Ticketmaster event search caching through `ApiCacheRepository`
  - [x] Wired OpenWeather response caching through `ApiCacheRepository`
  - [x] Made cache failures non-blocking
  - [x] Added cache-hit data to workflow traces

---

## In Progress
None currently - stabilization stages 1-6 have been applied locally.

---

## Next Priority
- [ ] Run full regression suite in a fully provisioned environment
- [ ] Add/adjust tests for cache-hit and cache-miss paths
- [ ] Review and commit Stage 2-6 plus documentation updates
- [ ] Continue Phase 8 planning after stabilization verification

---

## Phase 8 - Future Enhancements
- [ ] User preferences storage
- [ ] Event itinerary planning
- [ ] Redis caching layer
- [ ] Advanced filtering options
- [ ] Social sharing features
- [ ] Email notifications for saved events
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] A/B testing framework

---

## Blockers
None currently.

---

## Notes
- Using PostgreSQL (not SQLite) per master.md requirements
- All API keys configured in .env
- watsonx.ai configured as LLM provider
- Demo mode available for testing without API calls
- **Phase Progress: 7/8 phases complete, plus post-Phase 7 stabilization stages 1-6 applied** ✅
- Phase 1: Foundation ✅
- Phase 2: Core Data Models & Demo Provider ✅
- Phase 3: Query Understanding & Validation ✅
- Phase 4: Event Search & Normalization ✅
- Phase 5: MCP Tools & Web Interface ✅
- Phase 6: Testing & Integration ✅
- Phase 7: Documentation & Polish ✅
- Phase 8: Future Enhancements (Pending)
