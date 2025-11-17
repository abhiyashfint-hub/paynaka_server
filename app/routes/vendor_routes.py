from fastapi import APIRouter

router = APIRouter()

@router.get("/vendor-test")
async def vendor_test():
    return {"message": "Vendor router active"}
