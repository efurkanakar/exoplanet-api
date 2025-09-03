"""
Base class for SQLAlchemy ORM models.

All ORM models in the project should inherit from this Base.
Alembic will also use this Base to detect models for migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass