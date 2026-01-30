"""Pytest configuration and fixtures."""

import os
import tempfile

# Create a temporary file for the test database
# This file will be cleaned up automatically when tests complete
test_db_file = tempfile.mktemp(suffix=".db", prefix="test_gaia_")

# Set DATABASE_URL to use a temporary file-based SQLite database
# This avoids the connection pooling issues with :memory: databases
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_file}"