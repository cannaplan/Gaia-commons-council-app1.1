"""Test configuration and fixtures."""

import os
import pytest
import tempfile

# Use a temporary file-based SQLite database for tests
# (in-memory doesn't work well with multiple connections)
test_db_path = os.path.join(tempfile.gettempdir(), "test_gaia.db")
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"


@pytest.fixture(autouse=True, scope="function")
def clean_database():
    """
    Clean the database between tests.
    
    This fixture ensures each test starts with a clean database state.
    """
    # Import after setting environment variable
    from app.db import engine
    from sqlmodel import SQLModel
    
    # Drop and recreate all tables before each test
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    yield
    
    # Clean up after test - tables will be dropped before next test


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Clean up the test database file after all tests are done."""
    yield
    # Remove the test database file
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

