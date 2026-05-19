"""
Search Events Node - Searches for events using Ticketmaster API or demo data.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging
import time
from typing import Any

from app.config.settings import settings
from app.db.database import get_session_context
from app.db.repositories import ApiCacheRepository
from app.graph.state import PulseGraphState
from app.integrations.ticketmaster_client import TicketmasterClient
from app.services.demo_provider import DemoProvider


logger = logging.getLogger(__name__)


async def search_events_node(state: PulseGraphState) -> PulseGraphState:
    """
    Search for events using Ticketmaster API or demo data.
    
    Falls back to demo provider if:
    - Demo mode is enabled
    - Ticketmaster API key is not configured
    - Ticketmaster API call fails
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with events_raw
    """
    fallback_used = False
    provider = "ticketmaster"
    error_message = None
    cache_hit = False
    errors = list(state.get("errors", []))
    started = time.perf_counter()
    
    # Check if demo mode or no API key
    if state.get("demo_mode") or state.get("use_demo_data") or settings.demo_mode or not settings.ticketmaster_api_key:
        fallback_used = True
        provider = "demo"
        logger.info(
            "Event search using provider",
            extra={"provider": provider, "fallback_used": fallback_used},
        )
        events_raw = await _search_demo_events(state)
    else:
        # Try Ticketmaster API
        try:
            logger.info(
                "Event search using provider",
                extra={"provider": provider, "fallback_used": fallback_used},
            )
            cache_key, request_hash = _build_event_search_cache_key(state)
            cached_events = await _get_cached_events(cache_key)
            if cached_events is not None:
                cache_hit = True
                events_raw = cached_events
                logger.info(
                    "Ticketmaster event search cache hit",
                    extra={"provider": provider, "cache_hit": cache_hit},
                )
            else:
                logger.info(
                    "Ticketmaster event search cache miss",
                    extra={"provider": provider, "cache_hit": cache_hit},
                )
                events_raw = await _search_ticketmaster_events(state)
                await _cache_events(
                    cache_key=cache_key,
                    request_hash=request_hash,
                    events_raw=events_raw,
                )
        except Exception as e:
            # Fallback to demo on error
            error_message = str(e)
            fallback_used = True
            provider = "demo"
            logger.warning(
                "Event search provider failed; falling back to demo provider",
                extra={"provider": "ticketmaster", "fallback_provider": provider, "error_type": type(e).__name__},
            )
            events_raw = await _search_demo_events(state)

            errors.append({
                "node": "search_events",
                "error": error_message
            })

    logger.info(
        "Event search completed",
        extra={"provider": provider, "event_count": len(events_raw), "fallback_used": fallback_used},
    )
    
    # Add to workflow trace
    trace_entry = {
        "node_name": "search_events",
        "status": "completed",
        "tool_called": "pulse_search_events",
        "provider": provider,
        "fallback_used": fallback_used,
        "cache_hit": cache_hit,
        "events_count": len(events_raw),
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
    }
    
    if error_message:
        trace_entry["error_message"] = error_message

    return {
        **state,
        "events_raw": events_raw,
        "fallback_used": fallback_used,
        **({"errors": errors} if errors or "errors" in state else {}),
        "workflow_trace": [
            *state.get("workflow_trace", []),
            trace_entry,
        ],
    }


async def _search_ticketmaster_events(state: PulseGraphState) -> list[dict]:
    """Search events using Ticketmaster API."""
    client = TicketmasterClient()
    
    # Convert date strings back to date objects if present
    date_from = None
    date_to = None
    
    if state.get("date_from"):
        date_from = datetime.fromisoformat(state["date_from"]).date()
    if state.get("date_to"):
        date_to = datetime.fromisoformat(state["date_to"]).date()
    
    events = await client.search_events(
        city=state.get("city"),
        country=state.get("country"),
        category=state.get("category"),
        keyword=state.get("keyword"),
        date_from=date_from,
        date_to=date_to,
        size=10
    )
    
    return events


def _build_event_search_cache_key(state: PulseGraphState) -> tuple[str, str]:
    """Build a stable cache key from Ticketmaster search parameters."""
    payload = {
        "city": state.get("city"),
        "country": state.get("country"),
        "category": state.get("category"),
        "keyword": state.get("keyword"),
        "date_from": state.get("date_from"),
        "date_to": state.get("date_to"),
    }
    request_hash = _hash_cache_payload(payload)
    return f"ticketmaster:events:{request_hash}", request_hash


def _hash_cache_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


async def _get_cached_events(cache_key: str) -> list[dict] | None:
    try:
        async with get_session_context() as session:
            cache = await ApiCacheRepository(session).get_cache(cache_key)
            if not cache:
                return None
            return json.loads(cache.response_json)
    except Exception as exc:
        logger.warning(
            "Ticketmaster event cache read failed; continuing without cache",
            extra={"error_type": type(exc).__name__},
        )
        return None


async def _cache_events(
    cache_key: str,
    request_hash: str,
    events_raw: list[dict],
) -> None:
    try:
        async with get_session_context() as session:
            await ApiCacheRepository(session).set_cache(
                cache_key=cache_key,
                tool_name="pulse_search_events",
                provider="ticketmaster",
                request_hash=request_hash,
                response_json=json.dumps(events_raw, default=str),
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.cache_ttl_events),
            )
    except Exception as exc:
        logger.warning(
            "Ticketmaster event cache write failed; continuing without cache",
            extra={"error_type": type(exc).__name__},
        )


async def _search_demo_events(state: PulseGraphState) -> list[dict]:
    """Search events using demo provider."""
    demo_provider = DemoProvider()
    
    # Convert date strings back to date objects if present
    date_from = None
    date_to = None
    
    if state.get("date_from"):
        date_from = datetime.fromisoformat(state["date_from"]).date()
    if state.get("date_to"):
        date_to = datetime.fromisoformat(state["date_to"]).date()
    
    events = demo_provider.search_events(
        city=state.get("city"),
        category=state.get("category"),
        date_from=date_from,
        date_to=date_to,
        budget_max=state.get("budget_max")
    )
    
    # Convert Event objects to dicts
    return [event.model_dump() for event in events]

# Made with Bob
