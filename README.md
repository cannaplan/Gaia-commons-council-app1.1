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

- Create and run a scenario (POST /scenarios)
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
    "status": "finished",
    "started_at": "2026-01-29T05:00:00Z",
    "finished_at": "2026-01-29T05:00:01Z",
    "result": {
      "summary": "demo result",
      "input_config": {"param1": "value1"}
    }
  }
  ```

- Get a scenario by ID (GET /scenarios/{id})
  ```bash
  curl http://127.0.0.1:8000/scenarios/550e8400-e29b-41d4-a716-446655440000
  ```
  Response (200 OK): Same as POST response

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

### Database
- The application now uses SQLite for scenario persistence (file-based by default)
- Database location: `./data/gaia.db` (created automatically on first run)
- For testing, a temporary file-based SQLite database is used automatically via the `DATABASE_URL` environment variable (configured in the test fixtures)
- To use a different database, set the `DATABASE_URL` environment variable:
  ```bash
  export DATABASE_URL="sqlite:///./custom-path.db"
  ```

### Migration Notes
- **IMPORTANT**: This version introduces SQLite persistence for scenarios. 
- On first run, the database schema will be created automatically in `./data/gaia.db`
- For production deployments, ensure the `./data` directory is writable and backed up regularly
- TODO: Implement proper database migrations using Alembic or similar tool for future schema changes
- The database is initialized on application startup; no manual migration is required for the initial deployment

### Production Considerations
- **Horizontal Scaling**: SQLite file-based databases are not suitable for concurrent writes from multiple application instances. For horizontal scaling with multiple FastAPI workers or instances:
  - Consider enabling WAL (Write-Ahead Logging) mode for better concurrent read performance
  - For true horizontal scaling, migrate to a client-server database (PostgreSQL, MySQL, etc.)
- **Backup Strategy**: 
  - Implement regular backups of the `./data/gaia.db` file
  - Use SQLite's `.backup` command or file system snapshots
  - Test restore procedures regularly
- **Performance**: For production workloads with high write concurrency, monitor for database lock contention and consider migrating to a client-server database

License
- This project uses the license text included in the LICENSE file (permission + restrictions + disclaimer).

Next Steps
1. ✅ Add database persistence for scenarios (completed in this PR)
2. Implement background task queue for async execution
3. Add more scenario types and configuration options
4. Expand API with scenario management endpoints
5. Add database migration support using Alembic