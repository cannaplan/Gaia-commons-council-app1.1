"""Task management module for background scenario execution."""

import time
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Session, select

from app.db import engine
from app.scenario import Scenario, run_scenario


class Task(SQLModel, table=True):
    """SQLModel for tracking background task execution."""
    
    task_id: str = Field(primary_key=True)
    scenario_id: str
    status: str  # "pending", "running", "finished", "failed"
    error: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


def create_task_record(scenario_id: str) -> dict:
    """
    Create a new task record for a scenario execution.
    
    Args:
        scenario_id: The ID of the scenario to execute
        
    Returns:
        Dictionary containing task_id, scenario_id, status, and timestamps
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
    Retrieve a task record by its ID.
    
    Args:
        task_id: The unique identifier of the task
        
    Returns:
        Dictionary containing task data
        
    Raises:
        FileNotFoundError: If the task is not found
    """
    with Session(engine) as session:
        statement = select(Task).where(Task.task_id == task_id)
        task = session.exec(statement).first()
        
        if task is None:
            raise FileNotFoundError(f"Task with id '{task_id}' not found")
        
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
    Update a task record with the given patch data.
    
    Args:
        task_id: The unique identifier of the task
        patch: Dictionary containing fields to update
        
    Returns:
        Dictionary containing updated task data
    """
    with Session(engine) as session:
        statement = select(Task).where(Task.task_id == task_id)
        task = session.exec(statement).first()
        
        if task is None:
            raise FileNotFoundError(f"Task with id '{task_id}' not found")
        
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
    Execute a scenario in the background and update task/scenario status.
    
    This function is invoked by FastAPI BackgroundTasks. It:
    1. Updates task and scenario to "running" status
    2. Calls run_scenario() to execute the scenario
    3. Persists result to Scenario.result and updates status
    4. Updates task record with final status
    5. Handles exceptions and marks task/scenario as failed if errors occur
    
    Args:
        scenario_id: The ID of the scenario to execute
        task_id: The ID of the task tracking this execution
    """
    started_at = datetime.now(timezone.utc).isoformat()
    
    try:
        # Update task to running
        _update_task(task_id, {
            "status": "running",
            "started_at": started_at
        })
        
        # Update scenario to running
        with Session(engine) as session:
            statement = select(Scenario).where(Scenario.id == scenario_id)
            scenario = session.exec(statement).first()
            
            if scenario is None:
                raise FileNotFoundError(f"Scenario with id '{scenario_id}' not found")
            
            scenario.status = "running"
            scenario.started_at = started_at
            session.add(scenario)
            session.commit()
        
        # Retrieve scenario config from DB
        with Session(engine) as session:
            statement = select(Scenario).where(Scenario.id == scenario_id)
            scenario = session.exec(statement).first()
            scenario_name = scenario.name
            scenario_config = scenario.config
        
        # Run the scenario (synchronous execution)
        result = run_scenario(name=scenario_name, config=scenario_config)
        
        finished_at = datetime.now(timezone.utc).isoformat()
        
        # Update scenario with result
        with Session(engine) as session:
            statement = select(Scenario).where(Scenario.id == scenario_id)
            scenario = session.exec(statement).first()
            scenario.status = "finished"
            scenario.result = result["result"]
            scenario.finished_at = finished_at
            session.add(scenario)
            session.commit()
        
        # Update task to finished
        _update_task(task_id, {
            "status": "finished",
            "finished_at": finished_at
        })
        
    except Exception as e:
        # Mark task and scenario as failed
        finished_at = datetime.now(timezone.utc).isoformat()
        error_message = str(e)
        
        # Update task to failed
        _update_task(task_id, {
            "status": "failed",
            "error": error_message,
            "finished_at": finished_at
        })
        
        # Update scenario to failed
        with Session(engine) as session:
            statement = select(Scenario).where(Scenario.id == scenario_id)
            scenario = session.exec(statement).first()
            
            if scenario is not None:
                scenario.status = "failed"
                scenario.finished_at = finished_at
                session.add(scenario)
                session.commit()
