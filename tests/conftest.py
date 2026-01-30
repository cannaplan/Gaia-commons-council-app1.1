"""Test configuration and fixtures."""

import os
import pytest
import tempfile


# Create a unique temporary database file for this test session
# This ensures parallel test runs don't interfere with each other
@pytest.fixture(scope="session")
def test_db_path():
    """Create a unique temporary database path for this test session."""
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_gaia_")
    os.close(fd)  # Close the file descriptor, we just need the path
    return path


# Configure test database before any imports
@pytest.fixture(scope="session", autouse=True)
def configure_test_database(test_db_path):
    """Set DATABASE_URL before any app modules are imported."""
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"
    yield
    # Cleanup: Remove the test database file after all tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture(autouse=True, scope="function")
def clean_database():
    """
    Clean the database between tests.
    
    This fixture ensures each test starts with a clean database state.
    """
    # Import after setting environment variable
    # Import Scenario model to ensure it's registered with SQLModel metadata
    from app.scenario import Scenario  # noqa: F401
    from app.db import engine
    from sqlmodel import SQLModel
    
    # Drop and recreate all tables before each test
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    yield
    
    # Clean up after test - tables will be dropped before next test

