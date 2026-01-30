"""Database helper module for SQLite persistence using SQLModel."""

import os
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine


# Read DATABASE_URL at import time; tests will set this env var before importing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/gaia.db")

# SQLite needs check_same_thread=False for file-based DB when using multiple threads
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    """
    Create database tables.
    
    Call this at app startup or in tests after configuring DATABASE_URL.
    Creates all tables defined by SQLModel.metadata.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """
    Yield a database session for use in non-FastAPI contexts.
    
    For FastAPI dependency injection, use the same pattern with Depends().
    
    Example:
        with next(get_session()) as session:
            # Use session here
            pass
    
    Or as a generator:
        for session in get_session():
            # Use session here
            break
    """
    with Session(engine) as session:
        yield session
