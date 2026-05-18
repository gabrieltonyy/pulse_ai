"""Event detail, calendar export, and click-tracking routes."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories import EventRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])

EventIdPath = Annotated[str, Path(regex=r"^[a-zA-Z0-9_\-]{1,64}$")]


# ---------------------------------------------------------------------------
# GET /api/events/{event_id}  – event detail
# ---------------------------------------------------------------------------
@router.get("/{event_id}")
async def get_event(
    event_id: EventIdPath,
    session: AsyncSession = Depends(get_db),
):
    """Return detailed information about a specific saved event."""
    repo = EventRepository(session)
    event = await repo.get_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id!r} not found.")

    return event


# ---------------------------------------------------------------------------
# POST /api/events/{event_id}/track-click  – outbound click tracking
# ---------------------------------------------------------------------------
@router.post("/{event_id}/track-click")
async def track_click(
    event_id: EventIdPath,
    session: AsyncSession = Depends(get_db),
):
    """Record a user click-through for analytics."""
    try:
        repo = EventRepository(session)
        await repo.increment_click_count(event_id)
        return {"success": True, "event_id": event_id}
    except Exception as exc:  # noqa: BLE001
        # Click tracking must never surface errors to the user.
        logger.warning("Click tracking failed for %r: %s", event_id, exc)
        return {"success": False, "event_id": event_id}


# ---------------------------------------------------------------------------
# GET /api/events/{event_id}/calendar  – .ics export
# ---------------------------------------------------------------------------
@router.get("/{event_id}/calendar", response_class=PlainTextResponse)
async def export_calendar(
    event_id: EventIdPath,
    session: AsyncSession = Depends(get_db),
) -> PlainTextResponse:
    """
    Generate a standards-compliant iCalendar (.ics) file for the event.

    The response can be saved directly by the browser or imported into
    Google Calendar, Apple Calendar, Outlook, etc.
    """
    repo = EventRepository(session)
    event = await repo.get_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id!r} not found.")

    # Format datetimes for iCal (basic YYYYMMDDTHHMMSSZ)
    def _ical_dt(value) -> str:
        if isinstance(value, datetime):
            return value.strftime("%Y%m%dT%H%M%SZ")
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.strftime("%Y%m%dT%H%M%SZ")
            except ValueError:
                pass
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    start_dt = _ical_dt(getattr(event, "start_datetime", None))
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    title = _escape_ical(getattr(event, "title", "Event"))
    description = _escape_ical(getattr(event, "description", ""))
    location = _escape_ical(getattr(event, "venue_name", ""))
    url = getattr(event, "url", "") or ""

    ics_content = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Pulse AI//Event Calendar//EN\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:PUBLISH\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{event_id}@pulse-ai.com\r\n"
        f"DTSTAMP:{dtstamp}\r\n"
        f"DTSTART:{start_dt}\r\n"
        f"SUMMARY:{title}\r\n"
        f"DESCRIPTION:{description}\r\n"
        f"LOCATION:{location}\r\n"
        f"URL:{url}\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )

    return PlainTextResponse(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{event_id}.ics"',
        },
    )


def _escape_ical(value: str) -> str:
    """Escape special characters required by the iCal spec (RFC 5545)."""
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
