# Gaia Commons Council

Gaia Commons Council is the world's first complete planetary transformation framework that bridges the critical gap between climate modeling and real-world implementation. Created by Minnesota Cannabi... (project description truncated for brevity in this header)

Status: Work in progress — early prototype. Contributions and feedback welcome.

This repository contains a Python-based CLI and a small API placeholder to run scenarios, compare results, visualize outputs, and generate reports.

Quickstart (beginner-friendly)
1. Clone the repo
   git clone https://github.com/cannaplan/Gaia-commons-council-app1.1.git
   cd Gaia-commons-council-app1.1

2. Create a Python virtual environment and activate it
   python3 -m venv .venv
   # macOS / Linux
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1

3. Install dependencies
   pip install -r requirements.txt
   # For development (includes test dependencies)
   pip install -r requirements-dev.txt

4. Run the API (development)
   # starts a small local API on port 8000
   uvicorn app.main:app --reload --port 8000

   Visit: http://127.0.0.1:8000/health

5. Run the CLI
   # Basic usage - run a scenario
   python -m app.cli run-scenario --name "demo"
   
   # With configuration file (JSON or YAML)
   python -m app.cli run-scenario --name "my-scenario" --config config.json
   
   # Save output to file
   python -m app.cli run-scenario --name "demo" --output result.json

6. Run tests
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=app

What’s included
- app/main.py — minimal FastAPI app with a health endpoint.
- app/cli.py — CLI entrypoint (click) with a run-scenario stub.
- requirements.txt — minimal package list to run the app and CLI.
- .env.example — example environment variables.
- Dockerfile — simple image to run the app.
- LICENSE — the permission & disclaimer text you provided.
- .github/workflows/ci.yml — tiny CI that installs dependencies and verifies the app imports.

Usage Examples

API:
- Health check (curl)
  ```bash
  curl http://127.0.0.1:8000/health
  ```
  Response: `{"status": "ok"}`

- **Phase A: Async Scenario Execution with DB-backed BackgroundTasks**
  
  The API now supports asynchronous scenario execution using FastAPI BackgroundTasks
  with database persistence. This enables non-blocking scenario runs with status polling.

- Create a scenario (POST /scenarios)
  ```bash
  curl -X POST http://127.0.0.1:8000/scenarios \
    -H "Content-Type: application/json" \
    -d '{"name": "my-scenario", "config": {"param1": "value1"}}'
  ```
  Response (201 Created):
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "my-scenario",
    "status": "pending",
    "config": {"param1": "value1"},
    "started_at": "2026-01-29T05:00:00Z",
    "finished_at": null,
    "result": null
  }
  ```

- Run a scenario asynchronously (POST /scenarios/{id}/run)
  ```bash
  curl -X POST http://127.0.0.1:8000/scenarios/550e8400-e29b-41d4-a716-446655440000/run
  ```
  Response (202 Accepted):
  ```json
  {
    "task_id": "abc123-task-id",
    "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending"
  }
  ```

- Check task status (GET /scenarios/tasks/{task_id})
  ```bash
  curl http://127.0.0.1:8000/scenarios/tasks/abc123-task-id
  ```
  Response (200 OK):
  ```json
  {
    "task_id": "abc123-task-id",
    "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "finished",
    "error": null,
    "created_at": "2026-01-29T05:00:00Z",
    "started_at": "2026-01-29T05:00:01Z",
    "finished_at": "2026-01-29T05:00:02Z"
  }
  ```

- Get a scenario by ID (GET /scenarios/{id})
  ```bash
  curl http://127.0.0.1:8000/scenarios/550e8400-e29b-41d4-a716-446655440000
  ```
  Response (200 OK):
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "my-scenario",
    "status": "finished",
    "config": {"param1": "value1"},
    "started_at": "2026-01-29T05:00:01Z",
    "finished_at": "2026-01-29T05:00:02Z",
    "result": {
      "summary": "demo result",
      "input_config": {"param1": "value1"}
    }
  }
  ```

- OpenAPI Documentation (Swagger UI)
  Visit http://127.0.0.1:8000/docs in your browser to explore the interactive API documentation

CLI:
- Run a scenario
  ```bash
  python -m app.cli run-scenario --name "demo"
  ```
  Output (JSON):
  ```json
  {
    "id": "uuid-here",
    "name": "demo",
    "status": "finished",
    "result": {
      "summary": "demo result",
      "input_config": {}
    },
    "started_at": "2026-01-29T00:00:00",
    "finished_at": "2026-01-29T00:00:01"
  }
  ```

Tests:
- Run tests
  ```bash
  pytest
  ```

Development
- Tests are located in `tests/` directory
- CI automatically runs tests on push and pull requests
- Use `pytest -v` for verbose test output
- Use `pytest --cov=app` to see code coverage

Database & Persistence
- **Default**: The application uses a file-based SQLite database at `./data/gaia.db` for persisting scenario and task records
- **File location**: The database file is created automatically in the `data/` directory (which is git-ignored)
- **In tests**: Tests use a temporary file-based SQLite database (created and cleaned up automatically)
- **Custom database**: Set the `DATABASE_URL` environment variable to use a different database:
  ```bash
  export DATABASE_URL="sqlite:///path/to/your/database.db"
  # Or for PostgreSQL (requires psycopg2):
  # export DATABASE_URL="postgresql://user:password@localhost/dbname"
  ```
- **Database initialization**: The database tables are created automatically on application startup via the `init_db()` function in the lifespan context manager
- **Migrations**: Database migrations with Alembic are planned for a future release (TODO)
- **Models**: 
  - **Scenario**: Stores scenario records with id, name, status, config (JSON), result (JSON), started_at, and finished_at fields
  - **Task**: Tracks background task execution with task_id, scenario_id, status, error, created_at, started_at, and finished_at fields

Phase A: Async Execution with BackgroundTasks
- **Implementation**: This release implements Phase A of async scenario execution using FastAPI BackgroundTasks
- **Database-backed**: All task and scenario state is persisted to the database for durability and status polling
- **Workflow**: 
  1. Create a scenario with POST /scenarios (stores config, returns scenario_id)
  2. Enqueue execution with POST /scenarios/{id}/run (returns task_id)
  3. Poll task status with GET /scenarios/tasks/{task_id}
  4. Retrieve final result with GET /scenarios/{id}
- **Future**: In a future release (Phase B), BackgroundTasks will be replaced with Celery/Redis for production-scale async execution. The API endpoints will remain the same, only the task enqueueing mechanism will change.

License
- This project uses the license text included in the LICENSE file (permission + restrictions + disclaimer).

Next Steps
1. ~~Add database persistence for scenarios~~ ✅ Completed
2. ~~Implement background task queue for async execution~~ ✅ Phase A completed (BackgroundTasks with DB persistence)
3. Add more scenario types and configuration options
4. Expand API with scenario management endpoints
5. Phase B: Replace BackgroundTasks with Celery/Redis for production-scale async execution