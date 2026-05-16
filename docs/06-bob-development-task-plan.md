# Pulse AI — Bob Development Task Plan

## 1. Purpose

This document defines how IBM Bob should be used to develop Pulse AI efficiently during the hackathon.

The goal is to:

* minimize wasted Bob credits,
* avoid repeated file rereading,
* maintain development continuity across sessions,
* support fast incremental progress,
* and keep the architecture aligned with the LangGraph + MCP design.

This document acts as:

* the execution roadmap,
* the session continuity strategy,
* and the AI-assisted development workflow guide.

---

# 2. Core Development Philosophy

Pulse AI should be built using:

```text
small increments
+
stable milestones
+
continuous handover tracking
+
minimal context waste
+
priority-first execution
```

The system should always remain:

* runnable,
* testable,
* and demoable.

---

# 3. Critical Rule: Avoid Context Waste

One of the biggest hackathon problems with AI coding agents is:

```text
Repeatedly rereading the same files
```

This:

* wastes credits,
* slows development,
* increases hallucinations,
* and reduces implementation consistency.

To solve this, the project must maintain:

```text
TASKS.md
HAND_OVER.md
```

at all times.

These are mandatory operational files.

---

# 4. Required Operational Files

| File                    | Purpose                                      |
| ----------------------- | -------------------------------------------- |
| `TASKS.md`              | Active implementation tracking               |
| `HAND_OVER.md`          | Session continuity and current project state |
| `ARCHITECTURE_NOTES.md` | Important architectural decisions            |
| `KNOWN_ISSUES.md`       | Bugs and unresolved blockers                 |
| `bob_sessions/`         | Exported Bob task sessions for judging       |

---

# 5. TASKS.md Specification

## Purpose

Tracks:

* completed work,
* current tasks,
* pending tasks,
* priorities,
* blockers,
* implementation order.

Bob should update this file continuously.

---

## Structure

```markdown
# Pulse AI — Development Tasks

## Completed
- [x] Initial FastAPI setup
- [x] LangGraph workflow scaffold
- [x] Ticketmaster integration
- [x] HTMX search form

---

## In Progress
- [ ] Ranking engine improvements

---

## Next Priority
- [ ] Venue enrichment
- [ ] Weather context integration
- [ ] Calendar export

---

## Future Enhancements
- [ ] Event itinerary planning
- [ ] User preferences
- [ ] Redis caching

---

## Blockers
- Geoapify API rate limit issue
```

---

## Rules for Bob

Bob should:

* update completed tasks immediately,
* move unfinished work to "In Progress",
* add blockers when encountered,
* never remove historical task completion,
* preserve chronological progress.

---

# 6. HAND_OVER.md Specification

## Purpose

This is the most important continuity file.

It prevents future sessions from needing to:

* reread the entire repository,
* rediscover architecture,
* or infer project state.

It should summarize:

* what has been built,
* current architecture,
* what works,
* what is broken,
* current focus,
* and next exact steps.

---

## Structure

```markdown
# Pulse AI — Session Hand Over

## Current System Status
- FastAPI app working
- LangGraph workflow connected
- HTMX search working
- Ticketmaster integration working

---

## Current Priority
Implement venue enrichment agent.

---

## Current Graph Flow
parse_query
→ validate_query
→ search_events
→ normalize_events
→ rank_events
→ generate_explanations
→ prepare_response

---

## Existing APIs
- Ticketmaster connected
- Geoapify pending
- Weather pending

---

## Current Problems
- Ranking explanations are too generic.
- Event images sometimes missing.

---

## Important Files
- app/graph/workflow.py
- app/tools/event_tools.py
- app/routes/web.py

---

## Last Completed Work
Implemented ranking node and explanation generation.

---

## Next Recommended Step
Create venue enrichment tool and integrate into LangGraph.

---

## Environment Notes
DEMO_MODE=true currently enabled.

---

## Testing Status
- Workflow tests passing
- Frontend partial rendering passing
```

---

## Rules for Bob

Before every new implementation session:

```text
Read HAND_OVER.md first.
```

This should be enough to resume work without scanning the entire repo.

Bob should update this file:

* after major milestones,
* after architecture changes,
* after new integrations,
* after blockers are discovered.

---

# 7. ARCHITECTURE_NOTES.md

## Purpose

Tracks architectural decisions to avoid inconsistent implementations later.

Example:

```markdown
# Architecture Notes

## Frontend Decision
No React or npm allowed.

Frontend stack:
- Jinja2
- HTMX
- vanilla JS

Reason:
Simpler deployment and faster hackathon execution.

---

## AI Workflow Decision
LangGraph from the start.

Reason:
Better orchestration visibility for judging.
```

---

# 8. KNOWN_ISSUES.md

## Purpose

Tracks:

* unresolved bugs,
* flaky APIs,
* technical debt,
* temporary hacks,
* demo risks.

Example:

```markdown
# Known Issues

## Weather API
Occasionally returns inconsistent timezone formatting.

Temporary workaround:
Normalize to UTC before ranking.

---

## Ticketmaster
Some events missing images.

Fallback:
Use placeholder image.
```

---

# 9. Bob Session Export Strategy

Hackathon judging requires Bob usage proof.

Mandatory folder:

```text
bob_sessions/
```

---

## Required Exports

For every major feature:

* export Bob task session
* save screenshots
* save markdown summaries

Example:

```text
bob_sessions/
  fastapi_setup/
    summary.png
    history.md

  langgraph_workflow/
    summary.png
    history.md

  ticketmaster_integration/
    summary.png
    history.md
```

