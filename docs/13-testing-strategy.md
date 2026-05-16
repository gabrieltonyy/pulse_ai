# Pulse AI — Testing Strategy

## 1. Purpose

This document defines how Pulse AI should be tested during development.

Bob should use this guide to generate tests incrementally while building the project.

The goal is to keep the app:

```text
stable
demo-ready
secure
easy to refactor
safe to publish
```

---

# 2. Testing Principles

Pulse AI testing should follow:

```text
test core workflow first
mock external APIs
keep tests fast
avoid fragile UI tests
test security-sensitive paths
test demo mode
```

Do not wait until the end to add tests.

---

# 3. Testing Stack

Use Python-first testing only.

```text
pytest
pytest-asyncio
httpx AsyncClient
Playwright Python
coverage.py
```

Do not use:

```text
npm
Jest
Cypress
React Testing Library
Node-based test runners
```

---

# 4. Test Categories

| Category          | Purpose                                   |
| ----------------- | ----------------------------------------- |
| Unit tests        | Test isolated logic                       |
| Integration tests | Test FastAPI + LangGraph flow             |
| API client tests  | Test external provider clients with mocks |
| Security tests    | Test input validation and safe redirects  |
| UI smoke tests    | Test core browser flow                    |
| Demo mode tests   | Ensure presentation fallback works        |

---

# 5. Priority Test Order

Bob should implement tests in this order:

```text
1. Ranking logic tests
2. LangGraph workflow tests
3. Demo provider tests
4. Ticketmaster normalization tests
5. FastAPI route tests
6. Security redirect tests
7. Calendar export tests
8. HTMX rendering tests
9. Playwright smoke tests
```

---

# 6. Unit Tests

## 6.1 Ranking Tests

File:

```text
tests/test_scoring_service.py
```

Test cases:

```text
exact category match ranks higher
event within budget gets high affordability score
free event gets maximum affordability score
missing price does not fail
missing weather does not fail
out-of-range date lowers score
best overall label is assigned correctly
ranked results are sorted descending
```

---

## 6.2 Query Parsing Tests

File:

```text
tests/test_parse_query_node.py
```

Test cases:

```text
extracts city from query
extracts category from query
extracts budget from query
extracts date phrase
defaults to upcoming weekend
handles missing category
rejects very long query
```

---

## 6.3 Calendar Export Tests

File:

```text
tests/test_calendar_service.py
```

Test cases:

```text
generates valid .ics content
sanitizes event title
sanitizes venue name
includes start datetime
includes provider URL only when safe
does not include raw HTML
```

---

# 7. LangGraph Workflow Tests

File:

```text
tests/test_graph_workflow.py
```

Test cases:

```text
graph executes with demo data
graph routes missing city to clarification
graph uses fallback when API fails
graph produces ranked events
graph appends workflow trace
graph completes without LLM key
```

Expected minimum assertion:

```text
raw query → ranked_events not empty
workflow_trace contains parse, search, rank, response
```

---

# 8. MCP Tool Tests

Files:

```text
tests/test_event_tools.py
tests/test_location_tools.py
tests/test_weather_tools.py
tests/test_redirect_tools.py
```

Test cases:

```text
pulse_search_events returns normalized events
pulse_get_demo_events works without API keys
pulse_rank_events returns sorted results
pulse_generate_ticket_redirect blocks unsafe URLs
pulse_generate_ticket_redirect allows approved domains
pulse_enrich_venue handles missing coordinates safely
```

---

# 9. External API Client Tests

External APIs must be mocked.

Do not call real APIs in automated tests.

Files:

```text
tests/test_ticketmaster_client.py
tests/test_geoapify_client.py
tests/test_openweather_client.py
```

Test cases:

```text
successful provider response maps to internal model
timeout returns safe error
rate limit returns safe error
malformed response does not crash
missing API key handled cleanly
```

Recommended approach:

```text
mock httpx.AsyncClient
use local JSON fixtures
```

Fixture folder:

