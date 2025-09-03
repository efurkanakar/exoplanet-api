"""
Planet API routes.

This module defines all RESTful API endpoints related to the `Planet` entity.
It covers CRUD operations, soft-delete/restore functionality, and reporting
utilities such as counting and grouping by discovery method.

Endpoints:
    - POST   /planets/             : Create a new planet
    - GET    /planets/             : List planets with optional filters
    - GET    /planets/count        : Count all active planets
    - GET    /planets/method-counts: Aggregate planets by discovery method
    - GET    /planets/{id}         : Retrieve a planet by ID
    - GET    /planets/by-name/{n}  : Retrieve a planet by name
    - PATCH  /planets/{id}         : Partially update a planet
    - DELETE /planets/{id}         : Soft-delete a planet
    - POST   /planets/{id}/restore : Restore a soft-deleted planet
    - GET    /planets/admin/deleted: List deleted planets (admin only)
    - DELETE /planets/admin/delete-all : Truncate planets table (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Response, status, Request
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from datetime import datetime, timezone

from app.db.session import get_db
from app.db.models import Planet
from app.schemas.planet import PlanetCreate, PlanetOut, PlanetUpdate, PlanetCount, MethodCount, DeletedPlanetOut
from app.core.security import api_key_auth


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
    response_model=List[PlanetOut],
    summary="List planets",
    description="Lists non-deleted planets with optional filters and pagination."
)
def list_planets(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    name: str | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    include_deleted: bool = False,
):
    """
    Retrieve a list of planets.

    Returns planets that are not soft-deleted by default, with support for
    basic filtering and pagination.

    Args:
        db (Session): SQLAlchemy database session.
        limit (int): Page size (1–200).
        offset (int): Number of records to skip.
        name (str | None): Case-insensitive substring filter on planet name.
        min_year (int | None): Minimum discovery year (inclusive).
        max_year (int | None): Maximum discovery year (inclusive).
        include_deleted (bool): If True, include soft-deleted records as well.

    Returns:
        List[PlanetOut]: The list of planets matching the criteria.
    """

    stmt = select(Planet)
    if not include_deleted:
        stmt = stmt.where(Planet.is_deleted == False)

    if min_year is not None and max_year is not None and min_year > max_year:
        raise HTTPException(status_code=400, detail="min_year must be <= max_year")

    if name:
        q = name.strip()
        if q:
            stmt = stmt.where(func.ilike(Planet.name, f"%{q}%"))

    if min_year is not None:
        stmt = stmt.where(Planet.disc_year >= min_year)
    if max_year is not None:
        stmt = stmt.where(Planet.disc_year <= max_year)


    stmt = stmt.order_by(Planet.id.desc()).limit(limit).offset(offset)

    return db.execute(stmt).scalars().all()


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
def wipe_planets(confirm: bool = Query(False, description="Set true to actually delete all rows"),
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
