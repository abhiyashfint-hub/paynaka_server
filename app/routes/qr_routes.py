from fastapi import APIRouter, HTTPException
from app.core.database import get_database

router = APIRouter()

@router.get("/qr/{vendor_id}")
async def get_vendor_qr(vendor_id: str):
    db = get_database()

    vendor = await db["vendors"].find_one({"vendor_id": vendor_id})

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return {
        "vendor_id": vendor["vendor_id"],
        "vendor_name": vendor["vendor_name"],
        "qr_token": vendor.get("qr_token")
    }
