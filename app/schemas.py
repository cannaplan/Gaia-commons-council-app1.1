"""Pydantic models for API request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScenarioCreate(BaseModel):
    """Request model for creating a new scenario."""
    
    name: str = Field(..., min_length=1, description="Name of the scenario to run")
    config: Optional[dict] = Field(None, description="Optional configuration dictionary")


class ScenarioResult(BaseModel):
    """Model representing the result of a scenario execution."""
    
    summary: str = Field(..., description="Summary of the scenario result")
    input_config: Optional[dict] = Field(None, description="The configuration used for the scenario")


class ScenarioResponse(BaseModel):
    """Response model for scenario data."""
    
    id: str = Field(..., description="Unique identifier (UUID) for the scenario")
    name: str = Field(..., description="Name of the scenario")
    status: str = Field(..., description="Status of the scenario execution (e.g., 'pending', 'running', 'finished', 'failed')")
    config: Optional[dict] = Field(None, description="Configuration dictionary for the scenario")
    started_at: Optional[datetime] = Field(None, description="Timestamp when the scenario started")
    finished_at: Optional[datetime] = Field(None, description="Timestamp when the scenario finished")
    result: Optional[ScenarioResult] = Field(None, description="Result payload of the scenario execution")


class TaskResponse(BaseModel):
    """Response model for task data."""
    
    task_id: str = Field(..., description="Unique identifier (UUID) for the task")
    scenario_id: str = Field(..., description="ID of the scenario being executed")
    status: str = Field(..., description="Status of the task execution (e.g., 'pending', 'running', 'finished', 'failed')")
    error: Optional[str] = Field(None, description="Error message if task failed")
    created_at: datetime = Field(..., description="Timestamp when the task was created")
    started_at: Optional[datetime] = Field(None, description="Timestamp when the task started")
    finished_at: Optional[datetime] = Field(None, description="Timestamp when the task finished")


class TaskCreateResponse(BaseModel):
    """Response model for task creation."""
    
    task_id: str = Field(..., description="Unique identifier (UUID) for the task")
    scenario_id: str = Field(..., description="ID of the scenario being executed")
    status: str = Field(..., description="Status of the task (will be 'pending' initially)")
