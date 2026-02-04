"""Test configuration for pytest."""

import os
import tempfile
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initialize the test database once for all tests."""
    # Create a temporary database file for tests using a safer method
    # NamedTemporaryFile creates a secure temp file and returns a file handle
    _test_db_fd = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    test_db_file = _test_db_fd.name
    _test_db_fd.close()  # Close the file handle but keep the file

    # Set the DATABASE_URL environment variable for the test session
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db_file}"

    # Import here so that app.db sees the correct DATABASE_URL
    from app.db import init_db

    # Initialize DB schema
    init_db()
    try:
        yield
    finally:
        # Cleanup: remove test database file
        if os.path.exists(test_db_file):
            os.remove(test_db_file)
        # Optionally, clean up environment variable
        os.environ.pop("DATABASE_URL", None)

from app import scenario
@pytest.fixture(autouse=True)
def clear_scenarios():
    """Clear scenarios before and after each test."""
    scenario.clear_scenario_store()
    yield
    scenario.clear_scenario_store()
