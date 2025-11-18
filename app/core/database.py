# app/core/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
mongodb_client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Connect to MongoDB and initialize Beanie"""
    global mongodb_client

    try:
        logger.info("🔌 Connecting to MongoDB...")

        mongodb_client = AsyncIOMotorClient(
            settings.MONGO_URL,          # <-- FIXED NAME
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000
        )

        # ping test
        await mongodb_client.admin.command("ping")
        logger.info("✅ MongoDB connected!")

        # select DB
        database = mongodb_client[settings.DATABASE_NAME]

        # import models
        from app.models.customer_model import Customer
        from app.models.user_model import User

        await init_beanie(
            database=database,
            document_models=[Customer, User]
        )

        logger.info("✅ Beanie initialized!")

    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise e


async def close_mongo_connection():
    global mongodb_client
    if mongodb_client:
        logger.info("🔌 Closing MongoDB connection...")
        mongodb_client.close()
        logger.info("✅ MongoDB closed")


def get_database():
    if mongodb_client is None:
        raise Exception("Database not initialized.")
    return mongodb_client[settings.DATABASE_NAME]
