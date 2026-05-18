"""Search-related Pydantic models for Pulse AI."""
from pydantic import BaseModel, Field
from pydantic import ConfigDict
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

    model_config = ConfigDict(populate_by_name=True)

    query: str = Field(..., min_length=2, max_length=300)
    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    budget_max: Optional[float] = None
    use_demo: bool = Field(default=False, alias="demo_mode")
    demo_mode: bool = False


class SearchResponse(BaseModel):
    """Response returned by the search API."""

    success: bool
    summary: str = ""
    events: list[dict] = []
    workflow_trace: list[dict] = []
    errors: list[dict | str] = []


class SearchValidationResult(BaseModel):
    """Result of search query validation."""
    
    is_valid: bool
    missing_fields: list[str] = []
    message: Optional[str] = None


# Made with Bob
