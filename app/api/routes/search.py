"""Search API routes – drives the full Pulse AI LangGraph workflow."""
from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.models.search import SearchRequest, SearchResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])

# Templates are initialised here but the directory path must match main.py.
# We reuse the same Jinja2Templates instance that is set on app.state in main.py
# when available; otherwise fall back to a local instance.
_templates = Jinja2Templates(directory="app/templates")

_MAX_QUERY_LENGTH = 300


# ---------------------------------------------------------------------------
# POST /api/search  – full workflow, returns JSON
# ---------------------------------------------------------------------------
@router.post("/", response_model=SearchResponse)
async def search_events(
    search_request: SearchRequest,
    request: Request,
) -> SearchResponse:
    """
    Search for events using a natural language query.

    Executes the full Pulse AI LangGraph pipeline:
    1. Parse query with IBM watsonx.ai LLM
    2. Validate search parameters
    3. Search events via Ticketmaster
    4. Normalize event data to internal schema
    5. Enrich venues with Geoapify nearby-places data
    6. Add OpenWeather forecast context
    7. Rank and score events (deterministic multi-factor)
    8. Generate AI explanations for each recommendation
    9. Prepare final response
    """
    started = time.perf_counter()
    try:
        workflow = request.app.state.workflow

        demo_mode = search_request.use_demo or search_request.demo_mode or settings.demo_mode

        initial_state: dict[str, Any] = {
            "raw_query": search_request.query,
            "city": search_request.city,
            "country": search_request.country,
            "category": search_request.category,
            "date_from": search_request.date_from,
            "date_to": search_request.date_to,
            "budget_max": search_request.budget_max,
            "demo_mode": demo_mode,
            "errors": [],
            "workflow_trace": [],
        }

        result = await workflow.ainvoke(initial_state)
        workflow_trace = [
            *result.get("workflow_trace", []),
            {
                "node_name": "api_search_route",
                "status": "completed",
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        ]

        return SearchResponse(
            success=True,
            summary=result.get("recommendation_summary", ""),
            events=result.get("ranked_events", []),
            workflow_trace=workflow_trace,
            errors=result.get("errors", []),
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception("Search workflow failed for query %r", search_request.query)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your search. Please try again.",
        ) from exc


# ---------------------------------------------------------------------------
# POST /api/search/htmx  – HTMX-friendly endpoint, returns HTML fragment
# ---------------------------------------------------------------------------
@router.post("/htmx", response_class=HTMLResponse)
async def search_events_htmx(request: Request) -> HTMLResponse:
    """
    HTMX variant: accepts form-encoded POST, returns rendered results.html fragment.
    The search form (search.html) targets this endpoint via hx-post="/api/search/htmx".
    """
    started = time.perf_counter()
    form = await request.form()
    query: str = form.get("query", "")
    city: str | None = form.get("city") or None
    category: str | None = form.get("category") or None
    date_from: str | None = form.get("date_from") or None
    date_to: str | None = form.get("date_to") or None
    use_demo = str(form.get("use_demo", "")).lower() in {"1", "true", "on", "yes"}

    if not query:
        return HTMLResponse(
            '<p class="text-red-600 font-medium">Please enter a search query.</p>',
            status_code=422,
        )

    # Guard: reject queries that exceed the maximum allowed length.
    if len(query) > _MAX_QUERY_LENGTH:
        return HTMLResponse(
            '<p class="text-red-600 font-medium">Search query is too long. Please keep it under 300 characters.</p>',
            status_code=422,
        )

    try:
        workflow = request.app.state.workflow

        initial_state: dict[str, Any] = {
            "raw_query": query,
            "city": city,
            "country": form.get("country") or None,
            "category": category,
            "date_from": date_from,
            "date_to": date_to,
            "budget_max": None,
            "demo_mode": use_demo or settings.demo_mode,
            "errors": [],
            "workflow_trace": [],
        }

        result = await workflow.ainvoke(initial_state)
        workflow_trace = [
            *result.get("workflow_trace", []),
            {
                "node_name": "htmx_search_route",
                "status": "completed",
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        ]

        templates = request.app.state.templates
        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "summary": result.get("recommendation_summary", "No results found."),
                "events": result.get("ranked_events", []),
                "errors": result.get("errors", []),
                "workflow_trace": workflow_trace,
            },
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception("HTMX search failed for query %r", query)
        # Never reflect exception text into HTML — XSS risk.
        return HTMLResponse(
            '<p class="text-red-600 font-medium">Search failed. Please try again.</p>',
            status_code=500,
        )


# ---------------------------------------------------------------------------
# GET /api/search/demo  – demo results without any API calls
# ---------------------------------------------------------------------------
@router.get("/demo")
async def search_demo(request: Request) -> dict[str, Any]:
    """Return demo search results without hitting live APIs."""
    workflow = request.app.state.workflow

    initial_state: dict[str, Any] = {
        "raw_query": "rock concerts in London this weekend",
        "city": "London",
        "country": "GB",
        "category": "Music",
        "demo_mode": True,
        "errors": [],
        "workflow_trace": [],
    }

    result = await workflow.ainvoke(initial_state)

    return {
        "success": True,
        "summary": result.get("recommendation_summary", ""),
        "events": result.get("ranked_events", [])[:5],
        "mode": "demo",
    }
