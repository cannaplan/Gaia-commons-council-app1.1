"""Tests for the API endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
    
    # Extract the scenario ID
    scenario_id = data["id"]
    
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
