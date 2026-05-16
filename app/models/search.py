"""Search-related Pydantic models for Pulse AI."""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class SearchIntent(BaseModel):
    """Structured meaning extracted from user query."""
    
    raw_query: str = Field(..., min_length=2, max_length=300)
    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    keyword: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    budget_max: Optional[float] = None
    currency: str = "USD"
    preferences: list[str] = []


class SearchRequest(BaseModel):
    """Request received from the UI/API."""
    
    query: str = Field(..., min_length=2, max_length=300)
    demo_mode: bool = False


class SearchValidationResult(BaseModel):
    """Result of search query validation."""
    
    is_valid: bool
    missing_fields: list[str] = []
    message: Optional[str] = None


# Made with Bob