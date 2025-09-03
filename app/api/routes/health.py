"""
System and health API routes.

Provides lightweight endpoints for liveness and readiness checks.
- /system/root       : friendly root info
- /system/health     : liveness probe
- /system/readiness  : readiness probe (checks dependencies like DB)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.system import RootOut, HealthOut, ReadinessOut

router = APIRouter(prefix="/system", tags=["system"])



@router.get(
    "/root",
    response_model=RootOut,
    summary="Service root",
    description="Returns a friendly root message to confirm the API is up."
)
def root() -> RootOut:
    """
    Return a friendly root payload.

    Returns:
        RootOut: Service liveness info with UTC timestamp.
    """
    return RootOut()


@router.get(
    "/health",
    response_model=HealthOut,
    status_code=status.HTTP_200_OK,
    summary="Liveness health check",
    description="Cheap liveness probe to confirm the process is alive."
)
def health() -> HealthOut:
    """
    Lightweight liveness probe.

    Confirms the application process is up and serving requests.
    Returns status='ok' and a UTC timestamp.

    Returns:
        HealthOut: Basic health information.
    """
    return HealthOut(status="ok")


@router.get(
    "/readiness",
    response_model=ReadinessOut,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Verifies external dependencies (e.g., database) are reachable."
)


def readiness(db: Session = Depends(get_db)) -> ReadinessOut:
    """
    Readiness probe that verifies external dependencies.

    Currently checks database connectivity by executing a trivial SQL statement.
    If the database is unreachable, readiness will be 'not_ready'.

    Args:
        db (Session): SQLAlchemy session dependency.

    Returns:
        ReadinessOut: Overall readiness with per-dependency status.
    """
    try:
        db.execute(text("SELECT 1"))
        return ReadinessOut(status="ready", db="ok")

    except Exception as exc:
        return ReadinessOut(status="not_ready", db="fail", detail=str(exc))