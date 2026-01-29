"""Test configuration for pytest."""

import os
import tempfile
import pytest

# Use a temp file-based SQLite for tests (more reliable than in-memory with multiple connections)
test_db_file = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_file}"

from app.db import init_db
from app import scenario


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initialize the test database once for all tests."""
    # Initialize DB schema
    init_db()
    yield
    # Cleanup: remove test database file
    import os as os_cleanup
    if os_cleanup.path.exists(test_db_file):
        os_cleanup.remove(test_db_file)


@pytest.fixture(autouse=True)
def clear_scenarios():
    """Clear scenarios before and after each test."""
    scenario.clear_scenario_store()
    yield
    scenario.clear_scenario_store()
