"""Vendor Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VendorBase(BaseModel):
    """Base vendor schema"""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    location: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = None
    gst_number: Optional[str] = None

class VendorCreate(VendorBase):
    """Schema for creating a vendor"""
    pass

class VendorResponse(VendorBase):
    """Schema for vendor response"""
    id: str
    created_at: datetime
    status: str = "active"
    
    class Config:
        from_attributes = True