---

# 10. Development Execution Strategy

## Important Rule

Do NOT attempt to build the entire project at once.

Development must follow:

```text
core workflow first
→ stable MVP
→ enrichment
→ polish
```

---

# 11. Development Phases

# Phase 1 — Foundation

## Goal

Create runnable skeleton.

---

## Tasks

### Backend Setup

* create FastAPI app
* configure routing
* configure templates
* configure static assets

### Frontend Setup

* HTMX setup
* search page
* loading states

### LangGraph Setup

* define graph state
* create empty nodes
* wire workflow

### Operational Files

* create TASKS.md
* create HAND_OVER.md
* create ARCHITECTURE_NOTES.md
* create KNOWN_ISSUES.md

---

## Expected Outcome

```text
Basic app starts successfully.
Graph executes mocked workflow.
```

---

# Phase 2 — Core Search Workflow

## Goal

Get real event search working.

---

## Tasks

### Event Search

* Ticketmaster API client
* search tool
* normalized event schema

### LangGraph Nodes

* parse_query
* validate_query
* search_events
* normalize_events

### UI

* event cards
* search results rendering

---

## Expected Outcome

```text
User can search events successfully.
```

---

# Phase 3 — Ranking & Recommendations

## Goal

Make results intelligent.

---

## Tasks

### Ranking

* scoring engine
* ranking formula
* recommendation labels

### AI Explanations

* generate recommendation explanations

### UI

* explanation badges
* ranking display

---

## Expected Outcome

```text
AI-generated recommendations visible.
```

---

# Phase 4 — Enrichment

## Goal

Add contextual intelligence.

---

## Tasks

### Venue Enrichment

* Geoapify integration
* nearby places
* area summaries

### Weather Context

* OpenWeather integration
* outdoor suitability

### LangGraph Updates

* enrichment nodes
* conditional routing

---

## Expected Outcome

```text
Events include contextual insights.
```

---

# Phase 5 — Planning Features

## Goal

Improve demo experience.

---

## Tasks

### Calendar Export

* `.ics` generation

### Ticket Redirect

* safe outbound redirects

### Saved Events

* SQLite persistence

---

## Expected Outcome

```text
End-to-end event workflow complete.
```

---

# Phase 6 — Demo Optimization

## Goal

Maximize hackathon presentation quality.

---

## Tasks

### Demo Mode

* stable fallback responses
* cached event results

### UI Polish

* loading states
* animations
* better cards

### Stability

* API fallback handling
* error states

---

## Expected Outcome

```text
Reliable polished demo ready.
```

---

# 12. Bob Prompting Strategy

## Bad Prompt

```text
Build the entire project.
```

This causes:

* context overload,
* hallucinations,
* inconsistent architecture.

---

## Good Prompt

```text
Implement only the LangGraph parse_query node.

Requirements:
- extract city
- extract category
- extract budget
- use Pydantic models
- update TASKS.md and HAND_OVER.md
```

---

# 13. Required Bob Session Workflow

For every implementation task:

## Step 1

Read:

```text
HAND_OVER.md
TASKS.md
```

---

## Step 2

Implement ONE focused task.

---

## Step 3

Run tests.

---

## Step 4

Update:

```text
TASKS.md
HAND_OVER.md
KNOWN_ISSUES.md
```

---

## Step 5

Export Bob session.

---

# 14. File Update Rules

| File                  | Update Frequency          |
| --------------------- | ------------------------- |
| TASKS.md              | Every implementation step |
| HAND_OVER.md          | Every milestone           |
| KNOWN_ISSUES.md       | When bug discovered       |
| ARCHITECTURE_NOTES.md | When architecture changes |

---

# 15. Demo Reliability Rules

The project must always remain:

```text
demoable
```

Never leave the repository in a broken state.

Before ending a session:

* ensure app starts,
* ensure workflow runs,
* ensure search page renders.

---

# 16. Demo Mode Strategy

Use:

```text
DEMO_MODE=true
```

during presentations.

Benefits:

* avoids live API failure,
* avoids rate-limit issues,
* preserves workflow visibility,
* keeps LangGraph execution active.

---

# 17. Development Priority Order

Strict order:

```text
1. App startup
2. LangGraph workflow
3. Event search
4. Normalization
5. Ranking
6. Recommendation explanations
7. UI rendering
8. Venue enrichment
9. Weather context
10. Calendar export
11. Demo polish
```

Avoid:

* authentication,
* payment processing,
* complex dashboards,
* unnecessary admin panels.

---

# 18. Testing Strategy

Testing should evolve incrementally.

## Initial Tests

* graph execution
* route rendering
* event normalization

## Midway Tests

* ranking logic
* enrichment workflows
* redirect safety

## Final Tests

* end-to-end search flow
* calendar export
* demo mode

---

# 19. Final Repository Structure

```text
pulse-ai/
  app/
  docs/
  tests/
  bob_sessions/

  TASKS.md
  HAND_OVER.md
  ARCHITECTURE_NOTES.md
  KNOWN_ISSUES.md

  README.md
  AGENTS.md
```

---

# 20. Final Development Goal

The final system should demonstrate:

```text
Natural language request
→ LangGraph orchestration
→ MCP tool calls
→ contextual enrichment
→ explainable ranking
→ polished UI response
```

while maintaining:

* stable incremental development,
* low Bob context waste,
* clear session continuity,
* and strong hackathon demo reliability.
