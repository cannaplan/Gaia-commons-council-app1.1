"""FastAPI application with health endpoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import router as api_router
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for app startup and shutdown events."""
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Any cleanup can go here


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
