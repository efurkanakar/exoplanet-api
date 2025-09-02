from fastapi import APIRouter, Depends, HTTPException, Query, Body, Response, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError

from datetime import datetime

from app.db.session import get_db
from app.db.models import Planet
from app.schemas.planet import PlanetCreate, PlanetOut, PlanetUpdate
from app.core.security import api_key_auth


router = APIRouter(prefix="/planets", tags=["planets"])


@router.post("/", response_model=PlanetOut, status_code=status.HTTP_201_CREATED)
def create_planet(payload: PlanetCreate, response: Response, db: Session = Depends(get_db)):
    planet = Planet(**payload.model_dump())
    db.add(planet)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Planet '{payload.name}' already exists.")
    db.refresh(planet)
    response.headers["Location"] = f"/planets/{planet.id}"
    return planet


# Listeleme (normal)
@router.get("/", response_model=List[PlanetOut])
def list_planets(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    name: str | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
):
    stmt = select(Planet).where(Planet.is_deleted == False)
    if name: stmt = stmt.where(func.ilike(Planet.name, f"%{name}%"))
    if min_year: stmt = stmt.where(Planet.disc_year >= min_year)
    if max_year: stmt = stmt.where(Planet.disc_year <= max_year)
    stmt = stmt.order_by(Planet.id.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


@router.get("/count")
def count_planets(db: Session = Depends(get_db)):
    total = db.execute(select(func.count()).select_from(Planet)).scalar()
    return {"count": total}


@router.get("/method-counts")
def method_counts(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Planet.disc_method, func.count())
        .group_by(Planet.disc_method)
        .order_by(func.count().desc())
    ).all()
    return [{"disc_method": m, "count": int(c)} for m, c in rows]


@router.get("/{planet_id}", response_model=PlanetOut)
def get_planet(planet_id: int, db: Session = Depends(get_db)):
    planet = db.get(Planet, planet_id)
    if not planet or planet.is_deleted:
        raise HTTPException(status_code=404, detail=f"Planet with id={planet_id} not found")
    return planet


@router.get("/by-name/{planet_name}", response_model=PlanetOut)
def get_planet_by_name(planet_name: str, db: Session = Depends(get_db)):
    stmt = (
        select(Planet)
        .where(func.lower(Planet.name) == planet_name.lower())
        .where(Planet.is_deleted == False)
    )
    planet = db.execute(stmt).scalar_one_or_none()
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet named '{planet_name}' not found")
    return planet


@router.get("/admin/deleted", dependencies=[Depends(api_key_auth)])
def list_deleted_planets(db: Session = Depends(get_db),
                         limit: int = Query(50, ge=1, le=200),
                         offset: int = Query(0, ge=0)):
    stmt = select(Planet).where(Planet.is_deleted == True).order_by(Planet.deleted_at.desc()).limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()
    # İstersen burada özel bir Out şeması kullanıp deleted_at alanını da dönebilirsin
    return [{"id": p.id, "name": p.name, "deleted_at": p.deleted_at} for p in rows]


@router.patch("/{planet_id}", response_model=PlanetOut)
def update_planet_partial(planet_id: int, updates: PlanetUpdate, db: Session = Depends(get_db)):
    planet = db.get(Planet, planet_id)
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")

    data = updates.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(planet, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Unique constraint failed")
    db.refresh(planet)
    return planet


@router.delete("/{planet_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(api_key_auth)])
def delete_planet(planet_id: int, db: Session = Depends(get_db)):
    """Soft delete: kaydı silmek yerine is_deleted=True yapar."""
    planet = db.get(Planet, planet_id)
    # Zaten silinmişse de 404 verelim ki dışarıya 'yok' gibi davransın
    if not planet or planet.is_deleted:
        raise HTTPException(status_code=404, detail=f"Planet with id={planet_id} not found")

    planet.is_deleted = True
    planet.deleted_at = datetime.utcnow()
    db.commit()
    return  # 204 No Content

@router.post("/{planet_id}/restore", status_code=status.HTTP_200_OK, dependencies=[Depends(api_key_auth)])
def restore_planet(planet_id: int, db: Session = Depends(get_db)):
    """Soft delete'i geri al: is_deleted=False, deleted_at=None."""
    planet = db.get(Planet, planet_id)
    if not planet:
        raise HTTPException(status_code=404, detail=f"Planet with id={planet_id} not found")
    if not planet.is_deleted:
        # Zaten aktifse 409 mantıklı
        raise HTTPException(status_code=409, detail="Planet is not deleted")

    planet.is_deleted = False
    planet.deleted_at = None
    db.commit()
    db.refresh(planet)
    return {"ok": True, "message": f"Planet {planet_id} restored."}


@router.delete("/admin/delete-all", dependencies=[Depends(api_key_auth)])
def wipe_planets(confirm: bool = Query(False, description="Set true to actually delete all rows"),
                 db: Session = Depends(get_db)):
    if not confirm:
        raise HTTPException(status_code=400, detail="Add ?confirm=true to proceed")
    try:
        db.execute(text("TRUNCATE TABLE planets RESTART IDENTITY;"))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to truncate: {e}")
    return {"ok": True, "message": "All planets deleted, IDs reset."}
{"ok": True, "message": "All planets deleted, IDs reset."}