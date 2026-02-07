"""FastAPI application with health endpoint."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as api_router
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Skip DB init when running under tests; test fixtures call init_db() themselves
    running_tests = os.getenv("PYTEST_CURRENT_TEST") is not None
    if not running_tests:
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
