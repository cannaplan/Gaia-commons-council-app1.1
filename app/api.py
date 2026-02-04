"""API router for scenario management endpoints."""

from fastapi import APIRouter, HTTPException, Response, status, BackgroundTasks

from app.scenario import create_scenario, get_scenario
from app.tasks import create_task_record, get_task_record, run_scenario_task
from app.schemas import ScenarioCreate, ScenarioResponse, TaskResponse, RunScenarioResponse

router = APIRouter()


@router.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario_endpoint(
    scenario: ScenarioCreate,
    response: Response
):
    """
    Create a new scenario without executing it.
    
    This endpoint creates a scenario record in the database with status "pending".
    To execute the scenario, use POST /scenarios/{scenario_id}/run.
    
    Args:
        scenario: ScenarioCreate object with name and optional config
        response: FastAPI Response object for setting headers
        
    Returns:
        ScenarioResponse with the scenario data (status: "pending")
    """
    # Create the scenario record in the database
    record = create_scenario(
        name=scenario.name,
        config=scenario.config
    )
    
    # Set Location header to point to the scenario resource
    response.headers["Location"] = f"/scenarios/{record['id']}"
    
    return record


@router.post("/scenarios/{scenario_id}/run", response_model=RunScenarioResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_scenario_endpoint(
    scenario_id: str,
    background_tasks: BackgroundTasks
):
    """
    Enqueue a scenario for background execution.
    
    This endpoint creates a task record and schedules the scenario to run
    in the background using FastAPI BackgroundTasks. The task ID can be used
    to poll for completion status via GET /scenarios/tasks/{task_id}.
    
    Args:
        scenario_id: The unique identifier of the scenario to run
        background_tasks: FastAPI BackgroundTasks for scheduling execution
        
    Returns:
        RunScenarioResponse with task_id, scenario_id, and status
        
    Raises:
        HTTPException: 404 if the scenario is not found
    """
    # Verify scenario exists
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id '{scenario_id}' not found"
        )
    
    # Create a task record
    task = create_task_record(scenario_id)
    
    # Schedule background execution
    background_tasks.add_task(run_scenario_task, scenario_id, task["task_id"])
    
    return {
        "task_id": task["task_id"],
        "scenario_id": scenario_id,
        "status": task["status"]
    }


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


@router.get("/scenarios/tasks/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: str):
    """
    Retrieve a task by its ID.
    
    This endpoint returns the status of a background task, which can be used
    to poll for completion of a scenario execution.
    
    Args:
        task_id: The unique identifier (UUID) of the task
        
    Returns:
        TaskResponse with the task status and metadata
        
    Raises:
        HTTPException: 404 if the task is not found
    """
    # get_task_record raises HTTPException if not found
    task = get_task_record(task_id)
    return task

