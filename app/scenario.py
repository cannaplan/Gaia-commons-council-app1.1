"""Scenario runner module for executing scenarios with SQLite persistence."""

import time
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from uuid import uuid4

from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy import Column, JSON

from app.db import engine


# SQLModel for Scenario persistence
class Scenario(SQLModel, table=True):
    """SQLModel for storing scenario execution records in the database."""
    
    id: str = Field(primary_key=True)
    name: str
    status: str
    config: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    result: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None

def clear_scenario_store():
    """
    Clears the scenario store (for backward compatibility with tests).
    
    This function is kept for backward compatibility but now clears the database
    instead of an in-memory store. For tests, use DATABASE_URL=sqlite:///:memory:
    and recreate tables via init_db() instead.
    """
    # For file-based DB, this would delete all records
    # For in-memory DB used in tests, tables are recreated per test
    with Session(engine) as session:
        # Delete all scenario records
        statement = select(Scenario)
        results = session.exec(statement).all()
        for scenario in results:
            session.delete(scenario)
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
    
    This function runs the scenario synchronously and persists the result
    in the database using SQLModel.
    
    Args:
        name: The name of the scenario to run
        config: Optional configuration dictionary for the scenario
        
    Returns:
        A dictionary containing the scenario record with id, name, status,
        result, created_at, started_at, and finished_at fields
    """
    # Run the scenario (synchronous execution)
    record = run_scenario(name=name, config=config)
    
    # Create a Scenario model instance from the result
    scenario = Scenario(
        id=record["id"],
        name=record["name"],
        status=record["status"],
        config=config,
        result=record["result"],
        created_at=record["started_at"],  # For sync execution, created and started are the same
        started_at=record["started_at"],
        finished_at=record["finished_at"]
    )
    
    # Persist to database
    with Session(engine) as session:
        session.add(scenario)
        session.commit()
        session.refresh(scenario)
    
    # Return as dict (same structure as before)
    return record
def get_scenario(scenario_id: str) -> Optional[dict]:
    """
    Retrieve a scenario record from the SQLite database.
    
    Args:
        scenario_id: The unique identifier (UUID) of the scenario
        
    Returns:
        The scenario record dictionary if found, None otherwise
    """
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
            "config": scenario.config,
            "result": scenario.result,
            "created_at": scenario.created_at,
            "started_at": scenario.started_at,
            "finished_at": scenario.finished_at
        }



def create_scenario(name: str, config: Optional[dict] = None) -> dict:
    """
    Create a scenario record in the database without executing it.
    
    This is used for the async flow where scenario creation and execution
    are separated. The scenario is created with status "pending" and will
    be executed later by a background task.
    
    Args:
        name: The name of the scenario to run
        config: Optional configuration dictionary for the scenario
        
    Returns:
        A dictionary containing the scenario record with id, name, status,
        config, created_at, and other fields
    """
    scenario_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    scenario = Scenario(
        id=scenario_id,
        name=name,
        status="pending",
        config=config,
        created_at=created_at
    )
    
    with Session(engine) as session:
        session.add(scenario)
        session.commit()
        session.refresh(scenario)
    
    return {
        "id": scenario.id,
        "name": scenario.name,
        "status": scenario.status,
        "config": scenario.config,
        "result": scenario.result,
        "created_at": scenario.created_at,
        "started_at": scenario.started_at,
        "finished_at": scenario.finished_at
    }



