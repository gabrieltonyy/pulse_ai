# Pulse AI — Known Issues

**Purpose:** Track bugs, blockers, and unresolved issues.

---

## Current Issues

### 1. watsonx.ai Model Deprecation ⚠️ WARNING
**Issue:** The working model `ibm/granite-8b-code-instruct` is deprecated and will be withdrawn on 2026-08-08.

**Status:** Using deprecated model temporarily
- Model works correctly for text generation
- Deprecated since 2026-05-05
- Will be withdrawn on 2026-08-08
- Alternative models tested but don't support text generation function:
  - `ibm/granite-3-1-8b-base` - base model, no text generation
  - `meta-llama/llama-3-1-8b` - doesn't support text generation
  - `mistral-large-2512` - doesn't support text generation (also deprecated)
  - Restricted models (cannot use): llama-3-405b-instruct, mistral-medium-2505, mistral-small-3-1-24b-instruct-2503

**Recommendation:**
- Continue using `ibm/granite-8b-code-instruct` for hackathon (works until August)
- Monitor for new instruct models that support text generation
- Implement fallback to deterministic parser if model becomes unavailable

**Date Identified:** 2026-05-16

### 2. Full Regression Suite Not Re-run After Hardening Changes ⚠️ ACTION NEEDED
**Issue:** Stages 1-8 changed security, FastAPI wiring, repository/session handling, logging, LangGraph state returns, API caching, rate limiting, MCP tools, and container commands. Targeted syntax checks passed, but the full test suite has not been re-run in this chat.

**Status:** Pending verification
- `python -m py_compile` passed for touched Python files during each stage
- Stage 5 state-mutation scan passed for all 9 graph nodes
- Stage 6 `git diff --check` passed for caching changes
- Stage 7/8 syntax checks passed for touched Python files
- Runtime imports may require installing missing dependencies in the active environment, including newly added `slowapi`

**Recommendation:**
- Run `./run_tests.sh` or `pytest tests/ -v` in a fully provisioned environment before release
- Include cache-hit/cache-miss and rate-limit coverage for Ticketmaster/OpenWeather/search/event paths when adding tests

**Date Identified:** 2026-05-19

---

## Resolved Issues

### Missing Application Rate Limiting ✅ FIXED
**Issue:** Public API endpoints had provider-level retry/rate-limit handling but no application-level request throttling.

**Fix:**
- Added `slowapi>=0.1.9`
- Added shared `Limiter(key_func=get_remote_address)` in `app/rate_limit.py`
- Registered `SlowAPIMiddleware` and stored the limiter on `app.state.limiter`
- Applied limits:
  - Search JSON/HTMX: `20/minute`
  - Event detail/calendar: `60/minute`
  - Click tracking: `120/minute`

**Date Fixed:** 2026-05-19

### MCP Tool Workflow and Error Response Polish ✅ FIXED
**Issue:** `pulse_search_events` did not directly call the singleton `get_workflow()`, and venue/weather MCP tools lacked logging and consistent `success: false` error responses.

**Fix:**
- Updated `pulse_search_events.py` to call `get_workflow()`
- Added logging to `pulse_enrich_venue.py` and `pulse_get_weather.py`
- Standardized failure responses to include `{"success": False, "error": ...}`
- Preserved demo-mode success responses for venue/weather tools

**Date Fixed:** 2026-05-19

### Production Container Command Needed Hardening ✅ FIXED
**Issue:** The production Docker command needed explicit non-reload Uvicorn settings and a clear worker-count note. The dev compose command intentionally still uses `--reload`.

**Fix:**
- Updated `Dockerfile` CMD to run `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1`
- Added a Dockerfile note that worker count should be increased through production deployment settings
- Added comments to `docker-compose.yml` marking it as development-only and documenting that `--reload` is local-only

**Date Fixed:** 2026-05-19

### P0 Security and Error Leakage Risks ✅ FIXED
**Issue:** Several API paths exposed implementation details or accepted overly broad input.

**Fix:**
- Replaced unsafe `str(exc)` response details with generic user-facing messages
- Prevented HTMX error HTML from reflecting exception text
- Added HTMX query length validation
- Required `SECRET_KEY` and rejected the insecure placeholder value
- Added regex validation for `event_id` path parameters
- Removed markdown fences from `.env.example`

**Date Fixed:** 2026-05-19

### Deprecated FastAPI Startup/Shutdown Wiring ✅ FIXED
**Issue:** The app used deprecated `@app.on_event("startup")` and `@app.on_event("shutdown")` hooks, and the LangGraph workflow was compiled per request.

**Fix:**
- Added FastAPI lifespan context manager
- Compiled workflow once at startup with `get_workflow()`
- Stored compiled workflow on `app.state.workflow`
- Updated search routes to use `request.app.state.workflow`
- Added `reset_workflow()` for tests

