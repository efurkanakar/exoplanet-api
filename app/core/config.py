import os
from pydantic import BaseModel


class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://furkan:1234@localhost:5432/testdb")
    API_KEY: str = os.getenv("API_KEY", "secret")


settings = Settings()