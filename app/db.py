"""Database module for SQLite persistence using SQLModel."""

import os
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine


# Read DATABASE_URL from environment variable
# Default to file-based SQLite database in ./data/gaia.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/gaia.db")

# SQLite requires check_same_thread=False for file-based DB with multiple threads
# This is safe when using SQLAlchemy's connection pooling
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create the database engine
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This should be called at application startup or in tests after
    configuring the DATABASE_URL environment variable.
    
    Note: This imports models to ensure they are registered with SQLModel.
    """
    # Import models to ensure they are registered
    from app.scenario import Scenario  # noqa: F401
    from app.tasks import Task  # noqa: F401
    
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """
    Get a database session for use in non-FastAPI contexts.
    
    Yields a Session that can be used with context managers:
        with Session(engine) as session:
            # use session
    
    For FastAPI dependency injection, use the same pattern with Depends.
    
    Yields:
        Session: A SQLModel database session
    """
    with Session(engine) as session:
        yield session
