from fastapi import APIRouter

router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"]
)

@router.get("/ping")
async def ping_vendor():
    return {"message": "Vendor routes working!"}
