"""Planet API routes with advanced filtering, analytics and admin utilities."""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Response, status, Request
from typing import Literal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from datetime import datetime, timezone

from app.db.session import get_db
from app.db.models import Planet
from app.schemas.planet import (
    PlanetCreate,
    PlanetOut,
    PlanetUpdate,
    PlanetCount,
    MethodCount,
    DeletedPlanetOut,
    PlanetStats,
    PlanetMethodStats,
    PlanetTimelinePoint,
    PlanetListResponse,
)
from app.core.security import api_key_auth

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/planets", tags=["planets"])

@router.post(
    "/",
    response_model=PlanetOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new planet",
    description="Creates a planet and returns 201 with Location header."
)
def create_planet(
        payload: PlanetCreate,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
):
    """
    Create a new planet record.

    This endpoint validates input against `PlanetCreate` schema and inserts
    a new planet into the database. The planet name must be unique.
    On success, it returns HTTP 201 and sets the `Location`
    header to the absolute resource URL.

    Args:
        payload (PlanetCreate): The incoming planet data to insert.
        request (Request): Used to generate the absolute resource URL.
        response (Response): Used to add the Location header.
        db (Session): The SQLAlchemy database session.

    Returns:
        PlanetOut: The newly created planet.

    Raises:
        HTTPException 409: If a planet with the same name already exists.
        HTTPException 500: For unexpected database errors.
    """

    exists = db.execute(select(Planet.id).where(func.lower(Planet.name) == payload.name.lower())).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail=f"Planet '{payload.name}' already exists.")


    planet = Planet(**payload.model_dump())
    db.add(planet)

    try:
        db.flush()

        location_url = request.url_for("get_planet", planet_id=planet.id)

        response.headers["Location"] = str(location_url)

        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Planet '{payload.name}' already exists.")

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating planet.")

    db.refresh(planet)

    return planet

