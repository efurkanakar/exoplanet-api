from pydantic import BaseModel, Field, field_validator, ConfigDict
# app/schemas/planet.py
from typing import Optional


class PlanetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    disc_method: str
    disc_year: int = Field(..., ge=1900, le=2100)
    orbperd: float = Field(..., gt=0)
    rade: float = Field(..., gt=0)
    masse: float = Field(..., gt=0)
    st_teff: float = Field(..., gt=0)
    st_rad: float = Field(..., gt=0)
    st_mass: float = Field(..., gt=0)


@field_validator("disc_method")
@classmethod
def normalize_method(cls, v: str) -> str:
    return " ".join(w.capitalize() for w in v.strip().split())


class PlanetOut(BaseModel):
    id: int
    name: str
    disc_method: str
    disc_year: int
    orbperd: float
    rade: float
    masse: float
    st_teff: float
    st_rad: float
    st_mass: float


    model_config = {"from_attributes": True}



class PlanetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    disc_method: Optional[str] = None
    disc_year: Optional[int] = Field(None, ge=1900, le=2100)
    orbperd: Optional[float] = Field(None, gt=0)
    rade: Optional[float] = Field(None, gt=0)
    masse: Optional[float] = Field(None, gt=0)
    st_teff: Optional[float] = Field(None, gt=0)
    st_rad: Optional[float] = Field(None, gt=0)
    st_mass: Optional[float] = Field(None, gt=0)

    model_config = ConfigDict(extra="forbid")  # bilinmeyen alanları reddet
