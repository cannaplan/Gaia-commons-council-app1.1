"""API router for scenario management endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse

from app.scenario import create_and_run_scenario, get_scenario
from app.schemas import ScenarioCreate, ScenarioResponse

router = APIRouter()


@router.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    scenario: ScenarioCreate,
    response: Response
):
    """
    Create and run a new scenario.
    
    This endpoint accepts a scenario name and optional configuration,
    executes the scenario synchronously, and returns the result.
    
    In future PRs, this will support asynchronous background execution.
    
    Args:
        scenario: ScenarioCreate object with name and optional config
        response: FastAPI Response object for setting headers
        
    Returns:
        ScenarioResponse with the scenario execution results
    """
    # Create and run the scenario
    record = create_and_run_scenario(
        name=scenario.name,
        config=scenario.config
    )
    
    # Set Location header to point to the scenario resource
    response.headers["Location"] = f"/scenarios/{record['id']}"
    
    return record


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario_by_id(scenario_id: str):
    """
    Retrieve a scenario by its ID.
    
    Args:
        scenario_id: The unique identifier (UUID) of the scenario
        
    Returns:
        ScenarioResponse with the scenario data
        
    Raises:
        HTTPException: 404 if the scenario is not found
    """
    record = get_scenario(scenario_id)
    
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id '{scenario_id}' not found"
        )
    
    return record
