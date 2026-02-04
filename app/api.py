"""API router for scenario management endpoints."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, status
from sqlmodel import Session, select

from app.db import engine
from app.scenario import Scenario, get_scenario
from app.tasks import Task, create_task_record, get_task_record, run_scenario_task
from app.schemas import ScenarioCreate, ScenarioResponse, TaskCreateResponse, TaskResponse

router = APIRouter()


@router.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    scenario: ScenarioCreate,
    response: Response
):
    """
    Create a new scenario without executing it.
    
    This endpoint creates a scenario record in the database with the provided
    name and configuration. The scenario is not executed immediately.
    Use POST /scenarios/{scenario_id}/run to execute it asynchronously.
    
    Args:
        scenario: ScenarioCreate object with name and optional config
        response: FastAPI Response object for setting headers
        
    Returns:
        ScenarioResponse with the created scenario (status='pending')
    """
    scenario_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    # Create scenario record in database
    scenario_record = Scenario(
        id=scenario_id,
        name=scenario.name,
        status="pending",
        config=scenario.config,
        started_at=created_at
    )
    
    with Session(engine) as session:
        session.add(scenario_record)
        session.commit()
        session.refresh(scenario_record)
    
    # Set Location header to point to the scenario resource
    response.headers["Location"] = f"/scenarios/{scenario_id}"
    
    return {
        "id": scenario_record.id,
        "name": scenario_record.name,
        "status": scenario_record.status,
        "config": scenario_record.config,
        "started_at": scenario_record.started_at,
        "finished_at": scenario_record.finished_at,
        "result": scenario_record.result
    }


@router.post("/scenarios/{scenario_id}/run", response_model=TaskCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_scenario(
    scenario_id: str,
    background_tasks: BackgroundTasks
):
    """
    Enqueue a scenario for asynchronous execution.
    
    This endpoint creates a task record and schedules the scenario to run
    in the background using FastAPI BackgroundTasks.
    
    Args:
        scenario_id: The unique identifier of the scenario to run
        background_tasks: FastAPI BackgroundTasks for async execution
        
    Returns:
        TaskCreateResponse with task_id for polling status
        
    Raises:
        HTTPException: 404 if the scenario is not found
    """
    # Verify scenario exists
    with Session(engine) as session:
        statement = select(Scenario).where(Scenario.id == scenario_id)
        scenario = session.exec(statement).first()
        
        if scenario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario with id '{scenario_id}' not found"
            )
    
    # Create task record
    task = create_task_record(scenario_id)
    
    # Enqueue background task
    background_tasks.add_task(run_scenario_task, scenario_id, task["task_id"])
    
    return {
        "task_id": task["task_id"],
        "scenario_id": task["scenario_id"],
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
async def get_task_status(task_id: str):
    """
    Retrieve the status of a task by its ID.
    
    Args:
        task_id: The unique identifier (UUID) of the task
        
    Returns:
        TaskResponse with the task status and metadata
        
    Raises:
        HTTPException: 404 if the task is not found
    """
    try:
        task = get_task_record(task_id)
        return task
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

