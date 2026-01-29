"""FastAPI application with health endpoint."""

from fastapi import FastAPI

from app.api import router as api_router

app = FastAPI(
    title="Gaia Commons Council API",
    description="Planetary transformation framework API",
    version="0.1.0"
)

# Include API router with scenario endpoints
app.include_router(api_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
