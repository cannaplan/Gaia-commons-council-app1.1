"""Pydantic models for API request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScenarioCreate(BaseModel):
    """Request model for creating a new scenario."""
    
    name: str = Field(..., description="Name of the scenario to run")
    config: Optional[dict] = Field(None, description="Optional configuration dictionary")


class ScenarioResult(BaseModel):
    """Model representing the result of a scenario execution."""
    
    summary: str = Field(..., description="Summary of the scenario result")
    input_config: Optional[dict] = Field(None, description="The configuration used for the scenario")


class ScenarioResponse(BaseModel):
    """Response model for scenario data."""
    
    id: str = Field(..., description="Unique identifier (UUID) for the scenario")
    name: str = Field(..., description="Name of the scenario")
    status: str = Field(..., description="Status of the scenario execution (e.g., 'finished')")
    started_at: datetime = Field(..., description="Timestamp when the scenario started")
    finished_at: datetime = Field(..., description="Timestamp when the scenario finished")
    result: ScenarioResult = Field(..., description="Result payload of the scenario execution")
