"""Tests for the API endpoints."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_post_and_get_scenario():
    """Test creating a scenario via POST and retrieving it via GET."""
    # Create a scenario
    scenario_data = {
        "name": "test-scenario",
        "config": {"param1": "value1", "param2": 42}
    }
    
    # POST the scenario
    post_response = client.post("/scenarios", json=scenario_data)
    
    # Assert 201 Created status
    assert post_response.status_code == 201
    
    # Assert response contains expected fields
    response_json = post_response.json()
    assert "id" in response_json
    assert response_json["name"] == "test-scenario"
    assert response_json["status"] == "finished"
    assert "result" in response_json
    assert response_json["result"]["summary"] == "demo result"
    assert response_json["result"]["input_config"] == {"param1": "value1", "param2": 42}
    assert "started_at" in response_json
    assert "finished_at" in response_json
    
    # Assert Location header is set
    assert "Location" in post_response.headers
    scenario_id = response_json["id"]
    assert post_response.headers["Location"] == f"/scenarios/{scenario_id}"
    
    # GET the scenario by ID
    get_response = client.get(f"/scenarios/{scenario_id}")
    
    # Assert 200 OK status
    assert get_response.status_code == 200
    
    # Assert GET response matches POST response
    get_json = get_response.json()
    assert get_json == response_json
    assert get_json["id"] == scenario_id
    assert get_json["name"] == "test-scenario"


def test_get_not_found():
    """Test that GET returns 404 for a non-existent scenario."""
    # Try to get a non-existent scenario
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    
    response = client.get(f"/scenarios/{non_existent_id}")
    
    # Assert 404 Not Found status
    assert response.status_code == 404
    
    # Assert error message is present
    response_json = response.json()
    assert "detail" in response_json
    assert non_existent_id in response_json["detail"]


def test_post_scenario_without_config():
    """Test creating a scenario without optional config."""
    # Create a scenario with only name (no config)
    scenario_data = {
        "name": "simple-scenario"
    }
    
    # POST the scenario
    response = client.post("/scenarios", json=scenario_data)
    
    # Assert 201 Created status
    assert response.status_code == 201
    
    # Assert response contains expected fields
    response_json = response.json()
    assert response_json["name"] == "simple-scenario"
    assert response_json["result"]["input_config"] == {}


def test_scenario_execution_failure():
    """Test that scenario failures are properly recorded with status 'failed'."""
    # Mock _execute_scenario to raise an exception
    with patch('app.scenario._execute_scenario') as mock_execute:
        mock_execute.side_effect = ValueError("Test error")
        
        scenario_data = {
            "name": "failing-scenario",
            "config": {"test": "value"}
        }
        
        # POST the scenario - should succeed even though execution fails
        response = client.post("/scenarios", json=scenario_data)
        
        # Assert 201 Created status (scenario created even though it failed)
        assert response.status_code == 201
        
        # Assert response indicates failure
        response_json = response.json()
        assert response_json["name"] == "failing-scenario"
        assert response_json["status"] == "failed"
        assert "Scenario failed" in response_json["result"]["summary"]
        assert "Test error" in response_json["result"]["summary"]
        assert response_json["result"]["input_config"] == {"test": "value"}
        
        # Verify the scenario was saved to database with failed status
        scenario_id = response_json["id"]
        get_response = client.get(f"/scenarios/{scenario_id}")
        assert get_response.status_code == 200
        get_json = get_response.json()
        assert get_json["status"] == "failed"
        assert "Scenario failed" in get_json["result"]["summary"]

