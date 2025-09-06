import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    API_KEY: str
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    model_config = SettingsConfigDict(
        env_file=None if os.getenv("ENV", "").lower() in {"prod","production"} or os.getenv("RENDER") else ".env"
    )

settings = Settings()
