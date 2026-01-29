"""Tests for the API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.scenario import _SCENARIO_STORE

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_scenario_store():
    """Clear the in-memory scenario store before each test."""
    _SCENARIO_STORE.clear()
    yield
    _SCENARIO_STORE.clear()


def test_post_and_get_scenario():
    """Test creating a scenario via POST and retrieving it via GET."""
    # Create a scenario via POST
    scenario_data = {
        "name": "test-scenario",
        "config": {"param1": "value1", "param2": 42}
    }
    
    response = client.post("/scenarios", json=scenario_data)
    
    # Assert 201 Created
    assert response.status_code == 201
    
    # Check Location header
    assert "Location" in response.headers
    
    # Check response JSON contains expected fields
    data = response.json()
    assert "id" in data
    assert data["name"] == "test-scenario"
    assert data["status"] == "finished"
    assert "started_at" in data
    assert "finished_at" in data
    assert "result" in data
    assert data["result"]["summary"] == "demo result"
    assert data["result"]["input_config"] == scenario_data["config"]
    
    # Extract the scenario ID and verify Location header
    scenario_id = data["id"]
    assert response.headers["Location"] == f"/scenarios/{scenario_id}"
    
    # Retrieve the scenario via GET
    get_response = client.get(f"/scenarios/{scenario_id}")
    
    # Assert 200 OK
    assert get_response.status_code == 200
    
    # Check that GET response matches POST response
    get_data = get_response.json()
    assert get_data == data


def test_get_not_found():
    """Test that GET for a non-existent scenario returns 404."""
    # Use a UUID that doesn't exist
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    
    response = client.get(f"/scenarios/{non_existent_id}")
    
    # Assert 404 Not Found
    assert response.status_code == 404
    
    # Check error message
    data = response.json()
    assert "detail" in data
    assert non_existent_id in data["detail"]


def test_post_scenario_empty_name():
    """Test that POST with empty name returns 422 validation error."""
    scenario_data = {
        "name": "",
        "config": {"param1": "value1"}
    }
    
    response = client.post("/scenarios", json=scenario_data)
    
    # Assert 422 Unprocessable Entity
    assert response.status_code == 422
    
    # Check validation error details
    data = response.json()
    assert "detail" in data


def test_post_scenario_without_config():
    """Test creating a scenario without the optional config field."""
    # POST without config key
    scenario_data = {
        "name": "test-scenario-no-config"
    }
    
    response = client.post("/scenarios", json=scenario_data)
    
    # Assert 201 Created
    assert response.status_code == 201
    
    # Check response JSON contains expected fields
    data = response.json()
    assert "id" in data
    assert data["name"] == "test-scenario-no-config"
    assert data["status"] == "finished"
    assert "result" in data
    assert data["result"]["summary"] == "demo result"
    # Verify that input_config defaults to empty dict when config is omitted
    assert data["result"]["input_config"] == {}
