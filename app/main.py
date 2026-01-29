"""FastAPI application with health endpoint."""

from fastapi import FastAPI

app = FastAPI(
    title="Gaia Commons Council API",
    description="Planetary transformation framework API",
    version="0.1.0"
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
