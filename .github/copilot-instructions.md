# GitHub Copilot Instructions for Gaia Commons Council

## Repository Overview

**Gaia Commons Council** is a Python-based planetary transformation framework that bridges climate modeling and real-world implementation. The repository provides:
- A **FastAPI-based REST API** for scenario management with OpenAPI/Swagger documentation
- A **CLI tool** for running scenarios and generating reports
- Scenario execution engine with configurable parameters

**Project Type**: Python web application with CLI  
**Size**: Small (~10 Python files)  
**Languages**: Python 3.11+  
**Key Frameworks**: FastAPI, Pydantic, Click, pytest  
**Status**: Early prototype, work in progress

## Tech Stack

- **Web Framework**: FastAPI 0.104.0+
- **ASGI Server**: uvicorn 0.24.0+
- **CLI Framework**: Click 8.1.0+
- **Data Validation**: Pydantic 2.0.0+
- **Configuration**: PyYAML 6.0.0+
- **Testing**: pytest 7.4.0+, httpx 0.25.0+, pytest-cov 4.1.0+
- **Python Version**: 3.11+ (CI uses 3.11, 3.12+ supported)

## Project Structure

```
app/
  __init__.py       # Package initialization
  main.py           # FastAPI application with health and scenario endpoints
  api.py            # API router with scenario CRUD endpoints
  schemas.py        # Pydantic models for request/response validation
  scenario.py       # Core scenario execution logic
  cli.py            # Click-based CLI entrypoint
tests/
  test_api.py       # API endpoint tests
  test_cli.py       # CLI tests
  test_health.py    # Health check tests
```

## Development Workflow

### Bootstrap (First Time Setup)

1. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

### Run the Application

**API Server** (development mode with auto-reload):
```bash
uvicorn app.main:app --reload --port 8000
```
- Health check: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs (OpenAPI/Swagger UI)

**CLI**:
```bash
python -m app.cli run-scenario --name "demo"
python -m app.cli run-scenario --name "test" --config config.json
python -m app.cli run-scenario --name "demo" --output result.json
```

### Testing

**Run all tests**:
```bash
pytest
```

**Run with verbose output**:
```bash
pytest -v
```

**Run with coverage report**:
```bash
pytest --cov=app
```

**Run specific test file**:
```bash
pytest tests/test_api.py
pytest tests/test_cli.py -v
```

**Test configuration**: Defined in `pytest.ini` with settings:
- Test discovery: `tests/` directory, `test_*.py` files
- Verbose output and strict marker enforcement enabled by default

### Linting & Code Quality

Currently, the project does not have configured linters (no flake8, black, mypy, or ruff config). When adding code:
- Follow **PEP 8** style guidelines
- Use **type hints** for function signatures
- Include **docstrings** for public functions and classes
- Keep imports organized (stdlib, third-party, local)

### CI/CD

GitHub Actions CI runs on:
- All pushes to `main` and `feature/**` branches
- All pull requests to `main`

CI workflow (`.github/workflows/ci.yml`):
1. Sets up Python 3.11
2. Installs dependencies from `requirements.txt` and `requirements-dev.txt`
3. Runs `pytest -q` (quiet mode)

## Coding Conventions

### API Design
- **Synchronous endpoints**: Use `def` (not `async def`) for endpoints that call blocking code (e.g., `time.sleep`)
  - FastAPI automatically runs synchronous endpoints in a threadpool
- **Status codes**: Use appropriate HTTP status codes (201 for creation, 404 for not found, etc.)
- **Response models**: Always specify Pydantic response models for OpenAPI schema generation
- **Location headers**: Include `Location` header in 201 responses for created resources

### Schema Design
- Use `Field(default_factory=dict)` for dict fields that should never be `None`
- Validate required fields with `min_length` constraints
- Return timezone-aware ISO 8601 timestamps (`datetime.now(timezone.utc).isoformat()`)

### Testing Practices
- **Avoid implementation coupling**: Don't import/manipulate private variables (e.g., `_SCENARIO_STORE`)
- **Field-by-field assertions**: Don't compare entire payloads; assert stable fields individually
- **Timestamp validation**: Parse timestamps with `datetime.fromisoformat()` and verify timezone-awareness
- **Test isolation**: Each test should be independent and not rely on execution order

### Thread Safety
- In-memory data structures accessed from multiple threads must use `threading.Lock`
- Document thread-safety considerations in comments

## Common Patterns

### API Endpoint Pattern
```python
@router.post("/scenarios", status_code=201, response_model=ScenarioResponse)
def create_scenario(scenario: ScenarioCreate, response: Response):
    """Create and execute a scenario. Synchronous to avoid blocking event loop."""
    result = create_and_run_scenario(scenario.name, scenario.config)
    response.headers["Location"] = f"/scenarios/{result['id']}"
    return result
```

### Test Pattern
```python
def test_endpoint():
    """Test description."""
    response = client.post("/scenarios", json={"name": "test"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test"
    assert data["status"] == "finished"
    # Validate timestamps
    started = datetime.fromisoformat(data["started_at"])
    assert started.tzinfo is not None
```

## Important Notes

- **Database**: Currently uses in-memory storage (grows unbounded). Database persistence planned for future PR.
- **Async execution**: Scenarios run synchronously with `time.sleep()`. Background task queue planned for future.
- **API versioning**: Not currently implemented; all endpoints are unversioned.

## Getting Help

- Check `README.md` for quickstart guide and usage examples
- Review existing tests in `tests/` for code examples
- API documentation available at `/docs` when server is running
- GitHub Actions CI logs show test failures and error messages
