from datetime import datetime
from typing import Optional

class CustomerVendorRelation:
    """Customer-Vendor credit relationship with trust score"""
    
    @staticmethod
    def make_relation_doc(data: dict) -> dict:
        return {
            "customer_id": data["customer_id"],
            "customer_phone": data["customer_phone"],
            "customer_name": data["customer_name"],
            "vendor_id": data["vendor_id"],
            "vendor_name": data.get("vendor_name", "Vendor Store"),
            
            # Credit Info
            "credit_limit": data.get("credit_limit", 500.0),
            "used_credit": 0.0,
            "available_credit": data.get("credit_limit", 500.0),
            
            # Trust Score (starts at 500)
            "trust_score": 500,
            "trust_score_history": [],
            
            # Activity
            "transaction_count": 0,
            "total_spent": 0.0,
            "total_repaid": 0.0,
            "on_time_payments": 0,
            "late_payments": 0,
            "default_count": 0,
            
            # Status
            "status": "active",  # active, suspended, blocked
            "auto_approved": True,
            "kyc_verified": False,
            
            # Dates
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_transaction_at": None,
            "last_payment_at": None,
        }

class Transaction:
    """Transaction with location verification"""
    
    @staticmethod
    def make_transaction_doc(data: dict) -> dict:
        return {
            "transaction_id": data.get("transaction_id"),
            "customer_id": data["customer_id"],
            "vendor_id": data["vendor_id"],
            "amount": data["amount"],
            "transaction_type": data.get("transaction_type", "credit_purchase"),
            "description": data.get("description", "Purchase on credit"),
            
            # Payment Info
            "payment_status": "pending",  # pending, paid, overdue
            "due_date": data.get("due_date"),
            "paid_date": None,
            "payment_method": None,
            
            # Location Info
            "customer_location": data.get("customer_location"),
            "vendor_location": data.get("vendor_location"),
            "distance_km": data.get("distance_km", 0),
            "location_verified": data.get("location_verified", False),
            
            # QR Info
            "qr_token": data.get("qr_token"),
            "scan_method": data.get("scan_method", "qr"),  # qr or manual
            
            # Metadata
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

class QRToken:
    """Dynamic QR Token that refreshes every 60 seconds"""
    
    @staticmethod
    def make_qr_token_doc(vendor_id: str) -> dict:
        import secrets
        token = secrets.token_urlsafe(32)
        
        return {
            "vendor_id": vendor_id,
            "token": token,
            "qr_data": f"paynaka://scan/{vendor_id}/{token}",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=60),
            "used": False,
            "used_by": None,
            "used_at": None,
        }