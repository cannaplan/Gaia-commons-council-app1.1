"""Database helper module for SQLite persistence using SQLModel."""

import os
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine


# Read DATABASE_URL at import time; tests will set this env var before importing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/gaia.db")

# Create data directory if using default SQLite path
if DATABASE_URL.startswith("sqlite:///./data/"):
    os.makedirs("./data", exist_ok=True)

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
    Yield a database session.
    
    This generator can be used as a context manager or in FastAPI dependency injection.
    
    Example usage in FastAPI:
        from fastapi import Depends
        from app.db import get_session
        
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            items = session.exec(select(Item)).all()
            return items
    
    Example usage as context manager:
        from app.db import get_session
        
        for session in get_session():
            # Use session here
            items = session.exec(select(Item)).all()
            break
    """
    with Session(engine) as session:
        yield session
