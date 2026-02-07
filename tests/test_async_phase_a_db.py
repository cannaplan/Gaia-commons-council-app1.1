"""Integration tests for Phase A: DB-backed async scenario execution."""

import time
import pytest
from fastapi.testclient import TestClient

from app.db import init_db
from app import scenario
from app.main import app

# Initialize database tables (DATABASE_URL is set in conftest.py)
init_db()

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_scenario_store():
    """Clear the scenario store before each test to ensure test isolation."""
    scenario.clear_scenario_store()
    yield
    scenario.clear_scenario_store()


def test_async_scenario_creation_and_execution():
    """
    Test the full async flow: create scenario, enqueue run, poll task status.
    
    This test verifies:
    1. POST /scenarios creates a scenario with status "pending"
    2. POST /scenarios/{id}/run returns a task_id with status "pending"
    3. Background task executes and updates scenario status to "finished"
    4. GET /scenarios/{id} returns updated status and result
    5. GET /scenarios/tasks/{task_id} returns task status
    """
    # Step 1: Create a scenario (without executing)
    scenario_data = {
        "name": "async-test-scenario",
        "config": {"param1": "value1", "param2": 42}
    }
    
    create_response = client.post("/scenarios", json=scenario_data)
    
    # Assert 201 Created status
    assert create_response.status_code == 201
    
    # Assert response contains expected fields
    create_json = create_response.json()
    assert "id" in create_json
    scenario_id = create_json["id"]
    assert create_json["name"] == "async-test-scenario"
    assert create_json["status"] == "pending"
    assert create_json["config"] == {"param1": "value1", "param2": 42}
    assert create_json["result"] is None
    assert create_json["finished_at"] is None
    
    # Assert Location header is set
    assert "Location" in create_response.headers
    assert create_response.headers["Location"] == f"/scenarios/{scenario_id}"
    
    # Step 2: Enqueue the scenario run
    run_response = client.post(f"/scenarios/{scenario_id}/run")
    
    # Assert 202 Accepted status
    assert run_response.status_code == 202
    
    # Assert response contains task_id
    run_json = run_response.json()
    assert "task_id" in run_json
    task_id = run_json["task_id"]
    assert run_json["scenario_id"] == scenario_id
    assert run_json["status"] == "pending"
    
    # Step 3: Poll task status until finished (with timeout)
    timeout_seconds = 5.0
    poll_interval_seconds = 0.1
    task_status = "pending"
    start_time = time.monotonic()
    
    while (time.monotonic() - start_time) < timeout_seconds and task_status not in ["finished", "failed"]:
        time.sleep(poll_interval_seconds)
        task_response = client.get(f"/scenarios/tasks/{task_id}")
        assert task_response.status_code == 200
        
        task_json = task_response.json()
        task_status = task_json["status"]
    
    # Assert task finished successfully
    assert task_status == "finished", f"Task did not finish in time. Status: {task_status}"
    assert task_json["error"] is None
    assert task_json["scenario_id"] == scenario_id
    assert task_json["started_at"] is not None
    assert task_json["finished_at"] is not None
    
    # Step 4: Verify scenario was updated
    scenario_response = client.get(f"/scenarios/{scenario_id}")
    assert scenario_response.status_code == 200
    
    scenario_json = scenario_response.json()
    assert scenario_json["id"] == scenario_id
    assert scenario_json["name"] == "async-test-scenario"
    assert scenario_json["status"] == "finished"
    assert scenario_json["config"] == {"param1": "value1", "param2": 42}
    assert scenario_json["result"] is not None
    assert scenario_json["result"]["summary"] == "demo result"
    assert scenario_json["result"]["input_config"] == {"param1": "value1", "param2": 42}
    assert scenario_json["finished_at"] is not None


def test_run_nonexistent_scenario():
    """Test that running a non-existent scenario returns 404."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    
    response = client.post(f"/scenarios/{non_existent_id}/run")
    
    # Assert 404 Not Found status
    assert response.status_code == 404
    
    # Assert error message is present
    response_json = response.json()
    assert "detail" in response_json
    assert non_existent_id in response_json["detail"]


def test_get_nonexistent_task():
    """Test that getting a non-existent task returns 404."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    
    response = client.get(f"/scenarios/tasks/{non_existent_id}")
    
    # Assert 404 Not Found status
    assert response.status_code == 404
    
    # Assert error message is present
    response_json = response.json()
    assert "detail" in response_json
    assert non_existent_id in response_json["detail"]


def test_scenario_without_config():
    """Test creating and running a scenario without optional config."""
    # Create a scenario with only name (no config)
    scenario_data = {
        "name": "simple-async-scenario"
    }
    
    # Create scenario
    create_response = client.post("/scenarios", json=scenario_data)
    assert create_response.status_code == 201
    
    create_json = create_response.json()
    scenario_id = create_json["id"]
    assert create_json["config"] is None
    
    # Run scenario
    run_response = client.post(f"/scenarios/{scenario_id}/run")
    assert run_response.status_code == 202
    
    task_id = run_response.json()["task_id"]
    
    # Poll for completion
    max_attempts = 20
    attempt = 0
    task_status = "pending"
    
    while attempt < max_attempts and task_status not in ["finished", "failed"]:
        time.sleep(0.5)
        task_response = client.get(f"/scenarios/tasks/{task_id}")
        task_status = task_response.json()["status"]
        attempt += 1
    
    assert task_status == "finished"
    
    # Verify scenario result
    scenario_response = client.get(f"/scenarios/{scenario_id}")
    scenario_json = scenario_response.json()
    assert scenario_json["status"] == "finished"
    assert scenario_json["result"]["input_config"] == {}


def test_prevent_concurrent_runs():
    """Test that running an already running/finished scenario is rejected."""
    # Create a scenario
    scenario_data = {"name": "concurrent-test-scenario"}
    create_response = client.post("/scenarios", json=scenario_data)
    assert create_response.status_code == 201
    scenario_id = create_response.json()["id"]
    
    # First run should succeed
    run_response1 = client.post(f"/scenarios/{scenario_id}/run")
    assert run_response1.status_code == 202
    task_id = run_response1.json()["task_id"]
    
    # Wait for completion
    timeout_seconds = 5.0
    poll_interval_seconds = 0.1
    task_status = "pending"
    start_time = time.monotonic()
    
    while (time.monotonic() - start_time) < timeout_seconds and task_status not in ["finished", "failed"]:
        time.sleep(poll_interval_seconds)
        task_response = client.get(f"/scenarios/tasks/{task_id}")
        task_status = task_response.json()["status"]
    
    assert task_status == "finished"
    
    # Try to run again - should fail with 409
    run_response2 = client.post(f"/scenarios/{scenario_id}/run")
    assert run_response2.status_code == 409
    assert "finished" in run_response2.json()["detail"].lower()
    assert "cannot be run" in run_response2.json()["detail"].lower()
