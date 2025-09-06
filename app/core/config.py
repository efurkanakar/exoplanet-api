"""
Application configuration.

Loads settings from environment variables or .env file
using Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    API_KEY: str
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    model_config = SettingsConfigDict(
        env_file=".env",
    )


# Singleton instance
settings = Settings()