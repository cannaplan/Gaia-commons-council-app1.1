"""Database configuration and session management."""

import os
from sqlmodel import SQLModel, create_engine, Session

# Read DATABASE_URL from environment, default to SQLite file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/gaia.db")

# Ensure directory exists for file-based SQLite databases
if DATABASE_URL.startswith("sqlite") and DATABASE_URL != "sqlite:///:memory:":
    # Extract filesystem path from URL (e.g., "./data/gaia.db" from "sqlite:///./data/gaia.db")
    db_path = DATABASE_URL.split(":///", 1)[-1]
    if db_path and not db_path.startswith(":"):
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
# Create engine with check_same_thread=False for SQLite
# This allows SQLite to be used with FastAPI's async endpoints
# For in-memory databases, we use connect_args to ensure the connection stays alive
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# For in-memory SQLite, use poolclass StaticPool to keep single connection alive
if DATABASE_URL == "sqlite:///:memory:":
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        poolclass=StaticPool,
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)


def init_db():
    """
    Initialize the database by creating all tables.
    
    This should be called on application startup or in tests
    to ensure all SQLModel tables are created.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Generator that yields a database session.
    
    Use this with FastAPI's Depends or in a context manager
    to get a database session that will be automatically closed.
    
    Yields:
        Session: An active database session
    """
    with Session(engine) as session:
        yield session
