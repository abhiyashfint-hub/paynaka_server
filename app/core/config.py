import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Paynaka Backend API"
    ENV: str = os.getenv("ENV", "development")

    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL")

    # JWT Config
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "PAYNAKA_SECRET_2025")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day

settings = Settings()
