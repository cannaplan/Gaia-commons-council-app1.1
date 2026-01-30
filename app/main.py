"""FastAPI application with health endpoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as api_router
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown events."""
    # Startup: Initialize database tables
    init_db()
    yield
    # Shutdown: cleanup if needed (none for now)


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
