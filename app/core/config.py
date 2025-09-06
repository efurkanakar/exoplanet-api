"""
Application configuration.

Loads settings from environment variables or .env file
using Pydantic BaseSettings.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    API_KEY: str
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    _env_file = ".env" if os.getenv("ENV", "").lower() not in {"prod", "production"} and not os.getenv("RENDER") else None
    model_config = SettingsConfigDict(env_file=_env_file)

settings = Settings()
