"""Scenario runner module for executing scenarios.

This module now uses SQLite-backed storage via SQLModel for persistence.
The DATABASE_URL can be configured via environment variable.
"""

import json
import time
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from sqlmodel import select

from app.db import ScenarioModel, get_session


def run_scenario(name: str, config: Optional[dict] = None) -> dict:
    """
    Execute a scenario with the given name and configuration.
    
    This is a simple synchronous runner that simulates work and returns
    a result dict. 
    
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
    
    This function:
    1. Creates a DB row with status 'running', started_at timestamp, name and config
    2. Executes the scenario synchronously (inline, not via run_scenario)
    3. Updates the DB row with finished_at, status ('finished' or 'failed'), and result
    
    Args:
        name: The name of the scenario to run
        config: Optional configuration dictionary for the scenario
        
    Returns:
        A dictionary containing the scenario record with id, name, status,
        result, started_at, and finished_at fields, compatible with ScenarioResponse schema
    """
    scenario_id = str(uuid4())
    started_at = datetime.now(timezone.utc)
    
    # Create initial database record with status 'running'
    with get_session() as session:
        scenario_model = ScenarioModel(
            id=scenario_id,
            name=name,
            status="running",
            started_at=started_at,
            config=json.dumps(config) if config else None
        )
        session.add(scenario_model)
        # Note: session.commit() happens automatically in get_session context manager
    
    # Execute the scenario
    try:
        # Simulate some work (small deterministic computation)
        time.sleep(0.1)  # Small sleep to simulate processing
        
        # Create result payload
        result_payload = {
            "summary": "demo result",
            "input_config": config or {}
        }
        
        finished_at = datetime.now(timezone.utc)
        status = "finished"
        
    except Exception as e:
        # If scenario execution fails, mark as failed
        finished_at = datetime.now(timezone.utc)
        status = "failed"
        result_payload = {
            "summary": f"Scenario failed: {str(e)}",
            "input_config": config or {}
        }
    
    # Update database record with results
    with get_session() as session:
        scenario_model = session.get(ScenarioModel, scenario_id)
        if scenario_model:
            scenario_model.status = status
            scenario_model.finished_at = finished_at
            scenario_model.result = json.dumps(result_payload)
            session.add(scenario_model)
            # Note: session.commit() happens automatically in get_session context manager
    
    # Return dict compatible with ScenarioResponse schema
    return {
        "id": scenario_id,
        "name": name,
        "status": status,
        "result": result_payload,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat()
    }


def get_scenario(scenario_id: str) -> Optional[dict]:
    """
    Retrieve a scenario record from the SQLite database.
    
    Args:
        scenario_id: The unique identifier (UUID) of the scenario
        
    Returns:
        The scenario record dictionary if found, None otherwise.
        Returns a dict compatible with ScenarioResponse schema.
    """
    with get_session() as session:
        scenario_model = session.get(ScenarioModel, scenario_id)
        
        if scenario_model is None:
            return None
        
        # Parse JSON fields
        result = json.loads(scenario_model.result) if scenario_model.result else None
        
        # Format timestamps - SQLite stores datetime without timezone info
        # so we need to add UTC timezone back for consistency
        started_at = scenario_model.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        
        finished_at_str = None
        if scenario_model.finished_at:
            finished_at = scenario_model.finished_at
            if finished_at.tzinfo is None:
                finished_at = finished_at.replace(tzinfo=timezone.utc)
            finished_at_str = finished_at.isoformat()
        
        # Return dict compatible with ScenarioResponse schema
        return {
            "id": scenario_model.id,
            "name": scenario_model.name,
            "status": scenario_model.status,
            "result": result,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at_str
        }


def clear_scenario_store():
    """
    Clear all scenarios from the database.
    
    This is primarily used for test isolation to ensure a clean state
    between test runs. Uses a bulk delete operation for efficiency.
    """
    with get_session() as session:
        # Use bulk delete for efficiency
        scenarios = session.exec(select(ScenarioModel)).all()
        for scenario in scenarios:
            session.delete(scenario)
        # Note: session.commit() happens automatically in get_session context manager


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
    return kwargs
