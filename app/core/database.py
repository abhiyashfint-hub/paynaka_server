from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.customer_model import Customer
from app.core.config import settings

async def init_db():
    print("📡 Connecting to MongoDB...")

    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client.get_default_database()

    await init_beanie(
        database=db,
        document_models=[
            Customer,  # ONLY CUSTOMER FOR NOW
        ]
    )

    print("✅ MongoDB connected successfully!")
