from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def user_ping():
    return {"message": "User route working"}
