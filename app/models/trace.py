"""Workflow trace-related Pydantic models for Pulse AI."""
from pydantic import BaseModel
from typing import Optional, Literal


class WorkflowTraceItem(BaseModel):
    """Represents a single step in the workflow execution trace."""
    
    node_name: str
    status: Literal["pending", "running", "completed", "failed", "skipped"]
    tool_called: Optional[str] = None
    provider: Optional[str] = None
    fallback_used: bool = False
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None


# Made with Bob