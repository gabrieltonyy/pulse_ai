"""Calendar export-related Pydantic models for Pulse AI."""
from pydantic import BaseModel


class CalendarExportRequest(BaseModel):
    """Request to export an event to calendar format."""
    
    event_id: str


class CalendarExportResult(BaseModel):
    """Result of calendar export operation."""
    
    event_id: str
    filename: str
    content_type: str = "text/calendar"
    download_url: str


# Made with Bob