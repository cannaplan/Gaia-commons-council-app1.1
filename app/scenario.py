"""Scenario runner module for executing scenarios."""

import time
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


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
