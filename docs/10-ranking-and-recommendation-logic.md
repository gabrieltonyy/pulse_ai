# Pulse AI — Ranking and Recommendation Logic

## 1. Purpose

This document defines how Pulse AI ranks events and generates recommendation explanations.

Bob should use this document when implementing:

* ranking services,
* LangGraph ranking nodes,
* recommendation labels,
* event card explanations,
* fallback ranking,
* and tests.

---

# 2. Ranking Goal

Pulse AI should not simply list events from an API.

It should intelligently answer:

```text
Which events are best for this user request, and why?
```

The final output should show:

* ranked events,
* clear labels,
* explainable scores,
* human-readable reasoning,
* and useful alternatives.

---

# 3. Ranking Inputs

The ranking engine uses:

```text
SearchIntent
Normalized Events
Venue Context
Weather Context
User Preferences
Budget
Date Range
Category
Keyword
```

---

# 4. Ranking Output

Each ranked event should include:

```text
total_score
recommendation_label
score breakdown
plain-English explanation
```

Example:

```text
Best Overall — This event closely matches your electronic music request, is within your budget, and happens during your selected weekend.
```

---

# 5. Core Scoring Formula

Default formula:

```text
total_score =
  relevance_score * 0.30 +
  date_match_score * 0.20 +
  affordability_score * 0.20 +
  popularity_score * 0.15 +
  context_score * 0.10 +
  weather_score * 0.05
```

Score range:

```text
0 to 100
```

---

# 6. Score Components

## 6.1 Relevance Score

Measures how well the event matches the user’s intent.

Factors:

```text
category match
keyword match
title match
description match
venue/event type match
```

Suggested scoring:

| Match Type                 | Score |
| -------------------------- | ----: |
| Exact category match       |   100 |
| Strong keyword/title match |    85 |
| Related category match     |    70 |
| Weak text match            |    40 |
| No clear match             |    10 |

Example:

```text
User asks for "electronic music".
Event title/category contains "Electronic", "EDM", "DJ", or "Dance".
Score: 85-100.
```

---

## 6.2 Date Match Score

Measures how well the event fits the requested date range.

Suggested scoring:

| Date Fit                    | Score |
| --------------------------- | ----: |
| Inside requested date range |   100 |
| Within 1 day of range       |    75 |
| Within 3 days of range      |    50 |
| Same month                  |    30 |
| No valid date               |    10 |

If the user does not provide a date, use default upcoming weekend or next 30 days.

---

## 6.3 Affordability Score

Measures whether the event fits the user’s budget.

Suggested scoring:

| Price Fit                                | Score |
| ---------------------------------------- | ----: |
| Free event                               |   100 |
| Price max <= budget                      |   100 |
| Price min <= budget but max above budget |    75 |
| Up to 20% above budget                   |    55 |
| More than 20% above budget               |    20 |
| Price unknown                            |    60 |

If no budget is provided:

```text
affordability_score = 70
```

---

## 6.4 Popularity Score

Measures event appeal using provider signals.

Possible inputs:

```text
provider popularity score
event ranking
ticket availability
venue prominence
image availability
provider confidence
```

Suggested scoring:

| Signal                                 |  Score |
| -------------------------------------- | -----: |
| Provider popularity available and high | 90-100 |
| Strong venue/image/metadata quality    |  70-85 |
| Average event metadata                 |  50-70 |
| Weak metadata                          |  30-50 |
| Unknown                                |     50 |

Do not over-rely on popularity. A highly popular but irrelevant event should not outrank a relevant one.

---

## 6.5 Context Score

Measures usefulness of venue/location context.

Factors:

```text
nearby restaurants
nearby transport
nearby attractions
central location
rich venue data
```

Suggested scoring:

| Context Quality                          | Score |
| ---------------------------------------- | ----: |
| Strong nearby places + transport context |    90 |
| Some nearby places                       |    70 |
| Venue coordinates only                   |    50 |
| Venue name only                          |    30 |
| No venue context                         |    10 |

---

## 6.6 Weather Score

Only applies when weather data is available.

Suggested scoring:

| Weather Suitability | Score |
| ------------------- | ----: |
| Good                |   100 |
| Moderate            |    60 |
| Poor                |    25 |
| Unknown             |    50 |

If event is clearly indoor:

```text
weather_score = 70
```

If weather API is unavailable:

```text
weather_score = 50
```

---

# 7. Recommendation Labels

Each ranked event should receive one label.

Allowed labels:

