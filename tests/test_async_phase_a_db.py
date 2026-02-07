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


def test_async_phase_a_db_flow():
    """
    Integration test for Phase A async flow with DB-backed BackgroundTasks.
    
    This test validates the complete async scenario execution flow:
    1. POST /scenarios creates a scenario record with config
    2. POST /scenarios/{id}/run enqueues a background task
    3. Polling GET /scenarios/tasks/{task_id} until finished
    4. GET /scenarios/{id} returns finished status and persisted result
    """
    # Step 1: Create a scenario (without executing it)
    scenario_data = {
        "name": "async-test-scenario",
        "config": {"param1": "test-value", "param2": 123}
    }
    
    create_response = client.post("/scenarios", json=scenario_data)
    
    # Assert 201 Created
    assert create_response.status_code == 201
    
    # Assert Location header is set
    assert "Location" in create_response.headers
    
    # Assert response contains scenario with pending status
    scenario_json = create_response.json()
    assert "id" in scenario_json
    scenario_id = scenario_json["id"]
    assert scenario_json["name"] == "async-test-scenario"
    assert scenario_json["status"] == "pending"
    assert scenario_json["config"] == {"param1": "test-value", "param2": 123}
    assert scenario_json["result"] is None
    assert create_response.headers["Location"] == f"/scenarios/{scenario_id}"
    
    # Step 2: Enqueue the scenario for execution
    run_response = client.post(f"/scenarios/{scenario_id}/run")
    
    # Assert 202 Accepted
    assert run_response.status_code == 202
    
    # Assert response contains task_id
    run_json = run_response.json()
    assert "task_id" in run_json
    task_id = run_json["task_id"]
    assert run_json["scenario_id"] == scenario_id
    assert run_json["status"] == "pending"
    
    # Step 3: Poll task status until finished
    max_attempts = 20
    poll_interval = 0.2  # 200ms
    task_finished = False
    
    for _ in range(max_attempts):
        task_response = client.get(f"/scenarios/tasks/{task_id}")
        assert task_response.status_code == 200
        
        task_json = task_response.json()
        assert task_json["task_id"] == task_id
        assert task_json["scenario_id"] == scenario_id
        
        if task_json["status"] == "finished":
            task_finished = True
            assert task_json["error"] is None
            assert task_json["started_at"] is not None
            assert task_json["finished_at"] is not None
            break
        elif task_json["status"] == "failed":
            pytest.fail(f"Task failed with error: {task_json['error']}")
        
        time.sleep(poll_interval)
    
    assert task_finished, "Task did not finish within the expected time"
    
    # Step 4: Verify scenario was updated with result
    scenario_response = client.get(f"/scenarios/{scenario_id}")
    
    assert scenario_response.status_code == 200
    
    final_scenario = scenario_response.json()
    assert final_scenario["id"] == scenario_id
    assert final_scenario["name"] == "async-test-scenario"
    assert final_scenario["status"] == "finished"
    assert final_scenario["config"] == {"param1": "test-value", "param2": 123}
    assert final_scenario["result"] is not None
    assert final_scenario["result"]["summary"] == "demo result"
    assert final_scenario["result"]["input_config"] == {"param1": "test-value", "param2": 123}
    assert final_scenario["started_at"] is not None
    assert final_scenario["finished_at"] is not None


def test_run_nonexistent_scenario():
    """Test that running a non-existent scenario returns 404."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    
    response = client.post(f"/scenarios/{non_existent_id}/run")
    
    assert response.status_code == 404
    assert "detail" in response.json()
    assert non_existent_id in response.json()["detail"]


def test_get_nonexistent_task():
    """Test that getting a non-existent task returns 404."""
    non_existent_task_id = "00000000-0000-0000-0000-000000000000"
    
    response = client.get(f"/scenarios/tasks/{non_existent_task_id}")
    
    assert response.status_code == 404
    assert "detail" in response.json()
    assert non_existent_task_id in response.json()["detail"]
