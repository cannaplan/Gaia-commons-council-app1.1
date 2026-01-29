"""Database initialization and models for SQLite persistence.

This module provides SQLite-backed storage for scenarios using SQLModel.
By default, it uses a file-based database at ./data/gaia.db.
For testing, set DATABASE_URL='sqlite:///:memory:' to use an in-memory database.
"""

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Session, create_engine, select


class ScenarioModel(SQLModel, table=True):
    """SQLModel representing a scenario in the database.
    
    Maps to the 'scenariomodel' table with fields matching ScenarioResponse schema.
    """
    __tablename__ = "scenarios"
    
    id: str = Field(primary_key=True, description="UUID primary key")
    name: str = Field(description="Name of the scenario")
    status: str = Field(description="Status of the scenario (e.g., 'running', 'completed', 'failed')")
    started_at: datetime = Field(description="Timestamp when the scenario started")
    finished_at: Optional[datetime] = Field(default=None, description="Timestamp when the scenario finished")
    result: Optional[str] = Field(default=None, description="JSON string of the result payload")
    config: Optional[str] = Field(default=None, description="JSON string of the input configuration")


# Get DATABASE_URL from environment variable or use default file-based SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/gaia.db")

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed for SQLite to work with FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)


def init_db():
    """Initialize the database by creating all tables.
    
    This should be called once at application startup or in tests.
    For file-based databases, it creates the ./data directory if needed.
    """
    # Create data directory if using file-based SQLite
    if DATABASE_URL.startswith("sqlite:///./"):
        os.makedirs("./data", exist_ok=True)
    
    # Create all tables
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    """Context manager that provides a database session.
    
    Usage:
        with get_session() as session:
            scenario = session.get(ScenarioModel, scenario_id)
            
    Yields:
        Session: A SQLModel Session instance
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