**Date Fixed:** 2026-05-19

### EventRepository Optional Session Pattern ✅ FIXED
**Issue:** `EventRepository` previously supported no-session construction and fallback session lookup, which was fragile and caused runtime risk.

**Fix:**
- `EventRepository` now requires `AsyncSession`
- Event routes use `Depends(get_db)` and instantiate `EventRepository(session=db)`
- Graph nodes use the new `get_session_context()` context manager when direct DB access is needed

**Date Fixed:** 2026-05-19

### Inconsistent LangGraph State Mutation ✅ FIXED
**Issue:** Some graph nodes mutated the incoming state object while others returned a fresh state dict.

**Fix:**
- Audited all 9 graph nodes
- Standardized mutation-heavy nodes to return `{**state, ...}`
- Ensured `workflow_trace` is always extended from existing trace
- Copied nested event/recommendation dictionaries before adding weather context or explanations

**Date Fixed:** 2026-05-19

### API Cache Table Was Unused in Main Pipeline ✅ FIXED
**Issue:** `ApiCacheRepository`, TTL settings, and `api_cache` table existed but were not wired into the workflow.

**Fix:**
- Ticketmaster search results now cache by hashed search parameter payload
- OpenWeather raw responses now cache by hashed latitude/longitude/date payload
- Cache failures are non-blocking

**Date Fixed:** 2026-05-19

### Alembic Async Driver Configuration ✅ FIXED
**Issue:** Alembic was trying to use psycopg2 (sync driver) with async engine, causing error:
```
The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
```

**Root Cause:**
- `app/db/migrations/env.py` was using `settings.database_url_sync` which returns a psycopg2 URL
- This was then passed to `async_engine_from_config` which requires asyncpg

**Fix:**
- Updated `env.py` line 30 and 75 to use `settings.database_url` (asyncpg) instead of `settings.database_url_sync`
- Migrations now run successfully with async driver

**Date Fixed:** 2026-05-16

### Database Credentials Mismatch ✅ FIXED
**Issue:** Alembic migrations failing with password authentication error for user "postgres"

**Root Cause:**
- `.env` file had `postgres:postgres@localhost:5433`
- `docker-compose.yml` created database with `pulse_user:pulse_password`
- Credentials didn't match

**Fix:**
- Updated `.env` to use `pulse_user:pulse_password@localhost:5433` matching docker-compose.yml
- Migrations now connect successfully

**Date Fixed:** 2026-05-16

### Docker Compose Version Attribute ✅ FIXED
**Issue:** Docker Compose showing deprecation warning for `version` attribute

**Fix:**
- Removed `version: '3.8'` from docker-compose.yml (line 1)
- Modern Docker Compose doesn't require version specification

**Date Fixed:** 2026-05-16

---

## Phase 6 Testing Results

### Test Suite Status ✅
- **Total Tests:** 50+ tests across 6 test files
- **Passing:** All critical tests passing
- **Coverage:** >70% of app/ directory
- **Performance:** All performance benchmarks met

### Test Categories
1. **Unit Tests (test_ranking_service.py):** 20/20 passing
2. **API Connection Tests (test_api_connections.py):** 8/8 passing
3. **Integration Tests (test_workflow_integration.py):** 3/3 passing
4. **API Route Tests (test_api_routes.py):** 8/8 passing
5. **MCP Tool Tests (test_mcp_tools.py):** 8/8 passing
6. **Performance Tests (test_performance.py):** 5/5 passing

### Known Test Limitations
- E2E tests are placeholders (require Playwright MCP server)
- Some tests skip slow operations with markers
- Live API tests may fail without valid API keys (gracefully handled)

---

## Future Considerations

### Dependency Conflicts
- SQLAlchemy version must be <2.0.36 for langchain-community compatibility
- Monitor for updates to langchain packages

### API Rate Limits
- Ticketmaster: 5000 requests/day
- Geoapify: Depends on plan
- OpenWeather: 1000 requests/day (free tier)
- Proper provider rate-limit handling implemented with retry logic
- Application-level SlowAPI limits now protect search/event routes
- DB-backed caching now active in the main graph for Ticketmaster event searches and OpenWeather responses
- Geoapify client still relies on retry/rate-limit handling; no graph-node cache is currently wired for venue enrichment

### Performance
- Multiple external API calls per search (optimized with async)
- Parallel requests implemented where possible
- Demo mode provides instant responses
- Performance benchmarks:
  - Workflow completion: <5s (demo mode)
  - Ranking 100 events: <1s
  - Demo data loading: <0.1s
  - LLM parsing: <3s

### Testing
- ✅ External APIs tested with real connections
- ✅ Demo mode provides comprehensive test data
- ✅ Integration tests use demo mode by default
- ⏳ E2E tests require Playwright MCP setup

---

## Notes

This file will be updated as issues are discovered during implementation.
