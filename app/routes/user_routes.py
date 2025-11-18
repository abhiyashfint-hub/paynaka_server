# app/routes/user_routes.py

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from datetime import datetime
from typing import Optional
from app.core.database import get_database

router = APIRouter(prefix="/users", tags=["Users"])


# Dependency to get DB
def db():
    return get_database()


# =========================================
#         CREATE / REGISTER USER
# =========================================
@router.post("/register")
async def register_user(data: dict, database=Depends(db)):
    """
    Register a new user (name, phone, profile info)
    """
    phone = data.get("phone")
    name = data.get("name")

    if not phone or not name:
        raise HTTPException(status_code=400, detail="Name & phone required")

    existing = await database["users"].find_one({"phone": phone})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user_data = {
        "name": name,
        "phone": phone,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "trust_score": 500,
    }

    result = await database["users"].insert_one(user_data)
    return {
        "success": True,
        "message": "User registered",
        "user_id": str(result.inserted_id),
    }


# =========================================
#            GET USER PROFILE
# =========================================
@router.get("/{phone}")
async def get_user(phone: str, database=Depends(db)):
    user = await database["users"].find_one({"phone": phone})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["_id"] = str(user["_id"])  # convert ObjectId

    return {
        "success": True,
        "user": user
    }


# =====================================================
#               TRUST SCORE CALCULATION
# =====================================================
async def calculate_trust_score(customer_id: str, vendor_id: str, database):
    """
    Internal function — not an API endpoint.
    Calculates trust score (300–1000)
    """

    relation = await database["customer_vendor_relations"].find_one({
        "customer_id": customer_id,
        "vendor_id": vendor_id
    })

    if not relation:
        return 500  # No history

    # Repayment: 40%
    total = relation.get("on_time_payments", 0) + relation.get("late_payments", 0)
    on_time_rate = relation.get("on_time_payments", 0) / total if total > 0 else 1
    repayment_score = on_time_rate * 40

    # Network reputation: 30%
    network_relations = await database["customer_vendor_relations"].count_documents({
        "customer_phone": relation.get("customer_phone"),
        "status": "active"
    })
    network_score = min(network_relations / 10, 1) * 30

    # Transaction velocity: 20%
    txn_count = relation.get("transaction_count", 0)
    velocity_score = min(txn_count / 50, 1) * 20

    # Account tenure: 10%
    age_days = (datetime.utcnow() - relation.get("created_at", datetime.utcnow())).days
    tenure_score = min(age_days / 365, 1) * 10

    raw = repayment_score + network_score + velocity_score + tenure_score
    final_score = int(300 + (raw / 100) * 700)

    # Penalties / bonuses
    if relation.get("on_time_payments", 0) >= 10 and relation.get("late_payments", 0) == 0:
        final_score += 100

    if relation.get("late_payments", 0) > 3:
        final_score -= 50

    if relation.get("default_count", 0) > 0:
        final_score -= 100 * relation.get("default_count", 0)

    final_score = max(300, min(1000, final_score))

    # Update DB
    await database["customer_vendor_relations"].update_one(
        {"_id": relation["_id"]},
        {
            "$set": {"trust_score": final_score, "updated_at": datetime.utcnow()},
            "$push": {
                "trust_score_history": {
                    "score": final_score,
                    "calculated_at": datetime.utcnow()
                }
            }
        }
    )

    return final_score


# =====================================================
#               LOCATION VERIFICATION
# =====================================================
def verify_location(customer_loc: dict, vendor_loc: dict):
    """
    Internal function to verify customer is within 500 meters.
    """

    try:
        from geopy.distance import geodesic

        c = (customer_loc["latitude"], customer_loc["longitude"])
        v = (vendor_loc["latitude"], vendor_loc["longitude"])

        distance_km = geodesic(c, v).kilometers

        return {
            "verified": distance_km <= 0.5,
            "distance_km": round(distance_km, 3)
        }

    except Exception as e:
        return {
            "verified": False,
            "distance_km": 0,
            "error": str(e)
        }
