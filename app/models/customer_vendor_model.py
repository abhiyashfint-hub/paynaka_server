from datetime import datetime
from typing import Optional

class CustomerVendorRelation:
    """Model for customer-vendor credit relationship"""
    
    @staticmethod
    def make_relation_doc(data: dict) -> dict:
        """Create customer-vendor relation document"""
        return {
            "customer_id": data["customer_id"],
            "customer_phone": data["customer_phone"],
            "customer_name": data["customer_name"],
            "vendor_id": data["vendor_id"],
            "vendor_name": data.get("vendor_name", "Vendor Store"),
            "credit_limit": data.get("credit_limit", 500.0),
            "used_credit": 0.0,
            "available_credit": data.get("credit_limit", 500.0),
            "transaction_count": 0,
            "status": "active",
            "auto_approved": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

class Transaction:
    """Model for transactions"""
    
    @staticmethod
    def make_transaction_doc(data: dict) -> dict:
        """Create transaction document"""
        return {
            "customer_id": data["customer_id"],
            "vendor_id": data["vendor_id"],
            "amount": data["amount"],
            "transaction_type": "credit_purchase",
            "description": data.get("description", "Purchase on credit"),
            "status": "completed",
            "created_at": datetime.utcnow(),
        }