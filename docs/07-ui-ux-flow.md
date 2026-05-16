# Pulse AI — UI/UX Flow Document

## 1. Purpose

This document defines the user interface and user experience flow for Pulse AI.

The goal is to help Bob build a clean, demo-friendly frontend using:

```text
Jinja2
HTMX
vanilla JavaScript
vanilla CSS
```

Important rule:

```text
Do not use React.
Do not use npm.
Do not use Node-based frontend tooling.
```

---

# 2. UX Goal

Pulse AI should feel like:

```text
an intelligent global event concierge
```

The interface must be:

* simple,
* fast,
* modern,
* easy to demo,
* visually clear,
* and focused on the main workflow.

The user should understand the product within the first 10 seconds.

---

# 3. Core User Journey

Primary journey:

```text
User enters natural language event request
→ app understands intent
→ LangGraph workflow runs
→ MCP tools fetch/enrich events
→ ranked event cards appear
→ user reviews explanations
→ user saves/export event
→ user opens official ticket provider
```

---

# 4. Main Pages

## 4.1 Home / Search Page

Route:

```text
GET /
```

Purpose:

* introduce Pulse AI,
* show search input,
* display suggested demo prompts,
* render event results.

Main sections:

```text
Hero section
Search assistant panel
Suggested prompts
Results area
Workflow trace panel
```

---

## 4.2 Event Detail Page

Route:

```text
GET /events/{event_id}
```

Purpose:

* show detailed event information,
* explain recommendation reasoning,
* show venue context,
* provide ticket link,
* provide calendar export.

This page is optional for MVP if event cards can show enough information inline.

---

## 4.3 Saved Events Page

Route:

```text
GET /saved
```

Purpose:

* display saved events,
* allow calendar export,
* reopen ticket provider links.

This can be deferred if time is limited.

---

## 4.4 Health / Developer Page

Route:

```text
GET /health
```

Purpose:

* confirm app status,
* show safe configuration status,
* confirm demo mode,
* confirm API availability without exposing secrets.

---

# 5. Home Page Layout

Recommended layout:

```text
┌─────────────────────────────────────────────┐
│ Header                                      │
│ Pulse AI | Demo Mode badge | GitHub link    │
├─────────────────────────────────────────────┤
│ Hero                                        │
│ "Find the best global events with AI"       │
│ Short product explanation                   │
├─────────────────────────────────────────────┤
│ Search Panel                                │
│ [Natural language input                  ]  │
│ [Find Events]                               │
│ Suggested prompts                           │
├─────────────────────────────────────────────┤
│ Results / Loading / Empty State             │
├─────────────────────────────────────────────┤
│ Optional Workflow Trace                     │
│ Parse → Search → Enrich → Rank → Explain    │
└─────────────────────────────────────────────┘
```

---

# 6. Search Panel

## 6.1 Input Placeholder

```text
Find electronic music events in Berlin this weekend under $100
```

---

## 6.2 Suggested Demo Prompts

Use international examples:

```text
Find electronic music events in Berlin this weekend under $100
Show Broadway shows in New York this month
Find startup networking events in San Francisco next week
Show football matches in London this weekend
Find art exhibitions in Paris this month
```

---

## 6.3 Search Behavior

The search form should submit with HTMX.

Route:

```text
POST /search
```

HTMX behavior:

```html
hx-post="/search"
hx-target="#results"
hx-swap="innerHTML"
hx-indicator="#loading"
```

Expected behavior:

* page does not reload,
* loading state appears,
* results replace the results area,
* errors render inside results area.

---

# 7. Results Area

The results area should support:

```text
loading state
empty state
error state
ranked results
fallback/demo notice
```

---

## 7.1 Loading State

Text:

```text
Finding the best events and ranking them for you...
```

Optional workflow animation:

```text
Understanding request → Searching events → Enriching venues → Ranking results
```

---

## 7.2 Empty State

Text:

```text
No matching events were found. Try a broader city, category, or date range.
```

Suggested fallback prompts:

```text
Try: "events in London this weekend"
Try: "concerts in New York this month"
```

---

## 7.3 Error State

Safe user-facing text:

```text
We could not load live events right now. Showing cached or demo results if available.
```

Never show:

```text
API keys
tracebacks
raw provider errors
internal file paths
```

---

# 8. Event Card Design

Each event result should be displayed as a card.

## Card Fields

```text
Image
Event title
Recommendation label
Date and time
Venue
City/country
Price range
Category
Provider
Why recommended
Action buttons
```

---

## Example Card Layout

```text
┌──────────────────────────────────────────┐
│ [Image]                                  │
│ Best Overall                             │
│ Electronic Night Berlin                  │
│ Fri, Jun 5, 2026 • 8:00 PM               │
│ Berlin Arena • Berlin, Germany           │
│ $40 - $95                                │
│                                          │
│ Why recommended:                         │
│ Matches your electronic music preference,│
│ fits your budget, and happens this       │
│ weekend.                                 │
│                                          │
│ [Save] [Add to Calendar] [View Tickets]  │
└──────────────────────────────────────────┘
```

---

# 9. Recommendation Labels

Use clear labels:

```text
Best Overall
Best Budget Pick
Trending Option
Closest Match
Premium Pick
Great Venue
Outdoor Friendly
```

These labels make ranking easy to understand during demo.

---

# 10. Workflow Trace Panel

Because the project is built around LangGraph and MCP, the UI should show a simple workflow trace.

This helps judges understand that the app is not just a search wrapper.

## Example Trace

