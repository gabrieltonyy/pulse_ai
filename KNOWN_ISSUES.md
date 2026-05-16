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

---

## Resolved Issues

### 1. Alembic Async Driver Configuration ✅ FIXED
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

### 2. Database Credentials Mismatch ✅ FIXED
**Issue:** Alembic migrations failing with password authentication error for user "postgres"

**Root Cause:**
- `.env` file had `postgres:postgres@localhost:5433`
- `docker-compose.yml` created database with `pulse_user:pulse_password`
- Credentials didn't match

**Fix:**
- Updated `.env` to use `pulse_user:pulse_password@localhost:5433` matching docker-compose.yml
- Migrations now connect successfully

**Date Fixed:** 2026-05-16

### 3. Docker Compose Version Attribute ✅ FIXED
**Issue:** Docker Compose showing deprecation warning for `version` attribute

**Fix:**
- Removed `version: '3.8'` from docker-compose.yml (line 1)
- Modern Docker Compose doesn't require version specification

**Date Fixed:** 2026-05-16

---

## Future Considerations

### Dependency Conflicts
- SQLAlchemy version must be <2.0.36 for langchain-community compatibility
- Monitor for updates to langchain packages

### API Rate Limits
- Ticketmaster: 5000 requests/day
- Geoapify: Depends on plan
- OpenWeather: 1000 requests/day (free tier)
- Need to implement proper rate limiting and caching

### Performance
- Multiple external API calls per search
- Need to optimize with parallel requests
- Consider caching strategy

### Testing
- Need to mock external APIs for tests
- Demo mode data needs to be comprehensive
- Integration tests require test database

---

## Notes

This file will be updated as issues are discovered during implementation.