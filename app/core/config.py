"""
Application configuration.

Loads settings from environment variables or .env file
using Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration class."""

    DATABASE_URL: str
    API_KEY: str

    # Pydantic settings config
    model_config = SettingsConfigDict(
        env_file=".env")


# Singleton instance
settings = Settings()