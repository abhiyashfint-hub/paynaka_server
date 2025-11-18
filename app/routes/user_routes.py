# ============ TRUST SCORE CALCULATION ============

async def calculate_trust_score(customer_id: str, vendor_id: str) -> int:
    """
    Calculate trust score based on:
    - Repayment history (40%)
    - Network reputation (30%)
    - Transaction velocity (20%)
    - Account tenure (10%)
    """
    try:
        relation = await db.customer_vendor_relations.find_one({
            "customer_id": customer_id,
            "vendor_id": vendor_id
        })
        
        if not relation:
            return 500  # Default score for new customers
        
        # Component 1: Repayment History (40%)
        total_payments = relation["on_time_payments"] + relation["late_payments"]
        if total_payments > 0:
            on_time_rate = relation["on_time_payments"] / total_payments
        else:
            on_time_rate = 1.0  # No history yet
        
        repayment_score = on_time_rate * 40
        
        # Component 2: Network Reputation (30%)
        # Count vendors who trust this customer
        all_relations = await db.customer_vendor_relations.count_documents({
            "customer_phone": relation["customer_phone"],
            "status": "active"
        })
        network_score = min(all_relations / 10, 1.0) * 30
        
        # Component 3: Transaction Velocity (20%)
        # Active customers get higher scores
        transaction_count = relation["transaction_count"]
        velocity_score = min(transaction_count / 50, 1.0) * 20
        
        # Component 4: Account Tenure (10%)
        # Older accounts get higher scores
        account_age_days = (datetime.utcnow() - relation["created_at"]).days
        tenure_score = min(account_age_days / 365, 1.0) * 10
        
        # Calculate raw score (0-100)
        raw_score = repayment_score + network_score + velocity_score + tenure_score
        
        # Convert to 300-1000 scale
        final_score = int(300 + (raw_score / 100) * 700)
        
        # Apply bonuses/penalties
        if relation["on_time_payments"] >= 10 and relation["late_payments"] == 0:
            final_score += 100  # Perfect payment record bonus
        
        if relation["late_payments"] > 3:
            final_score -= 50  # Multiple late payments penalty
        
        if relation["default_count"] > 0:
            final_score -= 100 * relation["default_count"]  # Default penalty
        
        # Clamp between 300-1000
        final_score = max(300, min(1000, final_score))
        
        # Update in database
        await db.customer_vendor_relations.update_one(
            {"_id": relation["_id"]},
            {
                "$set": {
                    "trust_score": final_score,
                    "updated_at": datetime.utcnow()
                },
                "$push": {
                    "trust_score_history": {
                        "score": final_score,
                        "calculated_at": datetime.utcnow()
                    }
                }
            }
        )
        
        return final_score
        
    except Exception as e:
        print(f"Error calculating trust score: {e}")
        return 500  # Default on error

# ============ LOCATION VERIFICATION ============

def verify_location(customer_location: dict, vendor_location: dict) -> dict:
    """Verify customer is within 500m of vendor"""
    try:
        from geopy.distance import geodesic
        
        customer_coords = (
            customer_location.get("latitude"),
            customer_location.get("longitude")
        )
        vendor_coords = (
            vendor_location.get("latitude"),
            vendor_location.get("longitude")
        )
        
        distance_km = geodesic(customer_coords, vendor_coords).kilometers
        
        return {
            "verified": distance_km <= 0.5,  # 500 meters
            "distance_km": round(distance_km, 3),
            "message": "Location verified" if distance_km <= 0.5 else "Too far from vendor"
        }
    except Exception as e:
        return {
            "verified": False,
            "distance_km": 0,
            "message": f"Location verification failed: {str(e)}"
        }