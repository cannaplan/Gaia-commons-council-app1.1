"""Scenario runner module for executing scenarios."""

import time
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Column, JSON, select
from app.db import get_session, engine

# SQLModel for scenario persistence
class Scenario(SQLModel, table=True):
    """SQLModel for storing scenario records in the database."""
    id: str = Field(primary_key=True)
    name: str
    status: str
    result: dict = Field(sa_column=Column(JSON))
    started_at: str
    finished_at: str

# TODO: Replace with SQLite database in PR #3
# In-memory registry for storing scenario records
_SCENARIO_STORE: Dict[str, dict] = {}

def clear_scenario_store():
    """
    Clears the scenario store (DB tables when DB is used).
    """
    # Clear the database tables
    from sqlmodel import Session
    with Session(engine) as session:
        # Delete all records from Scenario table
        scenarios = session.exec(select(Scenario)).all()
        for scenario in scenarios:
            session.delete(scenario)
        session.commit()
    
    # Also clear the in-memory store for backward compatibility
    _SCENARIO_STORE.clear()

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
    Create and execute a scenario, storing it in the database.
    
    This function runs the scenario synchronously and stores the result
    in the SQLite database.
    
    Args:
        name: The name of the scenario to run
        config: Optional configuration dictionary for the scenario
        
    Returns:
        A dictionary containing the scenario record with id, name, status,
        result, started_at, and finished_at fields
    """
    # Run the scenario (synchronous execution)
    record = run_scenario(name=name, config=config)
    
    # Persist to database
    from sqlmodel import Session
    with Session(engine) as session:
        scenario = Scenario(
            id=record["id"],
            name=record["name"],
            status=record["status"],
            result=record["result"],
            started_at=record["started_at"],
            finished_at=record["finished_at"]
        )
        session.add(scenario)
        session.commit()
    
    return record
def get_scenario(scenario_id: str) -> Optional[dict]:
    """
    Retrieve a scenario record from the database.
    
    Args:
        scenario_id: The unique identifier (UUID) of the scenario
        
    Returns:
        The scenario record dictionary if found, None otherwise
    """
    from sqlmodel import Session
    with Session(engine) as session:
        scenario = session.get(Scenario, scenario_id)
        if scenario is None:
            return None
        
        # Convert to dict matching the previous ScenarioResponse shape
        return {
            "id": scenario.id,
            "name": scenario.name,
            "status": scenario.status,
            "result": scenario.result,
            "started_at": scenario.started_at,
            "finished_at": scenario.finished_at
        }

def create_scenario_record(**kwargs) -> dict:
    """
    Placeholder for creating a scenario record in the database.
    
    This will be replaced with actual DB logic in later PRs.
    For now, it just returns the kwargs as-is.
    
    Args:
        **kwargs: Arbitrary keyword arguments representing scenario data
        
    Returns:
        The same data passed in
    """
    # TODO: Replace with actual DB persistence in PR #3
    return kwargs
