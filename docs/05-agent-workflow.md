# Pulse AI — Agent Workflow Document

## 1. Purpose

This document defines the agent workflow for **Pulse AI — Intelligent Event Discovery & Ticketing Assistant**.

The workflow will be implemented using **LangGraph from the start** and will coordinate:

```text
user request → intent extraction → event search → enrichment → ranking → explanation → response
```

The goal is to make the system behave like an intelligent global event concierge, not a basic search page.

---

# 2. Workflow Philosophy

Pulse AI should use agents as focused workflow responsibilities.

Each agent should:

* do one clear job,
* update the shared LangGraph state,
* call tools only when needed,
* return structured outputs,
* fail safely,
* and support demo reliability.

---

# 3. Core Agent List

| Agent                     | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| Query Understanding Agent | Understand the user’s natural language request   |
| Validation Agent          | Confirm enough details exist to search           |
| Event Discovery Agent     | Search event providers                           |
| Normalization Agent       | Convert provider data into internal event format |
| Context Enrichment Agent  | Add venue/location/weather context               |
| Ranking Agent             | Score and rank events                            |
| Recommendation Agent      | Explain why results are recommended              |
| Planning Agent            | Support save/export/itinerary actions            |
| Response Agent            | Prepare final UI-ready response                  |

---

# 4. LangGraph State

The workflow should use one shared state object.

```text
PulseGraphState
- raw_query
- user_session_id
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
- selected_event
- calendar_export
- redirect_url
- errors
- fallback_used
- workflow_trace
```

---

# 5. Main Workflow

```text
START
  ↓
Query Understanding Agent
  ↓
Validation Agent
  ↓
Event Discovery Agent
  ↓
Normalization Agent
  ↓
Context Enrichment Agent
  ↓
Ranking Agent
  ↓
Recommendation Agent
  ↓
Response Agent
  ↓
END
```

---

# 6. Workflow Diagram

```text
┌──────────────┐
│ User Request │
└──────┬───────┘
       ▼
┌───────────────────────────┐
│ Query Understanding Agent │
└──────┬────────────────────┘
       ▼
┌───────────────────────────┐
│ Validation Agent          │
└──────┬─────────────┬──────┘
       │ valid       │ missing info
       ▼             ▼
┌──────────────────┐ ┌────────────────────┐
│ Event Discovery  │ │ Clarification Reply │
│ Agent            │ └────────────────────┘
└──────┬───────────┘
       ▼
┌───────────────────────────┐
│ Normalization Agent       │
└──────┬────────────────────┘
       ▼
┌───────────────────────────┐
│ Context Enrichment Agent  │
└──────┬────────────────────┘
       ▼
┌───────────────────────────┐
│ Ranking Agent             │
└──────┬────────────────────┘
       ▼
┌───────────────────────────┐
│ Recommendation Agent      │
└──────┬────────────────────┘
       ▼
┌───────────────────────────┐
│ Response Agent            │
└──────┬────────────────────┘
       ▼
┌──────────────┐
│ Final Result │
└──────────────┘
```

---

# 7. Agent Details

## 7.1 Query Understanding Agent

### Responsibility

Extract structured intent from the user query.

### Input

```text
Find electronic music events in Berlin this weekend under $100
```

### Output

```json
{
  "city": "Berlin",
  "country": "Germany",
  "category": "electronic music",
  "date_from": "2026-06-05",
  "date_to": "2026-06-07",
  "budget_max": 100,
  "currency": "USD",
  "preferences": ["music", "nightlife", "electronic"]
}
```

### Notes

This agent should support:

* city extraction,
* category extraction,
* date parsing,
* budget parsing,
* preference extraction,
* default fallback values.

If the LLM fails, use deterministic parsing.

---

## 7.2 Validation Agent

### Responsibility

Check whether the parsed request has enough information to continue.

### Required Fields

```text
city
date range
category or keyword
```

### If valid

Route to:

```text
Event Discovery Agent
```

### If invalid

Route to:

```text
Clarification Reply
```

Example clarification:

```text
Which city should I search in?
```

---

## 7.3 Event Discovery Agent

### Responsibility

Search available event providers using MCP tools.

### Main Tool

```text
pulse_search_events
```

### Primary Provider

```text
Ticketmaster Discovery API
```

### Optional Providers

```text
Eventbrite
Meetup
Dice
Resident Advisor
```

### Output

```text
events_raw
```

### Failure Handling

| Situation       | Action                |
| --------------- | --------------------- |
| API timeout     | Use cached results    |
| API key missing | Use demo events       |
| No results      | Broaden category/date |
| Rate limit      | Use cached/demo data  |

---

## 7.4 Normalization Agent

### Responsibility

Convert provider-specific responses into Pulse AI’s internal event schema.

### Input

```text
events_raw
```

### Output

```text
events_normalized
```

### Normalized Fields

```text
id
title
description
category
venue_name
venue_city
venue_country
latitude
longitude
start_datetime
end_datetime
price_min
price_max
currency
provider
provider_event_url
image_url
```

---

