# app/routes/health_routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"status": "success", "message": "Paynaka API is healthy!"}
