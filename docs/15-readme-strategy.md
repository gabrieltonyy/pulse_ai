# Pulse AI — README Strategy

## 1. Purpose

This document defines how the final `README.md` should be written for Pulse AI.

The README must help judges and developers quickly understand:

* what the project does,
* why it matters,
* how IBM Bob was used,
* how MCP and LangGraph are involved,
* how to run the project,
* and how to demo it safely.

---

# 2. README Goal

The README should make Pulse AI look:

```text
clear
polished
credible
demo-ready
AI-native
hackathon-aligned
```

The first 30 seconds of reading should communicate:

```text
Pulse AI is an AI-powered global event concierge built with IBM Bob, LangGraph, and MCP-style tool orchestration.
```

---

# 3. Recommended README Structure

```text
README.md

1. Project title and tagline
2. Short product summary
3. Demo preview
4. Problem statement
5. Solution overview
6. Key features
7. IBM Bob usage
8. Architecture overview
9. LangGraph workflow
10. MCP tool layer
11. Tech stack
12. Setup instructions
13. Environment variables
14. Running locally
15. Demo mode
16. Testing
17. Security notes
18. Repository structure
19. Hackathon judging notes
20. Roadmap
```

---

# 4. Title Section

Recommended title:

```markdown
# Pulse AI — Intelligent Event Discovery & Ticketing Assistant
```

Recommended tagline:

```markdown
An AI-powered global event concierge built with IBM Bob, LangGraph, and MCP-style tool orchestration.
```

---

# 5. Short Summary

The README should include a short paragraph like:

```markdown
Pulse AI helps users discover, compare, and plan events across major global cities using natural language. It combines LangGraph workflows, MCP-style tools, event APIs, venue enrichment, recommendation scoring, and ticket provider handoff into one polished AI concierge experience.
```

---

# 6. Demo Preview Section

Include:

```markdown
## Demo Preview
```

Recommended content:

```text
Search: "Find electronic music events in Berlin this weekend under $100"

Pulse AI will:
1. understand the request,
2. search event providers,
3. enrich venue context,
4. rank events,
5. explain recommendations,
6. allow calendar export,
7. redirect to official ticket providers.
```

If screenshots are available, include:

```markdown
![Pulse AI Demo](docs/images/demo-preview.png)
```

---

# 7. Problem Statement

Explain the user problem:

```markdown
Finding the right event is fragmented. Users often search multiple platforms, compare prices manually, check venues separately, and then plan around weather or location context on their own.
```

Keep it short and direct.

---

# 8. Solution Overview

Explain the product:

```markdown
Pulse AI acts as an intelligent event concierge. It uses AI agents and MCP-style tools to search global event data, rank results, enrich venue context, and produce useful recommendations with clear explanations.
```

---

# 9. Key Features

Recommended feature list:

```markdown
## Key Features

- Natural language event search
- Global city event discovery
- LangGraph-powered workflow orchestration
- MCP-style tool layer
- Ticketmaster event search
- Geoapify venue enrichment
- Optional weather context
- Explainable ranking engine
- Calendar export
- Safe official ticket redirects
- Demo mode for reliable presentations
```

---

# 10. IBM Bob Usage Section

This is one of the most important README sections.

Recommended heading:

```markdown
## How IBM Bob Was Used
```

Explain that Bob helped with:

```text
project planning
architecture design
LangGraph workflow scaffolding
MCP tool design
API integration planning
security-first implementation
test generation
README/documentation
demo preparation
```

Mention:

```markdown
Bob task session exports are included in the `bob_sessions/` folder as required for hackathon judging.
```

---

# 11. Architecture Section

Recommended heading:

```markdown
## Architecture Overview
```

Include simple text diagram:

```text
User Browser
  → FastAPI
  → Jinja2 + HTMX UI
  → LangGraph Workflow
  → MCP Tool Layer
  → External APIs
```

Mention:

```text
No React.
No npm.
No Node-based frontend build.
```

---

# 12. LangGraph Workflow Section

Recommended heading:

```markdown
## LangGraph Workflow
```

Include:

```text
parse_query
→ validate_query
→ search_events
→ normalize_events
→ enrich_venues
→ rank_events
→ generate_explanations
→ prepare_response
```

Explain:

```markdown
LangGraph coordinates the AI workflow through focused nodes, allowing the system to remain modular, observable, and easy to extend.
```

---

