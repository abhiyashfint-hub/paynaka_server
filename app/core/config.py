# app/core/config.py

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Paynaka Backend"
    APP_VERSION: str = "1.0.0"

    # Mongo
    MONGO_URL: str
    DATABASE_NAME: str = "paynaka_db"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # Allow all, or specify list

    class Config:
        env_file = ".env"


settings = Settings()
