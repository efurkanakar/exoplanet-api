# app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator  # ← EKLE

class Settings(BaseSettings):
    DATABASE_URL: str
    API_KEY: str
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://efurkanakar.github.io"
    ]
    CORS_ORIGIN_REGEX: str | None = None
    CORS_ALLOW_CREDENTIALS: bool = False

    # comma-separated env -> list[str]
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            # "a,b,c" -> ["a", "b", "c"]
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=None if os.getenv("ENV", "").lower() in {"prod", "production"} or os.getenv("RENDER") else ".env"
    )

settings = Settings()