```text
AI Workflow
✓ Parsed request
✓ Searched Ticketmaster
✓ Enriched venue context
✓ Ranked events
✓ Generated explanations
```

---

## Trace Fields

```text
node name
status
tool used
fallback used
execution time
```

---

## UI Behavior

The trace can appear:

* below results,
* in a collapsible panel,
* or as a small sidebar.

Recommended MVP:

```text
collapsible panel below results
```

---

# 11. Event Detail View

If implemented, event detail should show:

```text
large event image
event title
date/time
venue information
price range
recommendation explanation
venue context
nearby places
weather note
ticket provider button
calendar export button
```

---

# 12. Save Event Flow

## Button

```text
Save
```

## Behavior

HTMX request:

```text
POST /events/{event_id}/save
```

Result:

```text
button changes to "Saved"
```

No login required for MVP.

Saved events can be stored using:

```text
session ID
SQLite
```

---

# 13. Calendar Export Flow

## Button

```text
Add to Calendar
```

Route:

```text
GET /events/{event_id}/calendar.ics
```

Behavior:

* downloads `.ics` file,
* works without login,
* uses sanitized event data.

---

# 14. Ticket Redirect Flow

## Button

```text
View Tickets
```

Route:

```text
GET /redirect/{event_id}
```

Behavior:

* validates provider URL,
* logs safe outbound click,
* redirects to official provider.

The UI should display:

```text
Official provider link
```

Do not imply Pulse AI processes payments.

---

# 15. Demo Mode UI

When:

```text
DEMO_MODE=true
```

show a small badge:

```text
Demo Mode
```

Do not make it look like an error.

Suggested text:

```text
Demo Mode: using stable event data for reliable presentation.
```

---

# 16. Responsive Design

The UI must work on:

```text
desktop
tablet
mobile
```

Priority:

```text
desktop first for hackathon demo
```

Mobile should still be readable.

---

# 17. Visual Style

Recommended style:

```text
clean
modern
dark or light neutral theme
large search box
card-based results
clear action buttons
subtle shadows
rounded corners
good spacing
```

Avoid:

```text
complex dashboards
too many menus
admin panels
heavy animations
overcrowded cards
```

---

# 18. Color Guidance

Recommended visual direction:

```text
dark navy / charcoal background
white cards or dark cards
accent color: electric blue or violet
success color for completed workflow steps
warning color for fallback/demo mode
```

Keep CSS simple and custom.

---

# 19. Template Structure

```text
app/templates/
  base.html
  index.html
  saved.html
  event_detail.html

  partials/
    search_panel.html
    suggested_prompts.html
    loading.html
    event_results.html
    event_card.html
    workflow_trace.html
    empty_state.html
    error.html
    demo_badge.html
```

---

# 20. Static Assets

```text
app/static/
  css/
    styles.css
  js/
    app.js
```

JavaScript should only handle:

```text
small UI interactions
copy prompt to search box
toggle workflow trace
minor button state changes
```

Do not build large frontend logic in JavaScript.

---

# 21. HTMX Interaction Map

| UI Element       | Route                           | Target             | Behavior             |
| ---------------- | ------------------------------- | ------------------ | -------------------- |
| Search form      | `POST /search`                  | `#results`         | Render event results |
| Save button      | `POST /events/{id}/save`        | button itself      | Change to Saved      |
| Calendar button  | `GET /events/{id}/calendar.ics` | browser download   | Download file        |
| Ticket button    | `GET /redirect/{id}`            | browser navigation | Open provider        |
| Suggested prompt | local JS                        | search input       | Fill input field     |
| Workflow toggle  | local JS                        | trace panel        | Show/hide trace      |

---

# 22. Accessibility Requirements

The UI should include:

* semantic HTML,
* visible focus states,
* readable contrast,
* alt text for event images,
* labels for forms,
* keyboard-accessible buttons.

---

# 23. User-Facing Copy

## Hero Title

```text
Find your next unforgettable event with AI.
```

## Hero Subtitle

```text
Search concerts, sports, festivals, shows, and conferences across global cities using an intelligent event concierge.
```

## Search Button

```text
Find Events
```

## Empty State

```text
No matching events found. Try broadening your search.
```

## Ticket Button

```text
View Official Tickets
```

## Calendar Button

```text
Add to Calendar
```

---

# 24. Demo Flow

Recommended live demo:

## Step 1

Open home page.

## Step 2

Click suggested prompt:

```text
Find electronic music events in Berlin this weekend under $100
```

## Step 3

Submit search.

## Step 4

Show ranked event cards.

## Step 5

Open workflow trace panel.

## Step 6

Explain:

```text
LangGraph parsed the request, MCP tools searched events, venue context was added, and the ranking engine explained why each event was recommended.
```

## Step 7

Click:

```text
Add to Calendar
```

## Step 8

Click:

```text
View Official Tickets
```

---

# 25. MVP Boundary

Must build:

```text
Home page
Search form
Suggested prompts
Results cards
Recommendation explanations
Workflow trace
Save button
Calendar export
Ticket redirect
Demo mode badge
```

Can defer:

```text
full user accounts
admin dashboard
advanced preferences
map view
social sharing
payments
```

---

# 26. Final UI Goal

Pulse AI’s UI should make the demo feel effortless:

```text
one natural language search
→ ranked global events
→ visible AI workflow
→ explanation
→ save/calendar/ticket action
```

The interface should help judges immediately understand:

* what the product does,
* where AI is used,
* how MCP tools are involved,
* and why the recommendation is useful.
