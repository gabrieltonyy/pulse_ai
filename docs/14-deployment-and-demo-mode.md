# Pulse AI — Deployment and Demo Mode Guide

## 1. Purpose

This document defines how Pulse AI should be deployed and how demo mode should work.

Bob should use this guide when implementing:

* Docker setup,
* environment configuration,
* deployment scripts,
* demo fallback behavior,
* API fallback handling,
* and presentation-safe execution.

---

# 2. Deployment Goal

Pulse AI must be easy to run in three modes:

```text
local development
live API mode
hackathon demo mode
```

The app must remain demo-ready even if:

* external APIs fail,
* internet is unstable,
* rate limits are reached,
* or API keys are missing.

---

# 3. Deployment Principles

```text
simple setup
Python-first
no React
no npm
secure secrets
demo-safe fallback
container-ready
```

---

# 4. Supported Deployment Targets

Recommended:

```text
Render
Railway
IBM Cloud Code Engine
VPS
Docker locally
```

Avoid complex deployment platforms unless necessary.

---

# 5. Runtime Stack

```text
Python 3.12+
FastAPI
Uvicorn
Jinja2
HTMX via CDN or local static file
SQLite
LangGraph
MCP Python SDK / FastMCP
```

No Node runtime should be required.

---

# 6. Environment Modes

## 6.1 Development Mode

```text
APP_ENV=development
DEBUG=true
DEMO_MODE=false
```

Used for local coding and testing.

---

## 6.2 Live API Mode

```text
APP_ENV=production
DEBUG=false
DEMO_MODE=false
```

Uses real external APIs.

Requires:

```text
TICKETMASTER_API_KEY
GEOAPIFY_API_KEY
OPENWEATHER_API_KEY optional
```

---

## 6.3 Hackathon Demo Mode

```text
APP_ENV=demo
DEBUG=false
DEMO_MODE=true
```

Uses stable demo data.

Should still run:

```text
LangGraph workflow
ranking
recommendation explanations
workflow trace
calendar export
ticket redirect validation
```

Demo mode must not bypass the core architecture.

---

# 7. Required Environment Variables

```text
APP_NAME=Pulse AI
APP_ENV=development
DEBUG=true
SECRET_KEY=change_me

DATABASE_URL=sqlite:///./pulse_ai.db

DEMO_MODE=false
CACHE_TTL_SECONDS=900

TICKETMASTER_API_KEY=
GEOAPIFY_API_KEY=
OPENWEATHER_API_KEY=

LLM_PROVIDER=none
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=
```

---

# 8. `.env.example`

The repo must include:

```text
.env.example
```

It should include placeholder values only.

Never commit:

```text
.env
.env.production
.env.demo
```

---

# 9. Local Setup Command

Recommended setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

App should run at:

```text
http://localhost:8000
```

---

# 10. Docker Setup

## 10.1 Dockerfile Requirements

Dockerfile should:

* use Python base image,
* install dependencies,
* copy app code,
* expose port 8000,
* run Uvicorn.

Example target command:

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 10.2 Docker Run

```bash
docker build -t pulse-ai .
docker run --env-file .env -p 8000:8000 pulse-ai
```

---

## 10.3 Docker Compose

Optional:

```yaml
services:
  pulse-ai:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
```

Do not add unnecessary services for MVP.

---

# 11. Database Deployment

For MVP:

```text
SQLite is acceptable.
```

Rules:

* create tables on startup if missing,
* keep schema simple,
* do not commit generated DB files,
* use PostgreSQL only after MVP is stable.

Required ignored files:

```text
pulse_ai.db
*.sqlite
*.sqlite3
```

---

# 12. Demo Mode Architecture

Demo mode must use:

```text
app/data/demo_events.json
```

When:

```text
DEMO_MODE=true
```

the event discovery node must call:

```text
DemoProvider
```

instead of live APIs.

---

# 13. Demo Mode Flow

