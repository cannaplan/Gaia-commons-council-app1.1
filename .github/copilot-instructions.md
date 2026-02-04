# GitHub Copilot Coding Agent Instructions

## Project Overview

Gaia Commons Council is a planetary transformation framework bridging climate modeling and real-world implementation. This repository contains a Python-based CLI and API for running scenarios, comparing results, visualizing outputs, and generating reports.

**Status**: Work in progress — early prototype

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **API Framework**: FastAPI (with Uvicorn server)
- **CLI**: Click framework
- **Database**: SQLite with SQLModel (SQLAlchemy ORM)
- **Schema Validation**: Pydantic v2.0+
- **Testing**: pytest with pytest-cov
- **Configuration**: YAML/JSON support via PyYAML

## Repository Structure

- `app/` — Main application code
  - `main.py` — FastAPI application entry point
  - `api.py` — API route definitions
  - `cli.py` — Click-based CLI implementation
  - `scenario.py` — Scenario execution logic
  - `schemas.py` — Pydantic models for validation
  - `db.py` — Database configuration and session management
- `tests/` — Test suite using pytest
- `data/` — SQLite database files (git-ignored)
- `.github/workflows/` — CI/CD workflows

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development/testing
```

### Running the Application
```bash
# Start API server (development with auto-reload)
uvicorn app.main:app --reload --port 8000

# Run CLI
python -m app.cli run-scenario --name "demo"
python -m app.cli run-scenario --name "my-scenario" --config config.json
```

### Testing
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run with coverage report
pytest --cov=app

# Run specific test file
pytest tests/test_api.py
```

### Verification
```bash
# Quick verification (same as CI)
pytest -q
```

## Code Standards and Conventions

### Python Style
- Follow **PEP 8** conventions for Python code
- Use **type hints** for function parameters and return types
- Write **docstrings** for all modules, classes, and public functions using triple quotes (`"""`)
- Use **f-strings** for string formatting (preferred over `.format()` or `%`)

### API Development
- All API endpoints should use **Pydantic models** for request/response validation
- Define models in `schemas.py` with proper Field descriptions
- Use **async functions** for API route handlers
- Include descriptive docstrings for all endpoints
- Follow REST conventions for endpoint naming

### CLI Development
- Use **Click decorators** for command definitions
- Provide helpful `--help` text for all commands and options
- Support both JSON and YAML configuration files
- Print results in JSON format by default for easier parsing

### Testing
- Place tests in the `tests/` directory
- Follow pytest naming conventions:
  - Test files: `test_*.py`
  - Test functions: `test_*`
  - Test classes: `Test*`
- Use **pytest fixtures** for common setup/teardown
- Use **httpx** for API endpoint testing
- Aim for good test coverage on new features

### Dependencies
- Keep `requirements.txt` minimal (runtime only)
- Add test/development dependencies to `requirements-dev.txt`
- Pin major versions but allow minor/patch updates (e.g., `fastapi>=0.104.0`)

## Important Conventions

### Imports
- Group imports in order: standard library, third-party, local modules
- Use absolute imports from the `app` package (e.g., `from app.schemas import ScenarioCreate`)

### Error Handling
- Use FastAPI's built-in exception handlers
- Return appropriate HTTP status codes
- Provide descriptive error messages

### Configuration
- Support both JSON and YAML configuration files
- Use environment variables for sensitive data (not committed to repo)

### Database & Persistence
- Use **SQLModel** for ORM models (combines SQLAlchemy and Pydantic)
- Default database: SQLite at `./data/gaia.db` (file-based, auto-created)
- Database URL configurable via `DATABASE_URL` environment variable
- The `data/` directory is git-ignored — never commit database files
- Call `init_db()` at application startup to create tables
- Use `Session` context managers for database operations
- For tests: Use temporary database (configured in `conftest.py`)

### Security
- **Never commit secrets, API keys, or passwords** to the repository
- Use environment variables for all sensitive configuration
- Validate all user input using Pydantic models
- Use proper HTTP status codes and error messages (avoid leaking sensitive info)
- Keep dependencies up-to-date to avoid known vulnerabilities

## CI/CD

The repository uses GitHub Actions for continuous integration:
- Runs on Python 3.11
- Installs dependencies from both `requirements.txt` and `requirements-dev.txt`
- Executes `pytest -q` for all tests
- Triggers on pushes to `main` and `feature/**` branches, and on pull requests to `main`

## Notes for Code Changes

- This is an **early prototype** — prioritize clarity and maintainability
- **Do not** modify the LICENSE file
- **Test changes** locally before committing
- Keep changes **minimal and focused**
- Update README.md if adding new features or changing usage patterns
- Ensure backward compatibility when possible
- New API endpoints should follow the existing pattern in `api.py`
- CLI commands should maintain consistent output formatting

## Future Roadmap (Context)

Planned features include:
1. Database persistence for scenarios (SQLite/PostgreSQL)
2. Background task queue for async execution
3. Additional scenario types and configuration options
4. Enhanced scenario management endpoints

When implementing these features, maintain the existing architectural patterns.
