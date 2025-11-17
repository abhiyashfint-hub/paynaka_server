from fastapi import APIRouter
from app.core.database import database

router = APIRouter()

@router.get("/test-db")
async def test_db():
    collections = await database.list_collection_names()
    return {"collections": collections}
