"""FastAPI application with health endpoint."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as api_router
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Skip DB init if using in-memory database (i.e., during tests)
    # Tests will call init_db() themselves
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url.startswith("sqlite:///:memory:"):
        init_db()
    yield
    # Shutdown: Could add cleanup here if needed


app = FastAPI(
    title="Gaia Commons Council API",
    description="Planetary transformation framework API",
    version="0.1.0",
    lifespan=lifespan
)

# Include API router with scenario endpoints
app.include_router(api_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
