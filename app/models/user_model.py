"""User Model (for vendors/admins)"""
from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime

class User(Document):
    """User document model for MongoDB"""
    
    phone_number: str = Field(..., description="User phone number")
    email: Optional[EmailStr] = Field(None, description="User email")
    name: str = Field(..., description="User full name")
    user_type: str = Field(..., description="User type: vendor, admin, customer")
    hashed_password: Optional[str] = Field(None, description="Hashed password")
    is_active: bool = Field(default=True, description="Is user active")
    is_verified: bool = Field(default=False, description="Is phone verified")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "users"
        indexes = [
            "phone_number",
            "email",
            "user_type"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+919876543210",
                "email": "vendor@example.com",
                "name": "Raj Store",
                "user_type": "vendor",
                "is_active": True,
                "is_verified": True
            }
        }