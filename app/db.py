"""Database initialization and models for SQLite persistence.

This module provides SQLite-backed storage for scenarios using SQLModel.
By default, it uses a file-based database at ./data/gaia.db.
For testing, set DATABASE_URL='sqlite:///:memory:' to use an in-memory database.
"""

import os
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Session, create_engine


class ScenarioModel(SQLModel, table=True):
    """SQLModel representing a scenario in the database.
    
    Maps to the 'scenarios' table with fields matching ScenarioResponse schema.
    """
    __tablename__ = "scenarios"
    
    id: str = Field(primary_key=True, description="UUID primary key")
    name: str = Field(description="Name of the scenario")
    status: str = Field(description="Status of the scenario (e.g., 'running', 'finished', 'failed')")
    started_at: datetime = Field(description="Timestamp when the scenario started")
    finished_at: Optional[datetime] = Field(default=None, description="Timestamp when the scenario finished")
    result: Optional[str] = Field(default=None, description="JSON string of the result payload")
    config: Optional[str] = Field(default=None, description="JSON string of the input configuration")


# Global engine instance (created lazily) and lock for thread-safety
_engine = None
_engine_lock = threading.Lock()


def get_engine():
    """Get or create the SQLAlchemy engine.
    
    This function is called lazily to ensure DATABASE_URL is read at runtime,
    not at import time. This allows tests to set the environment variable
    before the engine is created.
    
    Thread-safe implementation using a lock to prevent multiple engine instances
    in multi-threaded environments (e.g., FastAPI with multiple workers).
    """
    global _engine
    if _engine is None:
        with _engine_lock:
            # Double-check pattern: check again inside the lock
            if _engine is None:
                # Get DATABASE_URL from environment variable or use default file-based SQLite
                database_url = os.getenv("DATABASE_URL", "sqlite:///./data/gaia.db")
                # Create the SQLAlchemy engine
                # connect_args={"check_same_thread": False} is needed for SQLite to work with FastAPI
                _engine = create_engine(database_url, connect_args={"check_same_thread": False}, echo=False)
    return _engine


def init_db():
    """Initialize the database by creating all tables.
    
    This should be called once at application startup or in tests.
    For file-based SQLite databases, it creates the parent directory if needed.
    """
    engine = get_engine()
    
    # Get the database URL from the engine to ensure consistency
    database_url = str(engine.url)
    
    # Create parent directory if using file-based SQLite (relative or absolute path)
    if database_url.startswith("sqlite:///"):
        path_part = database_url[len("sqlite:///") :]
        # Skip in-memory SQLite
        if path_part and not path_part.startswith(":memory:"):
            if path_part.startswith("/"):
                db_path = path_part
            else:
                db_path = os.path.join(os.getcwd(), path_part)
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
    
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
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
