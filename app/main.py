"""Pulse AI – FastAPI application entry point."""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes.events import router as events_router
from app.api.routes.search import router as search_router

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Pulse AI",
    description=(
        "AI-powered event discovery and recommendation platform. "
        "Combines IBM watsonx.ai, Ticketmaster, Geoapify, and OpenWeather "
        "through a LangGraph workflow."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---------------------------------------------------------------------------
# Templates (shared via app.state so routes can reuse the same instance)
# ---------------------------------------------------------------------------
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(search_router)
app.include_router(events_router)


# ---------------------------------------------------------------------------
# Core pages
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request) -> HTMLResponse:
    """Render the main search page."""
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/health", tags=["system"])
async def health() -> dict:
    """Basic health-check endpoint."""
    return {"status": "healthy", "service": "pulse-ai"}


# ---------------------------------------------------------------------------
# Startup / shutdown events
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def on_startup() -> None:  # noqa: RUF029
    logger.info("Pulse AI starting up…")


@app.on_event("shutdown")
async def on_shutdown() -> None:  # noqa: RUF029
    logger.info("Pulse AI shutting down.")