```text
tests/fixtures/
  ticketmaster_search_success.json
  ticketmaster_empty_response.json
  geoapify_places_success.json
  openweather_success.json
```

---

# 10. FastAPI Route Tests

File:

```text
tests/test_web_routes.py
```

Test cases:

```text
GET / returns 200
POST /search returns event results partial
POST /search handles empty query
POST /events/{id}/save works
GET /events/{id}/calendar.ics returns text/calendar
GET /redirect/{id} validates provider URL
GET /health returns safe config status
```

---

# 11. HTMX Tests

HTMX route behavior should be tested at the response level.

Test:

```text
POST /search
```

Expected:

```text
returns HTML partial
contains event cards
contains recommendation explanation
contains workflow trace
does not return full page layout
```

Do not over-test styling.

---

# 12. Playwright Python Smoke Tests

Use Playwright Python only.

File:

```text
tests/e2e/test_demo_flow.py
```

Smoke test flow:

```text
open home page
enter demo query
submit search
wait for results
verify event cards appear
verify workflow trace exists
click Add to Calendar
verify .ics response
verify ticket link exists
```

Recommended demo query:

```text
Find electronic music events in Berlin this weekend under $100
```

---

# 13. Security Tests

File:

```text
tests/test_security.py
```

Required tests:

```text
unsafe redirect domain is blocked
javascript URL is blocked
http URL is blocked
ticketmaster.com.evil.com is blocked
raw HTML in event description is escaped
very long query is rejected
negative budget is rejected
API keys are not exposed in health response
provider errors are sanitized
```

---

# 14. Demo Mode Tests

File:

```text
tests/test_demo_mode.py
```

Test cases:

```text
DEMO_MODE=true uses demo provider
demo mode does not require API keys
demo mode still runs LangGraph
demo results are ranked
demo results render in UI
fallback notice appears when appropriate
```

---

# 15. Regression Tests

Every time Bob fixes a bug, it should add or update a test.

Example:

```text
Bug: unsafe redirect allowed fake-ticketmaster.com
Fix: validate host exactly
Test: fake-ticketmaster.com is blocked
```

---

# 16. Test Data Strategy

Use international demo examples.

Preferred test cities:

```text
Berlin
London
New York
Paris
Amsterdam
Los Angeles
San Francisco
```

Avoid local-only demo data for MVP.

---

# 17. Minimum Test Suite Before Demo

Before final demo, these must pass:

```text
pytest
```

Minimum passing areas:

```text
ranking tests
graph workflow tests
route tests
redirect security tests
demo mode tests
calendar export tests
```

Optional:

```text
Playwright smoke test
```

---

# 18. Coverage Target

Recommended hackathon coverage:

```text
60% minimum
75% ideal
```

Focus coverage on:

```text
ranking
graph workflow
API normalization
security
demo mode
```

Do not chase 100% coverage at the expense of finishing the demo.

---

# 19. Bob Testing Instructions

Every Bob coding task should end with:

```text
Run or update relevant tests.
Update TASKS.md.
Update HAND_OVER.md.
Record any failing tests in KNOWN_ISSUES.md.
```

Bob should not mark a task complete if:

* the app cannot start,
* the graph cannot run,
* or tests for the changed area are missing.

---

# 20. Suggested Test Commands

```bash
pytest
```

```bash
pytest tests/test_scoring_service.py
```

```bash
pytest tests/test_graph_workflow.py
```

```bash
pytest tests/test_security.py
```

For Playwright Python:

```bash
pytest tests/e2e/test_demo_flow.py
```

---

# 21. CI Recommendation

If time allows, add a simple GitHub Actions workflow.

```text
.github/workflows/tests.yml
```

Steps:

```text
checkout
setup Python
install requirements
run pytest
```

No npm setup.

---

# 22. Final Testing Goal

Pulse AI should be testable in a simple way:

```text
clone repo
create .env or enable DEMO_MODE
install Python dependencies
run pytest
start app
run demo
```

