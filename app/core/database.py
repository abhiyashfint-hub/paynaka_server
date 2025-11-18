"""Database connection and initialization"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Global MongoDB client
mongodb_client: AsyncIOMotorClient = None

async def connect_to_mongo():
    """Connect to MongoDB and initialize Beanie"""
    global mongodb_client
    
    try:
        logger.info("🔌 Connecting to MongoDB...")
        
        # Create Motor client
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000
        )
        
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info("✅ MongoDB connected successfully!")
        
        # Get database
        database = mongodb_client[settings.DATABASE_NAME]
        
        # Import models for Beanie initialization
        from app.models.customer_model import Customer
        from app.models.user_model import User
        
        # Initialize Beanie with document models
        await init_beanie(
            database=database,
            document_models=[Customer, User]
        )
        
        logger.info(f"✅ Beanie initialized with database: {settings.DATABASE_NAME}")
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise e

async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client
    
    if mongodb_client:
        logger.info("🔌 Closing MongoDB connection...")
        mongodb_client.close()
        logger.info("✅ MongoDB connection closed")

def get_database():
    """Get database instance (for dependency injection)"""
    if mongodb_client is None:
        raise Exception("Database not initialized. Call connect_to_mongo() first.")
    return mongodb_client[settings.DATABASE_NAME]