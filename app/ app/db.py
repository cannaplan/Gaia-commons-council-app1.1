from typing import Iterator
import os

from sqlmodel import SQLModel, create_engine, Session

# Read DATABASE_URL at import time; tests will set this env var before importing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/gaia.db")

# SQLite needs check_same_thread=False for file-based DB when using multiple threads
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    """Create DB tables. Call this at app startup or in tests after configuring DATABASE_URL."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """Yield a session for use in non-FastAPI contexts. For FastAPI dependency use the same pattern."""
    with Session(engine) as session:
        yield session
