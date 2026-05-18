from __future__ import annotations
from typing import Any
from app.graph.workflow import create_pulse_workflow

async def pulse_search_events(
    query: str,
    city: str | None = None,
    country: str | None = None,
    state: str | None = None,
    category: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    budget_max: float | None = None,
    use_demo: bool = False,
)   -> dict[str, Any]:
    """
    search for events using the pulse AI recommendation engine.

        Args:
        query:      Natural language search query (required).
        city:       City name – optional, can be extracted from the query.
        country:    ISO 3166-1 alpha-2 country code (default: "US").
        category:   Event category, e.g. Music, Sports, Arts.
        date_from:  Start date in ISO format YYYY-MM-DD.
        date_to:    End date in ISO format YYYY-MM-DD.
        budget_max: Maximum ticket price in USD.
        use_demo:   When True, use bundled demo data instead of live APIs.
 
    Returns:
        Dictionary with keys:
        - success (bool)
        - summary (str)   – human-readable recommendation summary
        - events (list)   – ranked event objects
        - workflow_trace (list) – node execution trace
        - errors (list)   – any non-fatal errors encountered
    """
    if not query or len(query.strip()) < 2:
        return {
            "success": False,
            "message": "Query must be at least 2 characters.",
            "events": [],
            "workflow_trace": [],
            "errors": [{"node": "pulse_search_events", "error": "invalid query"}],
        }

    workflow = create_pulse_workflow()
 
    initial_state: dict[str, Any] = {
        "raw_query": query,
        "city": city,
        "country": country or "US",
        "category": category,
        "date_from": date_from,
        "date_to": date_to,
        "budget_max": budget_max,
        "use_demo_data": use_demo,
        "errors": [],
        "workflow_trace": [],
    }
 
    result = await workflow.ainvoke(initial_state)
 
    return {
        "success": True,
        "summary": result.get("recommendation_summary", ""),
        "events": result.get("ranked_events", []),
        "workflow_trace": result.get("workflow_trace", []),
        "errors": result.get("errors", []),
    }
