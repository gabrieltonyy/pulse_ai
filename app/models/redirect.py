"""Ticket redirect-related Pydantic models for Pulse AI."""
from pydantic import BaseModel


class TicketRedirectRequest(BaseModel):
    """Request to redirect to ticket purchase page."""
    
    event_id: str


class TicketRedirectResult(BaseModel):
    """Result of ticket redirect operation."""
    
    event_id: str
    provider: str
    redirect_url: str
    external_url: str
    safe: bool


# Made with Bob