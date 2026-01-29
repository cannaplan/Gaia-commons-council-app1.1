"""API router for scenario endpoints."""

from fastapi import APIRouter, HTTPException, Response, status

from app.scenario import create_and_run_scenario, get_scenario
from app.schemas import ScenarioCreate, ScenarioResponse

router = APIRouter()


@router.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(scenario: ScenarioCreate, response: Response):
    """
    Create and run a new scenario.
    
    Accepts a JSON body with scenario name and optional configuration.
    Returns the scenario record with execution details and a Location header.
    
    Note: This is a synchronous endpoint so FastAPI runs it in a threadpool,
    preventing the blocking time.sleep in run_scenario from blocking the event loop.
    """
    # Create and run the scenario
    record = create_and_run_scenario(name=scenario.name, config=scenario.config)
    
    # Set Location header to point to the new resource
    response.headers["Location"] = f"/scenarios/{record['id']}"
    
    return record


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def get_scenario_by_id(scenario_id: str):
    """
    Retrieve a scenario by its unique identifier.
    
    Returns the scenario record if found, otherwise returns 404.
    """
    record = get_scenario(scenario_id)
    
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id '{scenario_id}' not found"
        )
    
    return record
