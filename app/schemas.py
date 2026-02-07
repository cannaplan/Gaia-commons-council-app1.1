"""Pydantic models for API request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScenarioCreate(BaseModel):
    """Request schema for creating a new scenario."""
    
    name: str = Field(..., min_length=1)
    config: Optional[dict] = None


class ScenarioResult(BaseModel):
    """Result data from scenario execution."""
    
    summary: str
    input_config: dict = Field(default_factory=dict)


class ScenarioResponse(BaseModel):
    """Response schema for scenario data."""
    
    id: str
    name: str
    status: str
    started_at: datetime
    finished_at: datetime
    result: ScenarioResult
