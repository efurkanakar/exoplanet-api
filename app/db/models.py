"""
Database models.

This module defines the SQLAlchemy ORM models for the database.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Planet(Base):
    """
    Planet ORM model.

    Represents an exoplanet entry with discovery metadata and host star parameters.
    Includes soft-delete support and automatic timestamps.

    Columns:
        id          : Primary key
        name        : Unique planet name
        disc_method : Discovery method (indexed)
        disc_year   : Discovery year (indexed)
        orbperd     : Orbital period (days)
        rade        : Radius (Earth radii)
        masse       : Mass (Earth masses)
        st_teff     : Host star effective temperature (K)
        st_rad      : Host star radius (Solar radii)
        st_mass     : Host star mass (Solar masses)
        is_deleted  : Soft delete flag
        deleted_at  : Timestamp of deletion (UTC)
        created_at  : Creation timestamp (UTC)
        updated_at  : Last update timestamp (UTC)
    """

    __tablename__ = "planets"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Planet identity
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)

    # Discovery metadata
    disc_method: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    disc_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Orbital & physical parameters
    orbperd: Mapped[float] = mapped_column(Float, nullable=False)
    rade: Mapped[float] = mapped_column(Float, nullable=False)
    masse: Mapped[float] = mapped_column(Float, nullable=False)
    st_teff: Mapped[float] = mapped_column(Float, nullable=False)
    st_rad: Mapped[float] = mapped_column(Float, nullable=False)
    st_mass: Mapped[float] = mapped_column(Float, nullable=False)

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("idx_planet_disc_year_method", "disc_year", "disc_method"),
    )