## 7.5 Context Enrichment Agent

### Responsibility

Add extra information that improves recommendations.

### Tools

```text
pulse_enrich_venue
pulse_get_weather_context
```

### Enrichment Data

```text
nearby restaurants
nearby attractions
public transport context
weather suitability
venue area summary
```

### Output

```text
enriched_events
```

### Rule

If enrichment fails, continue with base event data.

---

## 7.6 Ranking Agent

### Responsibility

Score and order events.

### Tool

```text
pulse_rank_events
```

### Ranking Factors

```text
relevance_score
date_match_score
affordability_score
popularity_score
context_score
weather_score
```

### Formula

```text
total_score =
  relevance_score * 0.30 +
  date_match_score * 0.20 +
  affordability_score * 0.20 +
  popularity_score * 0.15 +
  context_score * 0.10 +
  weather_score * 0.05
```

### Output

```text
ranked_events
```

---

## 7.7 Recommendation Agent

### Responsibility

Generate plain-English explanations for the ranked results.

### Output Example

```text
This event is recommended because it matches your electronic music preference,
fits your budget, happens this weekend, and is hosted at a popular Berlin venue.
```

### Explanation Types

```text
Best Overall
Best Budget Pick
Trending Option
Closest Match
Premium Pick
```

---

## 7.8 Planning Agent

### Responsibility

Handle post-search planning actions.

### Supported Actions

```text
save event
export calendar file
create shortlist
prepare ticket redirect
```

### Tools

```text
pulse_create_calendar_file
pulse_generate_ticket_redirect
```

This agent may run after the main recommendation flow when a user selects an event.

---

## 7.9 Response Agent

### Responsibility

Prepare the final response for UI rendering.

### Output

```text
event cards
recommendation summary
fallback notices
error messages
ticket links
calendar actions
```

---

# 8. Conditional Routing Rules

| Condition               | Route                        |
| ----------------------- | ---------------------------- |
| Missing city            | Clarification Reply          |
| Missing date            | Use default upcoming weekend |
| Missing category        | Search broad events          |
| No results              | Broaden Search Agent         |
| API failure             | Fallback Cache/Demo Agent    |
| Outdoor event found     | Weather Context Tool         |
| User asks for itinerary | Planning Agent               |
| User selects event      | Planning Agent               |
| Valid ranked results    | Response Agent               |

---

# 9. Fallback Workflow

Fallbacks are important for demo reliability.

```text
External API fails
  ↓
Check cache
  ↓
If cache exists, use cached results
  ↓
If no cache, use demo events
  ↓
Continue ranking and response flow
```

The fallback should still pass through:

```text
normalization → ranking → explanation → response
```

This ensures the demo still shows LangGraph orchestration.

---

# 10. Demo Mode Workflow

When:

```text
DEMO_MODE=true
```

The Event Discovery Agent should call:

```text
pulse_get_demo_events
```

instead of live APIs.

Demo mode should:

* use realistic international event data,
* preserve LangGraph execution,
* preserve ranking,
* preserve explanations,
* preserve UI experience.

Recommended demo cities:

```text
Berlin
London
New York
Amsterdam
Paris
Los Angeles
```

---

# 11. Conversation Continuity

The system may store lightweight session context.

Examples:

```text
last searched city
preferred category
budget range
saved events
```

Example follow-up:

```text
User: Show cheaper options.
System uses previous city/category/date context.
```

Do not store sensitive personal data.

---

# 12. Workflow Trace

Each LangGraph run should capture a trace for debugging and demo explanation.

Trace fields:

```text
node_name
started_at
completed_at
status
tool_called
fallback_used
error_message
```

This can be shown in a developer/debug panel if time allows.

---

# 13. Agent Implementation Files

Suggested structure:

```text
app/graph/
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
    planning.py
```

---

# 14. Tool Mapping

| Agent                    | Tool                                                           |
| ------------------------ | -------------------------------------------------------------- |
| Event Discovery Agent    | `pulse_search_events`, `pulse_get_demo_events`                 |
| Context Enrichment Agent | `pulse_enrich_venue`, `pulse_get_weather_context`              |
| Ranking Agent            | `pulse_rank_events`                                            |
| Planning Agent           | `pulse_create_calendar_file`, `pulse_generate_ticket_redirect` |
| Response Agent           | No external tool required                                      |

---

# 15. Bob Usage Guidance

Bob should be asked to implement this workflow in increments:

```text
1. Define PulseGraphState.
2. Create empty LangGraph nodes.
3. Wire the graph.
4. Add mocked event data.
5. Add ranking.
6. Add response formatting.
7. Add real Ticketmaster integration.
8. Add enrichment.
9. Add calendar export.
10. Add tests.
```

The detailed incremental plan will be handled in a separate Bob development task document.

---

# 16. Final Workflow Goal

The final agent workflow should clearly demonstrate:

```text
Natural language request
→ structured intent
→ LangGraph orchestration
→ MCP tool calls
→ enriched event data
→ explainable ranking
→ polished UI response
```

This is the core AI story for Pulse AI.