```text
User query
→ parse query
→ validate intent
→ DemoProvider returns matching demo data
→ normalize events
→ enrich using static/context data
→ rank events
→ generate explanations
→ render UI
```

The user experience should look identical to live mode.

---

# 14. Demo Cities

Demo data should include rich international examples:

```text
Berlin
London
New York
Paris
Amsterdam
Los Angeles
San Francisco
Dubai
Tokyo
```

---

# 15. Recommended Demo Queries

```text
Find electronic music events in Berlin this weekend under $100
Show Broadway shows in New York this month
Find startup networking events in San Francisco next week
Show football matches in London this weekend
Find art exhibitions in Paris this month
Find nightlife events in Amsterdam this weekend
```

---

# 16. Fallback Strategy

If `DEMO_MODE=false` but a live API fails:

```text
try cache
→ if cache unavailable, use demo fallback
→ continue workflow
→ show fallback notice
```

User-facing notice:

```text
Live events were unavailable, so Pulse AI is showing stable demo results.
```

---

# 17. Cache Strategy for Deployment

Use cache for:

```text
event searches
venue enrichment
weather lookups
ranked responses
```

Cache backend:

```text
SQLite cache table
```

Recommended TTL:

```text
event search: 15 minutes
venue enrichment: 24 hours
weather: 30 minutes
ranked response: 15 minutes
```

---

# 18. Health Check Endpoint

Route:

```text
GET /health
```

Should return safe information only:

```json
{
  "status": "ok",
  "app": "Pulse AI",
  "environment": "demo",
  "demo_mode": true,
  "database": "ok",
  "ticketmaster_configured": false,
  "geoapify_configured": false
}
```

Do not return:

```text
API keys
secret values
full env contents
internal stack traces
```

---

# 19. Deployment Checklist

Before deploying:

```text
[ ] .env is not committed
[ ] .env.example exists
[ ] requirements.txt is complete
[ ] Dockerfile works
[ ] app starts locally
[ ] /health returns ok
[ ] DEMO_MODE=true works without API keys
[ ] pytest passes
[ ] safe redirects are validated
[ ] demo data is included
[ ] README has setup steps
```

---

# 20. Hackathon Demo Checklist

Before presenting:

```text
[ ] Run app locally or deployed URL
[ ] Set DEMO_MODE=true
[ ] Test main demo query
[ ] Confirm event cards render
[ ] Confirm workflow trace renders
[ ] Confirm calendar export works
[ ] Confirm ticket redirect does not break
[ ] Confirm Bob session exports exist
[ ] Confirm README explains IBM Bob usage
```

---

# 21. Render Deployment Notes

Recommended build command:

```bash
pip install -r requirements.txt
```

Recommended start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Environment variables should be configured in Render dashboard.

Do not upload `.env`.

---

# 22. Railway Deployment Notes

Recommended:

```text
Python service
start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set environment variables through Railway variables.

---

# 23. IBM Cloud Code Engine Notes

If using IBM Cloud Code Engine:

* build container image,
* set environment variables securely,
* expose port 8000,
* use demo mode for judging reliability.

---

# 24. Demo Data Rules

Demo data must:

* look realistic,
* use international cities,
* include images or placeholder image URLs,
* include provider URLs,
* include venue names,
* include pricing,
* include dates,
* include categories.

Demo data must not include:

```text
real personal data
fake payment details
private API responses
confidential data
```

---

# 25. Fail-Safe Behavior

If everything fails, the UI should still show:

```text
Pulse AI is currently in safe demo mode.
Try one of the suggested demo prompts.
```

Never allow the app to crash visibly during demo.

---

# 26. Bob Implementation Notes

Bob should implement deployment in this order:

```text
1. .env.example
2. config loader
3. demo mode flag
4. demo events JSON
5. health endpoint
6. Dockerfile
7. requirements.txt
8. cache fallback
9. README deployment section
```

---

# 27. Final Deployment Goal

Pulse AI should be deployable and demoable with:

```bash
cp .env.example .env
# set DEMO_MODE=true
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The final demo should work even without live API keys.