@router.get(
    "/",
    response_model=PlanetListResponse,
    summary="List planets",
    description="Lists planets with comprehensive filtering, sorting and pagination metadata."
)
def list_planets(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    name: str | None = Query(
        None,
        description="Case-insensitive substring search on planet name",
    ),
    disc_method: str | None = Query(
        None,
        description="Exact discovery method filter (case-insensitive)",
    ),
    min_year: int | None = Query(None, ge=0, description="Minimum discovery year (inclusive)"),
    max_year: int | None = Query(None, ge=0, description="Maximum discovery year (inclusive)"),
    min_orbperd: float | None = Query(None, gt=0, description="Minimum orbital period (days)"),
    max_orbperd: float | None = Query(None, gt=0, description="Maximum orbital period (days)"),
    min_rade: float | None = Query(None, gt=0, description="Minimum planet radius (Earth radii)"),
    max_rade: float | None = Query(None, gt=0, description="Maximum planet radius (Earth radii)"),
    min_masse: float | None = Query(None, gt=0, description="Minimum planet mass (Earth masses)"),
    max_masse: float | None = Query(None, gt=0, description="Maximum planet mass (Earth masses)"),
    min_st_teff: float | None = Query(None, gt=0, description="Minimum host star effective temperature (K)"),
    max_st_teff: float | None = Query(None, gt=0, description="Maximum host star effective temperature (K)"),
    min_st_rad: float | None = Query(None, gt=0, description="Minimum host star radius (Solar radii)"),
    max_st_rad: float | None = Query(None, gt=0, description="Maximum host star radius (Solar radii)"),
    min_st_mass: float | None = Query(None, gt=0, description="Minimum host star mass (Solar masses)"),
    max_st_mass: float | None = Query(None, gt=0, description="Maximum host star mass (Solar masses)"),
    include_deleted: bool = Query(False, description="Include soft-deleted planets as well"),
    sort_by: Literal[
        "id",
        "name",
        "disc_year",
        "disc_method",
        "orbperd",
        "rade",
        "masse",
        "st_teff",
        "st_rad",
        "st_mass",
        "created_at",
    ] = Query("id", description="Column to sort by"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort direction"),
):
    """Retrieve planets with advanced filtering, sorting and pagination metadata."""

    conditions = []
    if not include_deleted:
        conditions.append(Planet.is_deleted == False)

    if min_year is not None and max_year is not None and min_year > max_year:
        raise HTTPException(status_code=400, detail="min_year must be <= max_year")

    if min_orbperd is not None and max_orbperd is not None and min_orbperd > max_orbperd:
        raise HTTPException(status_code=400, detail="min_orbperd must be <= max_orbperd")

    if min_rade is not None and max_rade is not None and min_rade > max_rade:
        raise HTTPException(status_code=400, detail="min_rade must be <= max_rade")

    if min_masse is not None and max_masse is not None and min_masse > max_masse:
        raise HTTPException(status_code=400, detail="min_masse must be <= max_masse")

    if min_st_teff is not None and max_st_teff is not None and min_st_teff > max_st_teff:
        raise HTTPException(status_code=400, detail="min_st_teff must be <= max_st_teff")

    if min_st_rad is not None and max_st_rad is not None and min_st_rad > max_st_rad:
        raise HTTPException(status_code=400, detail="min_st_rad must be <= max_st_rad")

    if min_st_mass is not None and max_st_mass is not None and min_st_mass > max_st_mass:
        raise HTTPException(status_code=400, detail="min_st_mass must be <= max_st_mass")

    if name:
        q = name.strip()
        if q:
            conditions.append(Planet.name.ilike(f"%{q}%"))

    if disc_method:
        normalized_method = disc_method.strip()
        if normalized_method:
            conditions.append(func.lower(Planet.disc_method) == normalized_method.lower())

    if min_year is not None:
        conditions.append(Planet.disc_year >= min_year)
    if max_year is not None:
        conditions.append(Planet.disc_year <= max_year)

    if min_orbperd is not None:
        conditions.append(Planet.orbperd >= min_orbperd)
    if max_orbperd is not None:
        conditions.append(Planet.orbperd <= max_orbperd)

    if min_rade is not None:
        conditions.append(Planet.rade >= min_rade)
    if max_rade is not None:
        conditions.append(Planet.rade <= max_rade)

    if min_masse is not None:
        conditions.append(Planet.masse >= min_masse)
    if max_masse is not None:
        conditions.append(Planet.masse <= max_masse)

    if min_st_teff is not None:
        conditions.append(Planet.st_teff >= min_st_teff)
    if max_st_teff is not None:
        conditions.append(Planet.st_teff <= max_st_teff)

    if min_st_rad is not None:
        conditions.append(Planet.st_rad >= min_st_rad)
    if max_st_rad is not None:
        conditions.append(Planet.st_rad <= max_st_rad)

    if min_st_mass is not None:
        conditions.append(Planet.st_mass >= min_st_mass)
    if max_st_mass is not None:
        conditions.append(Planet.st_mass <= max_st_mass)

    sortable_fields = {
        "id": Planet.id,
        "name": Planet.name,
        "disc_year": Planet.disc_year,
        "disc_method": Planet.disc_method,
        "orbperd": Planet.orbperd,
        "rade": Planet.rade,
        "masse": Planet.masse,
        "st_teff": Planet.st_teff,
        "st_rad": Planet.st_rad,
        "st_mass": Planet.st_mass,
        "created_at": Planet.created_at,
    }

    order_column = sortable_fields[sort_by]
    primary_order = order_column.asc() if sort_order == "asc" else order_column.desc()
    secondary_order = Planet.id.asc() if sort_order == "asc" else Planet.id.desc()

    stmt = select(Planet)
    if conditions:
        stmt = stmt.where(*conditions)

    total_stmt = select(func.count()).select_from(Planet)
    if conditions:
        total_stmt = total_stmt.where(*conditions)

    total = db.execute(total_stmt).scalar_one()

    stmt = stmt.order_by(primary_order, secondary_order).limit(limit).offset(offset)

    items = db.execute(stmt).scalars().all()

    return PlanetListResponse(items=items, limit=limit, offset=offset, total=int(total))


@router.get(
    "/count",
    response_model=PlanetCount,
    summary="Count planets",
    description="Returns the total number of non-deleted planets in the database."
)
def count_planets(db: Session = Depends(get_db)):
    """
    Count the number of planets.

    This endpoint executes a simple aggregate query to count the total
    number of planets that are not soft-deleted.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        PlanetCount: A dictionary with a single `count` field.
    """
    total = db.execute(
        select(func.count()).select_from(Planet).where(Planet.is_deleted == False)
    ).scalar()
    return {"count": total}



@router.get(
    "/method-counts",
    response_model=list[MethodCount],
    summary="Get discovery method counts",
    description="Returns the number of planets grouped by their discovery method."
)
def method_counts(db: Session = Depends(get_db)):
    """
    Count planets by discovery method.

    This endpoint aggregates all planets in the database and returns
    how many planets were discovered by each discovery method.
    Soft-deleted planets are excluded from the count.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        list[MethodCount]: A list of objects, each containing:
            - `disc_method` (str): The discovery method name.
            - `count` (int): Number of planets found with this method.
    """
    stmt = (
        select(Planet.disc_method, func.count())
        .where(Planet.is_deleted == False)
        .group_by(Planet.disc_method)
        .order_by(func.count().desc())
    )

    rows = db.execute(stmt).all()

    return [
        {"disc_method": m, "count": int(c)}
        for m, c in rows
    ]


@router.get(
    "/stats",
    response_model=PlanetStats,
    summary="Get aggregate planet statistics",
    description="Returns min/max/average values for key planet and host star metrics.",
)
def planet_statistics(db: Session = Depends(get_db)):
    """Return aggregated statistics for all non-deleted planets."""

    stats_stmt = (
        select(
            func.count(Planet.id).label("count"),
            func.min(Planet.orbperd).label("orbperd_min"),
            func.max(Planet.orbperd).label("orbperd_max"),
            func.avg(Planet.orbperd).label("orbperd_avg"),
            func.min(Planet.rade).label("rade_min"),
            func.max(Planet.rade).label("rade_max"),
            func.avg(Planet.rade).label("rade_avg"),
            func.min(Planet.masse).label("masse_min"),
            func.max(Planet.masse).label("masse_max"),
            func.avg(Planet.masse).label("masse_avg"),
            func.min(Planet.st_teff).label("st_teff_min"),
            func.max(Planet.st_teff).label("st_teff_max"),
            func.avg(Planet.st_teff).label("st_teff_avg"),
            func.min(Planet.st_rad).label("st_rad_min"),
            func.max(Planet.st_rad).label("st_rad_max"),
            func.avg(Planet.st_rad).label("st_rad_avg"),
            func.min(Planet.st_mass).label("st_mass_min"),
            func.max(Planet.st_mass).label("st_mass_max"),
            func.avg(Planet.st_mass).label("st_mass_avg"),
        )
        .where(Planet.is_deleted == False)
    )

    result = db.execute(stats_stmt).mappings().one()

    def _summary(prefix: str) -> dict[str, float | None]:
        return {
            "min": float(result[f"{prefix}_min"]) if result[f"{prefix}_min"] is not None else None,
            "max": float(result[f"{prefix}_max"]) if result[f"{prefix}_max"] is not None else None,
            "avg": float(result[f"{prefix}_avg"]) if result[f"{prefix}_avg"] is not None else None,
        }

    return PlanetStats(
        count=int(result["count"] or 0),
        orbperd=_summary("orbperd"),
        rade=_summary("rade"),
        masse=_summary("masse"),
        st_teff=_summary("st_teff"),
        st_rad=_summary("st_rad"),
        st_mass=_summary("st_mass"),
    )


@router.get(
    "/timeline",
    response_model=list[PlanetTimelinePoint],
    summary="Get discovery timeline",
    description="Returns the number of planets discovered for each year.",
)
def planet_timeline(
    db: Session = Depends(get_db),
    start_year: int | None = Query(None, ge=0, description="Optional start year filter"),
    end_year: int | None = Query(None, ge=0, description="Optional end year filter"),
    include_deleted: bool = Query(False, description="Include soft-deleted discoveries"),
):
    """Return discovery counts grouped by year with optional bounds."""

    if start_year is not None and end_year is not None and start_year > end_year:
        raise HTTPException(status_code=400, detail="start_year must be <= end_year")

    stmt = select(Planet.disc_year, func.count()).group_by(Planet.disc_year)

    if not include_deleted:
        stmt = stmt.where(Planet.is_deleted == False)
    if start_year is not None:
        stmt = stmt.where(Planet.disc_year >= start_year)
    if end_year is not None:
        stmt = stmt.where(Planet.disc_year <= end_year)

    stmt = stmt.order_by(Planet.disc_year.asc())

    rows = db.execute(stmt).all()

    return [
        PlanetTimelinePoint(disc_year=int(year), count=int(count))
        for year, count in rows
    ]


@router.get(
    "/method/{disc_method}/stats",
    response_model=PlanetMethodStats,
    summary="Get statistics for a discovery method",
    description="Returns aggregate statistics scoped to a specific discovery method.",
)
def method_statistics(disc_method: str, db: Session = Depends(get_db)):
    """Return aggregated statistics for the provided discovery method."""

    normalized = disc_method.strip()
    if not normalized:
        raise HTTPException(status_code=400, detail="Discovery method must be provided")

    canonical = db.execute(
        select(Planet.disc_method)
        .where(func.lower(Planet.disc_method) == normalized.lower())
        .where(Planet.is_deleted == False)
        .limit(1)
    ).scalar_one_or_none()

    if canonical is None:
        raise HTTPException(status_code=404, detail=f"No planets found for discovery method '{disc_method}'")

    stats_stmt = (
        select(
            func.count(Planet.id).label("count"),
            func.min(Planet.orbperd).label("orbperd_min"),
            func.max(Planet.orbperd).label("orbperd_max"),
            func.avg(Planet.orbperd).label("orbperd_avg"),
            func.percentile_cont(0.5).within_group(Planet.orbperd).label("orbperd_median"),
            func.min(Planet.rade).label("rade_min"),
            func.max(Planet.rade).label("rade_max"),
            func.avg(Planet.rade).label("rade_avg"),
            func.percentile_cont(0.5).within_group(Planet.rade).label("rade_median"),
            func.min(Planet.masse).label("masse_min"),
            func.max(Planet.masse).label("masse_max"),
            func.avg(Planet.masse).label("masse_avg"),
            func.percentile_cont(0.5).within_group(Planet.masse).label("masse_median"),
            func.min(Planet.st_teff).label("st_teff_min"),
            func.max(Planet.st_teff).label("st_teff_max"),
            func.avg(Planet.st_teff).label("st_teff_avg"),
            func.percentile_cont(0.5).within_group(Planet.st_teff).label("st_teff_median"),
            func.min(Planet.st_rad).label("st_rad_min"),
            func.max(Planet.st_rad).label("st_rad_max"),
            func.avg(Planet.st_rad).label("st_rad_avg"),
            func.percentile_cont(0.5).within_group(Planet.st_rad).label("st_rad_median"),
            func.min(Planet.st_mass).label("st_mass_min"),
            func.max(Planet.st_mass).label("st_mass_max"),
            func.avg(Planet.st_mass).label("st_mass_avg"),
            func.percentile_cont(0.5).within_group(Planet.st_mass).label("st_mass_median"),
        )
        .where(func.lower(Planet.disc_method) == normalized.lower())
        .where(Planet.is_deleted == False)
    )

    result = db.execute(stats_stmt).mappings().one()

    def _summary(prefix: str) -> dict[str, float | None]:
        return {
            "min": float(result[f"{prefix}_min"]) if result[f"{prefix}_min"] is not None else None,
            "max": float(result[f"{prefix}_max"]) if result[f"{prefix}_max"] is not None else None,
            "avg": float(result[f"{prefix}_avg"]) if result[f"{prefix}_avg"] is not None else None,
            "median": float(result[f"{prefix}_median"]) if result.get(f"{prefix}_median") is not None else None,
        }

    return PlanetMethodStats(
        disc_method=canonical,
        count=int(result["count"] or 0),
        orbperd=_summary("orbperd"),
        rade=_summary("rade"),
        masse=_summary("masse"),
        st_teff=_summary("st_teff"),
        st_rad=_summary("st_rad"),
        st_mass=_summary("st_mass"),
    )


@router.get(
    "/{planet_id}",
    response_model=PlanetOut,
    summary="Get planet by ID",
    description="Returns a single planet by ID; soft-deleted ones are treated as not found."
)
def get_planet(planet_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a planet by its ID.

    Args:
        planet_id (int): The ID of the planet.
        db (Session): SQLAlchemy database session.

    Returns:
        PlanetOut: The planet record.

    Raises:
        HTTPException: 404 if the planet does not exist or is soft-deleted.
    """
    planet = db.get(Planet, planet_id)

    if not planet or planet.is_deleted:
        raise HTTPException(status_code=404, detail=f"Planet with id={planet_id} not found")

    return planet


@router.get(
    "/by-name/{planet_name}",
    response_model=PlanetOut,
    summary="Get planet by name",
    description="Returns a single planet by its name (case-insensitive); excludes soft-deleted records."
)
def get_planet_by_name(planet_name: str, db: Session = Depends(get_db)):
    """
    Retrieve a planet by its name (case-insensitive).

    Args:
        planet_name (str): The name of the planet.
        db (Session): SQLAlchemy database session.

    Returns:
        PlanetOut: The planet record.

    Raises:
        HTTPException: 404 if no matching planet is found or it is soft-deleted.
    """
    q = planet_name.strip()

    stmt = (
        select(Planet)
        .where(func.lower(Planet.name) == func.lower(q))
        .where(Planet.is_deleted == False)
    )

    planet = db.execute(stmt).scalar_one_or_none()

    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet named '{planet_name}' not found")

    return planet


@router.get(
    "/admin/deleted",
    response_model=list[DeletedPlanetOut],
    summary="List soft-deleted planets (admin)",
    description="Lists soft-deleted planets ordered by deletion time (most recent first).",
    dependencies=[Depends(api_key_auth)],
)
def list_deleted_planets(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    List all soft-deleted planets with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        limit (int): Maximum number of results to return.
        offset (int): Number of results to skip.

    Returns:
        list[DeletedPlanetOut]: A list of soft-deleted planets with ID, name, and deletion timestamp.
    """
    stmt = (
        select(Planet)
        .where(Planet.is_deleted == True)
        .order_by(Planet.deleted_at.desc())
        .limit(limit)
        .offset(offset)
    )

    rows = db.execute(stmt).scalars().all()

    return [
        DeletedPlanetOut(id=p.id, name=p.name, deleted_at=p.deleted_at)
        for p in rows
    ]
@router.patch(
    "/{planet_id}",
    response_model=PlanetOut,
    summary="Partially update a planet",
    description="Updates only provided fields; others remain unchanged."
)
def update_planet_partial(planet_id: int, updates: PlanetUpdate, db: Session = Depends(get_db)):
    """
    Partially update an existing planet.

    Args:
        planet_id (int): The ID of the planet to update.
        updates (PlanetUpdate): The fields to update.
        db (Session): SQLAlchemy database session.

    Returns:
        PlanetOut: The updated planet.

    Raises:
        HTTPException: 400 if the payload is empty.
        HTTPException: 404 if the planet does not exist.
        HTTPException: 409 if a unique constraint fails.
    """

    planet = db.get(Planet, planet_id)
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")

    data = updates.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(status_code=400, detail="Empty update payload")

    for k, v in data.items():
        setattr(planet, k, v)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Unique constraint failed")

    db.refresh(planet)
    return planet


@router.delete(
    "/{planet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete a planet",
    description="Marks a planet as deleted; returns 204 with no content.",
    dependencies=[Depends(api_key_auth)],
)
def delete_planet(planet_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a planet.

    Args:
        planet_id (int): The ID of the planet to delete.
        db (Session): SQLAlchemy database session.

    Returns:
        None: Responds with 204 No Content.

    Raises:
        HTTPException: 404 if the planet does not exist or is already deleted.
    """

    planet = db.get(Planet, planet_id)
    if not planet or planet.is_deleted:
        raise HTTPException(status_code=404, detail=f"Planet with id={planet_id} not found")

    planet.is_deleted = True

    planet.deleted_at = datetime.now(timezone.utc)

    db.commit()

    return


@router.delete(
    "/admin/hard-delete/{planet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hard delete a single planet (only if soft-deleted)",
    description="Permanently deletes a planet from the database, allowed only if it was previously soft-deleted.",
    dependencies=[Depends(api_key_auth)],
)
def hard_delete_planet(
    planet_id: int,
    confirm: Literal[True, False] = Query(..., description="Must be true to proceed"),
    db: Session = Depends(get_db),
):
    """
    Permanently delete a planet record (hard delete).

    Unlike soft delete, this operation removes the planet completely
    from the database. Only planets that are already soft-deleted can
    be hard-deleted, ensuring accidental data loss is avoided.

    Args:
        planet_id (int): The ID of the planet to hard delete.
        confirm (bool): Must be True (`?confirm=true`) to proceed.
        db (Session): SQLAlchemy database session.

    Returns:
        None: Responds with 204 No Content on success.

    Raises:
        HTTPException 400: If `confirm=true` is not provided.
        HTTPException 404: If the planet does not exist.
        HTTPException 409: If the planet is not soft-deleted.
    """
    if not confirm:
        raise HTTPException(status_code=400, detail="Add ?confirm=true to proceed")

    planet = db.get(Planet, planet_id)
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet {planet_id} not found")

    if not planet.is_deleted:
        raise HTTPException(status_code=409, detail="Planet is not soft-deleted")

    db.delete(planet)
    db.commit()
    return



@router.post(
    "/{planet_id}/restore",
    status_code=status.HTTP_200_OK,
    summary="Restore a soft-deleted planet",
    description="Clears soft-delete flags and makes the planet visible again.",
    dependencies=[Depends(api_key_auth)],
)
def restore_planet(planet_id: int, db: Session = Depends(get_db)):
    """
    Restore a soft-deleted planet.

    Args:
        planet_id (int): The ID of the planet to restore.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: A success message.

    Raises:
        HTTPException: 404 if the planet does not exist.
        HTTPException: 409 if the planet is already active.
    """
    planet = db.get(Planet, planet_id)

    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet with id={planet_id} not found")

    if not planet.is_deleted:
        raise HTTPException(status_code=409, detail="Planet is not deleted")

    # Geri al
    planet.is_deleted = False
    planet.deleted_at = None
    db.commit()
    db.refresh(planet)

    return {"ok": True, "message": f"Planet {planet_id} restored."}



@router.delete(
    "/admin/delete-all",
    summary="Truncate planets table (admin)",
    description="Dangerous operation: truncates the planets table and resets identity.",
    dependencies=[Depends(api_key_auth)],
)
def wipe_planets(confirm: Literal[True, False] = Query(..., description="Set true to actually delete all rows"),
                 db: Session = Depends(get_db)):
    """
    Truncate the planets table and reset identity (admin only).

    Args:
        confirm (bool): Must be True to confirm deletion.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: A success message.

    Raises:
        HTTPException: 400 if confirm is not set to True.
        HTTPException: 500 if the truncate fails.
    """
    if not confirm:
        raise HTTPException(status_code=400, detail="Add ?confirm=true to proceed")

    try:
        db.execute(text("TRUNCATE TABLE planets RESTART IDENTITY;"))
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to truncate: {e}")

    return {"ok": True, "message": "All planets deleted, IDs reset."}


@router.get(
    "/methods",
    response_model=list[str],
    summary="List discovery methods",
    description="Returns a sorted list of unique discovery methods. Excludes soft-deleted records by default."
)
def list_methods(
    db: Session = Depends(get_db),
    include_deleted: bool = Query(False, description="Include soft-deleted planets when extracting methods"),
    search: str | None = Query(None, description="Case-insensitive substring filter on method name"),
):
    # Base statement: distinct discovery methods
    stmt = select(func.distinct(Planet.disc_method)).where(Planet.disc_method.isnot(None))

    # Exclude soft-deleted unless requested
    if not include_deleted:
        stmt = stmt.where(Planet.is_deleted == False)

    # Optional substring search (case-insensitive)
    if search:
        q = search.strip()
        if q:
            stmt = stmt.where(Planet.disc_method.ilike(f"%{q}%"))

    # Sort alphabetically for stable UX
    stmt = stmt.order_by(func.lower(Planet.disc_method).asc())

    rows = db.execute(stmt).all()
    # rows is a list of 1-tuples like [('Transit',), ('Radial Velocity',) ...]
    methods = [r[0] for r in rows if r[0] is not None]

    return methods
