"""
Planet schemas.

This module defines Pydantic models for Planet-related requests and responses.
It includes creation/update payloads, output models, and lightweight utility
schemas for counts and soft-deleted listings.
"""

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator, ConfigDict


# ---------------------------
# Shared base (readable shape)
# ---------------------------

class PlanetBase(BaseModel):
    """Common planet fields shared by multiple schemas."""

    name: str = Field(..., min_length=1, max_length=200, description="Unique planet name")
    disc_method: str = Field(..., description="Discovery method")
    disc_year: int = Field(..., ge=1900, le=2100, description="Discovery year (1900..2100)")
    orbperd: float = Field(..., gt=0, description="Orbital period (days)")
    rade: float = Field(..., gt=0, description="Planet radius (Earth radii)")
    masse: float = Field(..., gt=0, description="Planet mass (Earth masses)")
    st_teff: float = Field(..., gt=0, description="Host star effective temperature (K)")
    st_rad: float = Field(..., gt=0, description="Host star radius (Solar radii)")
    st_mass: float = Field(..., gt=0, description="Host star mass (Solar masses)")


# ---------------------------
# Create
# ---------------------------

class PlanetCreate(PlanetBase):
    """
    Payload schema for creating a new planet.

    - Trims `name` and `disc_method`
    - Normalizes `disc_method` to Title Case
    - Forbids extra/unexpected fields
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "Kepler-22b",
                "disc_method": "Transit",
                "disc_year": 2011,
                "orbperd": 290.0,
                "rade": 2.4,
                "masse": 5.0,
                "st_teff": 5500.0,
                "st_rad": 0.9,
                "st_mass": 0.8,
            }
        },
    )

    @field_validator("name")
    @classmethod
    def _normalize_name(cls, v: str) -> str:
        """Trim whitespace for name."""
        return v.strip()

    @field_validator("disc_method")
    @classmethod
    def _normalize_method(cls, v: str) -> str:
        """Normalize discovery method to Title Case (trimmed)."""
        v = v.strip()
        # Title case: "radial velocity" -> "Radial Velocity"
        return " ".join(w.capitalize() for w in v.split())


# ---------------------------
# Read (output)
# ---------------------------

class PlanetOut(PlanetBase):
    """
    Response schema for a planet record.

    - Includes primary key `id`
    - Configured for ORM objects via `from_attributes=True`
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanetChangeEntry(BaseModel):
    """Represents a single field change in a planet mutation."""

    field: str = Field(..., description="Name of the field that changed")
    before: Any | None = Field(None, description="Previous value before the change")
    after: Any | None = Field(None, description="New value after the change")


class PlanetWithChanges(PlanetOut):
    """Planet response extended with change metadata."""

    changes: list[PlanetChangeEntry] = Field(
        default_factory=list,
        description="List of individual field changes applied in the request",
    )

    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# PATCH
# ---------------------------

class PlanetUpdate(BaseModel):
    """
    Payload schema for partial updates.

    - All fields are optional
    - Only provided fields will be updated
    - Trims/normalizes `name` and `disc_method` when present
    - Forbids extra/unexpected fields
    """

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    disc_method: Optional[str] = None
    disc_year: Optional[int] = Field(None, ge=1900, le=2100)
    orbperd: Optional[float] = Field(None, gt=0)
    rade: Optional[float] = Field(None, gt=0)
    masse: Optional[float] = Field(None, gt=0)
    st_teff: Optional[float] = Field(None, gt=0)
    st_rad: Optional[float] = Field(None, gt=0)
    st_mass: Optional[float] = Field(None, gt=0)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "Kepler-22b",
                "disc_year": 2012,
                "rade": 2.5
            }
        },
    )

    @field_validator("name")
    @classmethod
    def _normalize_name_optional(cls, v: Optional[str]) -> Optional[str]:
        """Trim whitespace for optional name."""
        return v.strip() if isinstance(v, str) else v

    @field_validator("disc_method")
    @classmethod
    def _normalize_method_optional(cls, v: Optional[str]) -> Optional[str]:
        """Normalize optional discovery method to Title Case (trimmed)."""
        if isinstance(v, str):
            v = v.strip()
            return " ".join(w.capitalize() for w in v.split())
        return v

# ---------------------------
# Lightweight utility schemas
# ---------------------------

class PlanetCount(BaseModel):
    """Response schema for count endpoints."""
    count: int = Field(..., ge=0, description="Total number of planets")


class MethodCount(BaseModel):
    """Response schema for method aggregation."""
    disc_method: str = Field(..., description="Discovery method name")
    count: int = Field(..., ge=0, description="Number of planets for this method")


class DeletedPlanetOut(BaseModel):
    """Response schema for soft-deleted listings."""
    id: int
    name: str
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp (UTC) or null")


class MetricSummary(BaseModel):
    """Minimum, maximum, average and median summary for a numeric metric."""

    min: Optional[float] = Field(None, description="Minimum value or null when unavailable")
    max: Optional[float] = Field(None, description="Maximum value or null when unavailable")
    avg: Optional[float] = Field(None, description="Average value or null when unavailable")
    median: Optional[float] = Field(None, description="Median value or null when unavailable")


class PlanetStats(BaseModel):
    """Aggregated statistics for planet metrics."""

    count: int = Field(..., ge=0, description="Number of matching planets")
    orbperd: MetricSummary
    rade: MetricSummary
    masse: MetricSummary
    st_teff: MetricSummary
    st_rad: MetricSummary
    st_mass: MetricSummary


class PlanetMethodStats(PlanetStats):
    """Statistics scoped to a specific discovery method."""

    disc_method: str = Field(..., description="Discovery method these statistics describe")


class PlanetTimelinePoint(BaseModel):
    """Discovery count for a given year."""

    disc_year: int = Field(..., ge=0, description="Discovery year")
    count: int = Field(..., ge=0, description="Number of planets discovered in that year")


class PlanetListResponse(BaseModel):
    """Paged planet response with pagination metadata."""

    items: list[PlanetOut]
    limit: int = Field(..., ge=1, description="Requested page size")
    offset: int = Field(..., ge=0, description="Requested offset")
    total: int = Field(..., ge=0, description="Total number of records that match the filters")
