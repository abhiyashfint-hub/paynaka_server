from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from app.core.database import db
import secrets

router = APIRouter(prefix="/qr", tags=["QR Code"])

@router.get("/generate/{vendor_id}")
async def generate_qr_token(vendor_id: str):
    """
    Generate dynamic QR token for vendor
    Expires in 60 seconds
    """
    try:
        # Check if vendor exists
        vendor = await db.vendors.find_one({"vendor_id": vendor_id})
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail="Vendor not found"
            )
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        qr_data = f"paynaka://scan/{vendor_id}/{token}"
        
        # Store token in database
        qr_doc = {
            "vendor_id": vendor_id,
            "token": token,
            "qr_data": qr_data,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=60),
            "used": False,
            "used_by": None,
            "used_at": None,
        }
        
        await db.qr_tokens.insert_one(qr_doc)
        
        return {
            "success": True,
            "qr_data": qr_data,
            "vendor_id": vendor_id,
            "expires_in": 60,
            "message": "QR token generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating QR: {str(e)}"
        )

@router.post("/validate")
async def validate_qr_token(
    qr_data: str,
    customer_id: str,
    customer_location: dict = None
):
    """
    Validate QR token before transaction
    Checks: expiry, location, usage
    """
    try:
        # Parse QR data
        if not qr_data.startswith("paynaka://scan/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid QR code format"
            )
        
        parts = qr_data.replace("paynaka://scan/", "").split("/")
        vendor_id = parts[0]
        token = parts[1]
        
        # Find token in database
        qr_token = await db.qr_tokens.find_one({
            "vendor_id": vendor_id,
            "token": token
        })
        
        if not qr_token:
            return {
                "valid": False,
                "error": "QR code not found or expired"
            }
        
        # Check if already used
        if qr_token["used"]:
            return {
                "valid": False,
                "error": "QR code already used"
            }
        
        # Check expiry
        if datetime.utcnow() > qr_token["expires_at"]:
            return {
                "valid": False,
                "error": "QR code expired (60 seconds limit)"
            }
        
        # Check location (if provided)
        location_verified = True
        distance_km = 0
        
        if customer_location and qr_token.get("vendor_location"):
            # Calculate distance
            from geopy.distance import geodesic
            
            customer_coords = (
                customer_location.get("latitude"),
                customer_location.get("longitude")
            )
            vendor_coords = (
                qr_token["vendor_location"].get("latitude"),
                qr_token["vendor_location"].get("longitude")
            )
            
            distance_km = geodesic(customer_coords, vendor_coords).kilometers
            
            # Must be within 0.5km (500 meters)
            if distance_km > 0.5:
                return {
                    "valid": False,
                    "error": f"Too far from vendor ({distance_km:.2f}km). Must be within 500m."
                }
        
        # Check customer-vendor relationship
        relation = await db.customer_vendor_relations.find_one({
            "customer_id": customer_id,
            "vendor_id": vendor_id,
            "status": "active"
        })
        
        if not relation:
            return {
                "valid": False,
                "error": "No active credit line with this vendor"
            }
        
        # All validations passed
        return {
            "valid": True,
            "vendor_id": vendor_id,
            "vendor_name": relation["vendor_name"],
            "available_credit": relation["available_credit"],
            "qr_token": token,
            "location_verified": location_verified,
            "distance_km": distance_km,
            "message": "QR code validated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating QR: {str(e)}"
        )

@router.post("/mark-used")
async def mark_qr_used(token: str, customer_id: str):
    """Mark QR token as used after successful transaction"""
    try:
        result = await db.qr_tokens.update_one(
            {"token": token, "used": False},
            {
                "$set": {
                    "used": True,
                    "used_by": customer_id,
                    "used_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Token already used or not found"
            )
        
        return {
            "success": True,
            "message": "QR token marked as used"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error marking QR as used: {str(e)}"
        )