```text
Best Overall
Best Budget Pick
Trending Option
Closest Match
Premium Pick
Great Venue
Outdoor Friendly
```

---

## 7.1 Label Assignment Rules

| Label            | Rule                                            |
| ---------------- | ----------------------------------------------- |
| Best Overall     | Highest total score                             |
| Best Budget Pick | Strong affordability score and decent relevance |
| Trending Option  | High popularity score                           |
| Closest Match    | Highest relevance score                         |
| Premium Pick     | High price + strong popularity/context          |
| Great Venue      | High context score                              |
| Outdoor Friendly | High weather score and outdoor event            |

---

# 8. Explanation Generation

Explanations should be short, useful, and specific.

Avoid generic text like:

```text
This is a good event.
```

Use:

```text
Recommended because it matches your electronic music preference, fits your budget, and happens during your selected weekend.
```

---

## 8.1 Explanation Template

```text
Recommended because it {relevance_reason}, {date_reason}, and {budget_reason}.
```

Optional additions:

```text
The venue also has {context_reason}.
Weather looks {weather_reason}.
```

---

## 8.2 Example Explanations

### Best Overall

```text
Recommended because it closely matches your electronic music request, fits your budget, and happens this weekend.
```

### Budget Pick

```text
This is the best budget-friendly option because it is within your price range while still matching your preferred event style.
```

### Great Venue

```text
This event stands out because the venue is close to restaurants, attractions, and public transport.
```

### Outdoor Friendly

```text
This outdoor event is a good fit because the forecast looks favorable for attending comfortably.
```

---

# 9. Recommendation Summary

After ranking events, generate a short summary.

Example:

```text
I found 8 strong matches in Berlin. The top recommendation balances music preference, budget, and date fit. I also highlighted a budget-friendly option and one event with strong venue context.
```

---

# 10. Fallback Ranking

If some data is missing, do not fail.

## Missing Price

Use:

```text
affordability_score = 60
```

## Missing Date

Use:

```text
date_match_score = 10
```

## Missing Venue Context

Use:

```text
context_score = 30
```

## Missing Weather

Use:

```text
weather_score = 50
```

## Missing Category

Use keyword/title matching.

---

# 11. Tie-Breaking Rules

If events have similar scores, sort by:

```text
1. Higher relevance_score
2. Earlier event date
3. Lower price_min
4. Higher popularity_score
5. Provider priority
```

Provider priority:

```text
Ticketmaster
Eventbrite
Meetup
DemoProvider
```

---

# 12. Search Result Limits

Recommended:

```text
Fetch up to 20 events.
Rank all.
Display top 6.
```

For demo:

```text
Display top 3 to 5.
```

This keeps the UI clean.

---

# 13. Ranking Node Behavior

LangGraph ranking node should:

```text
receive enriched_events
calculate scores
assign labels
sort events
save ranked_events to state
append workflow trace
```

---

# 14. Score Breakdown Display

Each event card may show:

```text
Match
Budget
Date
Venue
Weather
```

Recommended MVP:

Show only explanation and label.

Optional advanced UI:

```text
Match: 92
Budget: 100
Date: 100
Venue: 80
```

---

# 15. Deterministic First, LLM Second

Ranking should be deterministic.

The LLM may help with explanation wording, but must not control final scores.

Rules:

```text
Scores come from code.
Explanations may use LLM or templates.
LLM output must be validated.
Fallback template explanations must exist.
```

---

# 16. Demo Query Optimization

The ranking logic should work well for these demo prompts:

```text
Find electronic music events in Berlin this weekend under $100
Show Broadway shows in New York this month
Find startup networking events in San Francisco next week
Show football matches in London this weekend
Find art exhibitions in Paris this month
```

---

# 17. Implementation Files

Recommended files:

```text
app/services/scoring_service.py
app/services/recommendation_service.py
app/graph/nodes/rank_events.py
app/graph/nodes/generate_explanations.py
tests/test_ranking_node.py
tests/test_scoring_service.py
```

---

# 18. Test Cases

Bob should generate tests for:

```text
exact category match ranks highest
event within budget gets high affordability score
free event gets top affordability score
event outside date range ranks lower
missing price does not fail
missing weather does not fail
highest total score gets Best Overall
budget event gets Best Budget Pick
ranking output is sorted descending
```

---

# 19. Final Recommendation Goal

The final user experience should feel like:

```text
Pulse AI did not just find events.
It understood what I wanted and explained why these events are worth choosing.
```

That is the ranking and recommendation goal.
