"""
Database session and engine configuration.

This module provides:
- SQLAlchemy engine creation from settings
- SessionLocal factory for DB sessions
- `get_db` dependency for FastAPI routes
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# SQLAlchemy Engine
# -----------------
# echo=False: disable verbose SQL logging
# pool_pre_ping=True: keeps idle connections healthy
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,   # Check beforehand if the connection is working, if it is broken, open a new one
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

def get_db() -> Generator:
    """
    FastAPI dependency that provides a SQLAlchemy session.

    Yields:
        Session: an active database session.

    Ensures:
        Session is always closed after request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()