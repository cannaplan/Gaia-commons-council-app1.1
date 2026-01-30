"""Pytest configuration and fixtures for testing."""

import os

# IMPORTANT: Set DATABASE_URL before any app imports
# This ensures the in-memory database is used for all tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_database_for_session():
    """
    Initialize database once for the entire test session.
    
    This runs before any tests and creates the database tables.
    """
    from app.db import init_db
    init_db()
    yield


@pytest.fixture(autouse=True)
def clean_database():
    """
    Clean up database between tests to ensure test isolation.
    
    This fixture:
    1. Yields for the test to run
    2. Clears the scenario store after the test
    """
    yield
    
    # Clean up after the test
    from app.scenario import clear_scenario_store
    clear_scenario_store()
