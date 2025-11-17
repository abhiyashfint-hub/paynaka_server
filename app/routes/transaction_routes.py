from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def transaction_ping():
    return {"message": "Transaction route working"}
