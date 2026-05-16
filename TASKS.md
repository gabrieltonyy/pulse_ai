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

---

## In Progress
None currently - Phase 1 complete!

---

## Next Priority (Phase 2)
- [ ] Implement parse_query node with LLM
- [ ] Implement validate_query node
- [ ] Implement search_events node (Ticketmaster integration)
- [ ] Implement normalize_events node
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