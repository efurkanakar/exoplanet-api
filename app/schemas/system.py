"""
Schemas for system and health-related endpoints.

These Pydantic models define the structured responses returned by
the system routes (root, health, readiness).
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class RootOut(BaseModel):
    ok: bool = Field(True, description="Service liveness indicator")
    message: str = Field(
        "API is running. You can test it at /docs.",
        description="Human-friendly message"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Server-side UTC timestamp"
    )


class HealthOut(BaseModel):
    status: str = Field(..., description="Health status (always 'ok' for liveness)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Server-side UTC timestamp"
    )


class ReadinessOut(BaseModel):
    status: str = Field(..., description="Overall readiness (ready | not_ready)")
    db: str = Field(..., description="Database connectivity (ok | fail)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Server-side UTC timestamp"
    )
    detail: Optional[str] = Field(
        None,
        description="Optional detail if readiness check fails"
    )