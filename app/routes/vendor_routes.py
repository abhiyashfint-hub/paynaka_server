"""Vendor routes (placeholder for future implementation)"""
from fastapi import APIRouter

router = APIRouter(prefix="/vendor", tags=["Vendor"])

@router.get("/")
async def get_vendors():
    """Get all vendors (placeholder)"""
    return {
        "message": "Vendor routes coming soon",
        "vendors": []
    }

@router.get("/{vendor_id}")
async def get_vendor(vendor_id: str):
    """Get vendor by ID (placeholder)"""
    return {
        "message": f"Vendor {vendor_id} details coming soon"
    }