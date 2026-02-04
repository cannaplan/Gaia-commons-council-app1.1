"""Task management module for background scenario execution."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, status
from sqlmodel import SQLModel, Field, Session, select

from app.db import engine


class Task(SQLModel, table=True):
    """SQLModel for storing task execution records in the database."""
    
    task_id: str = Field(primary_key=True)
    scenario_id: str
    status: str  # pending, running, finished, failed
    error: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


def create_task_record(scenario_id: str) -> dict:
    """
    Create a new task record in the database.
    
    Args:
        scenario_id: The ID of the scenario to run
        
    Returns:
        A dictionary containing the task record with task_id, scenario_id,
        status, error, and timestamp fields
    """
    task_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    task = Task(
        task_id=task_id,
        scenario_id=scenario_id,
        status="pending",
        created_at=created_at
    )
    
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
    
    return {
        "task_id": task.task_id,
        "scenario_id": task.scenario_id,
        "status": task.status,
        "error": task.error,
        "created_at": task.created_at,
        "started_at": task.started_at,
        "finished_at": task.finished_at
    }


def get_task_record(task_id: str) -> dict:
    """
    Retrieve a task record from the database.
    
    Args:
        task_id: The unique identifier of the task
        
    Returns:
        A dictionary containing the task record
        
    Raises:
        HTTPException: 404 if the task is not found
    """
    with Session(engine) as session:
        statement = select(Task).where(Task.task_id == task_id)
        task = session.exec(statement).first()
        
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found"
            )
        
        return {
            "task_id": task.task_id,
            "scenario_id": task.scenario_id,
            "status": task.status,
            "error": task.error,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "finished_at": task.finished_at
        }


def _update_task(task_id: str, patch: dict) -> dict:
    """
    Update a task record in the database.
    
    Args:
        task_id: The unique identifier of the task
        patch: Dictionary of fields to update
        
    Returns:
        The updated task record as a dictionary
    """
    with Session(engine) as session:
        statement = select(Task).where(Task.task_id == task_id)
        task = session.exec(statement).first()
        
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found"
            )
        
        # Update fields from patch
        for key, value in patch.items():
            setattr(task, key, value)
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return {
            "task_id": task.task_id,
            "scenario_id": task.scenario_id,
            "status": task.status,
            "error": task.error,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "finished_at": task.finished_at
        }


def run_scenario_task(scenario_id: str, task_id: str) -> None:
    """
    Background worker function to execute a scenario.
    
    This function is invoked from FastAPI BackgroundTasks. It:
    1. Marks the task and scenario as running
    2. Calls the existing run_scenario() function to execute the scenario
    3. Persists the scenario result and status to the database
    4. Updates the task record with completion status
    5. Handles exceptions and marks failed tasks
    
    Args:
        scenario_id: The ID of the scenario to run
        task_id: The ID of the task tracking this execution
    """
    from app.scenario import run_scenario, Scenario
    
    started_at = datetime.now(timezone.utc).isoformat()
    
    try:
        # Mark task as running
        _update_task(task_id, {
            "status": "running",
            "started_at": started_at
        })
        
        # Mark scenario as running
        with Session(engine) as session:
            statement = select(Scenario).where(Scenario.id == scenario_id)
            scenario = session.exec(statement).first()
            
            if scenario is None:
                raise Exception(f"Scenario with id '{scenario_id}' not found")
            
            scenario.status = "running"
            scenario.started_at = started_at
            session.add(scenario)
            session.commit()
        
        # Get scenario config from database
        with Session(engine) as session:
            statement = select(Scenario).where(Scenario.id == scenario_id)
            scenario = session.exec(statement).first()
            config = scenario.config if scenario else None
            name = scenario.name if scenario else "unknown"
        
        # Run the scenario (this is synchronous and returns the result)
        result = run_scenario(name=name, config=config)
        
        # Update scenario with result and finished status
        finished_at = datetime.now(timezone.utc).isoformat()
        with Session(engine) as session:
            statement = select(Scenario).where(Scenario.id == scenario_id)
            scenario = session.exec(statement).first()
            
            if scenario:
                scenario.status = "finished"
                scenario.result = result["result"]
                scenario.finished_at = finished_at
                session.add(scenario)
                session.commit()
        
        # Mark task as finished
        _update_task(task_id, {
            "status": "finished",
            "finished_at": finished_at
        })
        
    except Exception as e:
        # Mark task as failed with error message
        finished_at = datetime.now(timezone.utc).isoformat()
        _update_task(task_id, {
            "status": "failed",
            "error": str(e),
            "finished_at": finished_at
        })
        
        # Mark scenario as failed
        try:
            with Session(engine) as session:
                statement = select(Scenario).where(Scenario.id == scenario_id)
                scenario = session.exec(statement).first()
                
                if scenario:
                    scenario.status = "failed"
                    scenario.finished_at = finished_at
                    session.add(scenario)
                    session.commit()
        except Exception:
            # If we can't update the scenario, at least the task status is correct
            pass
