"""Test configuration for pytest."""

import os
import tempfile
import pytest

# Create a temporary database file for tests using a safer method
# NamedTemporaryFile creates a secure temp file and returns a file handle
_test_db_fd = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
test_db_file = _test_db_fd.name
_test_db_fd.close()  # Close the file handle but keep the file

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