# 13. MCP Tool Layer Section

Recommended heading:

```markdown
## MCP-Style Tool Layer
```

List tools:

```text
pulse_search_events
pulse_enrich_venue
pulse_get_weather_context
pulse_rank_events
pulse_create_calendar_file
pulse_generate_ticket_redirect
pulse_get_demo_events
```

Explain that these tools separate AI workflow logic from external API integrations.

---

# 14. Tech Stack Section

Recommended:

```markdown
## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Workflow | LangGraph |
| Tool Layer | MCP Python SDK / FastMCP-style tools |
| Frontend | Jinja2, HTMX, vanilla JavaScript |
| Styling | Vanilla CSS |
| Database | SQLite |
| Testing | pytest, Playwright Python |
| Deployment | Docker / Render / Railway |
```

---

# 15. Setup Instructions

Recommended:

```markdown
## Local Setup
```

Commands:

```bash
git clone <repo-url>
cd pulse-ai

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Then:

```bash
uvicorn app.main:app --reload
```

---

# 16. Environment Variables Section

Recommended:

```markdown
## Environment Variables
```

Show safe example:

```text
APP_ENV=development
DEBUG=true
DEMO_MODE=true
SECRET_KEY=change_me
DATABASE_URL=sqlite:///./pulse_ai.db

TICKETMASTER_API_KEY=
GEOAPIFY_API_KEY=
OPENWEATHER_API_KEY=
```

Emphasize:

```markdown
Do not commit `.env`. Use `.env.example` only.
```

---

# 17. Demo Mode Section

Very important for judges.

Recommended heading:

```markdown
## Demo Mode
```

Content:

```markdown
Pulse AI includes a demo mode for stable hackathon presentations. When `DEMO_MODE=true`, the system uses realistic international event data while still running the full LangGraph workflow and ranking logic.
```

Command:

```bash
DEMO_MODE=true uvicorn app.main:app --reload
```

---

# 18. Testing Section

Recommended:

```markdown
## Running Tests
```

Commands:

```bash
pytest
```

Optional:

```bash
pytest tests/test_graph_workflow.py
pytest tests/test_security.py
pytest tests/e2e/test_demo_flow.py
```

---

# 19. Security Notes Section

Recommended:

```markdown
## Security Notes
```

Mention:

```text
API keys are loaded from environment variables.
Unsafe redirects are blocked.
External provider content is treated as untrusted.
No payment processing is handled by Pulse AI.
No personal data is required for MVP.
```

---

# 20. Repository Structure

Recommended:

```text
pulse-ai/
  app/
    graph/
    mcp/
    tools/
    integrations/
    routes/
    templates/
    static/
  docs/
  tests/
  bob_sessions/
  TASKS.md
  HAND_OVER.md
  README.md
```

---

# 21. Hackathon Judging Notes

Recommended heading:

```markdown
## Hackathon Judging Notes
```

Content:

```markdown
This project was built to align with the IBM Bob Hackathon theme: turning ideas into impact faster. IBM Bob was used as the development partner for planning, scaffolding, coding, testing, documentation, and demo preparation.
```

Mention:

```markdown
The repository includes:
- Bob task session exports
- architecture documentation
- security guide
- demo mode
- test strategy
```

---

# 22. Roadmap Section

Recommended:

```markdown
## Roadmap
```

Future ideas:

```text
hotel/event itinerary planning
multi-provider event search
user preference memory
group planning
mobile app
affiliate ticket partnerships
direct calendar integrations
```

---

# 23. README Writing Style

The README should be:

```text
confident
clear
brief
demo-oriented
judge-friendly
developer-friendly
```

Avoid:

```text
very long theory
overly technical jargon
unverified claims
local-only examples
messy setup instructions
```

---

# 24. README Must-Have Checklist

Before final submission, README must include:

```text
[ ] Clear project title
[ ] One-sentence product pitch
[ ] Demo query
[ ] IBM Bob usage section
[ ] LangGraph explanation
[ ] MCP tool explanation
[ ] Setup commands
[ ] Demo mode instructions
[ ] Security note
[ ] Testing commands
[ ] Repository structure
[ ] Bob sessions folder mention
```

---

# 25. Final README Goal

The final README should convince judges that:

```text
Pulse AI is not just an event search app.
It is a Bob-assisted, LangGraph-orchestrated, MCP-powered AI workflow product.
```

That is the story the README must communicate.
