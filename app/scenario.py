"""Scenario runner module for executing scenarios with SQLite persistence."""

import time
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Session, select, delete
from sqlalchemy import Column, JSON

from app.db import engine


class Scenario(SQLModel, table=True):
    """
    SQLModel for scenario persistence in SQLite database.
    
    Attributes:
        id: Unique identifier (UUID) - primary key
        name: Scenario name
        status: Execution status (e.g., "finished", "running", "failed")
        result: Result payload as JSON (dict)
        started_at: ISO timestamp when scenario started
        finished_at: ISO timestamp when scenario finished
    """
    id: str = Field(primary_key=True, max_length=36)
    name: str = Field(max_length=255)
    status: str = Field(max_length=50)
    result: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    started_at: str
    finished_at: Optional[str] = None


def clear_scenario_store():
    """
    Clears the scenario store (for backward compatibility with tests).
    
    This deletes all scenario records from the database.
    """
    # Use bulk delete for efficiency
    with Session(engine) as session:
        session.exec(delete(Scenario))
        session.commit()

def run_scenario(name: str, config: Optional[dict] = None) -> dict:
    """
    Execute a scenario with the given name and configuration.
    
    This is a simple synchronous runner that simulates work and returns
    a result dict. In future PRs, this will be extended with DB persistence
    and background queue support.
    
    Args:
        name: The name of the scenario to run
        config: Optional configuration dictionary for the scenario
        
    Returns:
        A dictionary containing:
            - id: Unique identifier (UUID4)
            - name: Scenario name
            - status: Execution status (always "finished" for now)
            - result: Result payload with summary and input config
            - started_at: ISO timestamp when scenario started
            - finished_at: ISO timestamp when scenario finished
    """
    started_at = datetime.now(timezone.utc)
    scenario_id = str(uuid4())
    
    # Simulate some work (small deterministic computation)
    time.sleep(0.1)  # Small sleep to simulate processing
    
    # Create result payload
    result_payload = {
        "summary": "demo result",
        "input_config": config or {}
    }
    
    finished_at = datetime.now(timezone.utc)
    
    return {
        "id": scenario_id,
        "name": name,
        "status": "finished",
        "result": result_payload,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat()
    }

def create_and_run_scenario(name: str, config: Optional[dict] = None) -> dict:
    """
    Create and execute a scenario, storing it in the SQLite database.
    
    This function runs the scenario synchronously and stores the result
    in the database using SQLModel.
    
    Args:
        name: The name of the scenario to run
        config: Optional configuration dictionary for the scenario
        
    Returns:
        A dictionary containing the scenario record with id, name, status,
        result, started_at, and finished_at fields
        
    Raises:
        Exception: If database operations fail
    """
    # Run the scenario (synchronous execution)
    record = run_scenario(name=name, config=config)
    
    try:
        # Create Scenario model instance from the record
        scenario = Scenario(
            id=record["id"],
            name=record["name"],
            status=record["status"],
            result=record["result"],
            started_at=record["started_at"],
            finished_at=record["finished_at"]
        )
        
        # Persist to database
        with Session(engine) as session:
            session.add(scenario)
            session.commit()
    except Exception as e:
        # Log the error and re-raise
        raise Exception(f"Failed to persist scenario to database: {str(e)}") from e
    
    return record
def get_scenario(scenario_id: str) -> Optional[dict]:
    """
    Retrieve a scenario record from the SQLite database.
    
    Args:
        scenario_id: The unique identifier (UUID) of the scenario
        
    Returns:
        The scenario record dictionary if found, None otherwise
        
    Raises:
        Exception: If database query fails
    """
    try:
        with Session(engine) as session:
            statement = select(Scenario).where(Scenario.id == scenario_id)
            scenario = session.exec(statement).first()
            
            if scenario is None:
                return None
            
            # Convert SQLModel to dict matching the expected response shape
            return {
                "id": scenario.id,
                "name": scenario.name,
                "status": scenario.status,
                "result": scenario.result,
                "started_at": scenario.started_at,
                "finished_at": scenario.finished_at
            }
    except Exception as e:
        # Log the error and re-raise
        raise Exception(f"Failed to retrieve scenario from database: {str(e)}") from e

