from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped
from app.db.base import Base
from datetime import datetime

class Planet(Base):
    __tablename__ = "planets"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, nullable=False, unique=True, index=True)
    disc_method: Mapped[str] = Column(String, nullable=False, index=True)
    disc_year: Mapped[int] = Column(Integer, nullable=False, index=True)
    orbperd: Mapped[float] = Column(Float, nullable=False)
    rade: Mapped[float] = Column(Float, nullable=False)
    masse: Mapped[float] = Column(Float, nullable=False)
    st_teff: Mapped[float] = Column(Float, nullable=False)
    st_rad: Mapped[float] = Column(Float, nullable=False)
    st_mass: Mapped[float] = Column(Float, nullable=False)

    # Soft delete
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
