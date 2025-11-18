"""Customer Model"""
from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime

class Customer(Document):
    """Customer document model for MongoDB"""
    
    phone_number: str = Field(..., description="Customer phone number")
    name: Optional[str] = Field(None, description="Customer full name")
    email: Optional[EmailStr] = Field(None, description="Customer email")
    trust_score: int = Field(default=500, ge=300, le=900, description="Credit trust score")
    credit_limit: float = Field(default=5000.0, ge=0, description="Total credit limit")
    available_credit: float = Field(default=5000.0, ge=0, description="Available credit")
    kyc_status: str = Field(default="pending", description="KYC verification status")
    status: str = Field(default="active", description="Account status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "customers"
        indexes = [
            "phone_number",
            "email",
            "status"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+919876543210",
                "name": "Rajesh Kumar",
                "email": "rajesh@example.com",
                "trust_score": 750,
                "credit_limit": 5000.0,
                "available_credit": 3000.0,
                "kyc_status": "verified",
                "status": "active"
            }
        }