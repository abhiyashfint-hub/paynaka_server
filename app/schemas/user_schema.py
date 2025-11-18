"""User Schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    """Schema for creating a user"""
    user_type: str = Field(..., pattern=r'^(vendor|admin|customer)$')
    password: Optional[str] = Field(None, min_length=6)

class UserResponse(UserBase):
    """Schema for user response"""
    id: str
    user_type: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomerCheckRequest(BaseModel):
    """Schema for checking if customer exists"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')

class CustomerCheckResponse(BaseModel):
    """Response for customer check"""
    exists: bool
    message: str
    customer_id: Optional[str] = None

class CustomerRegisterRequest(BaseModel):
    """Schema for customer registration"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None

class CustomerRegisterResponse(BaseModel):
    """Response for customer registration"""
    success: bool
    message: str
    customer_id: str
    trust_score: int
    credit_limit: float

class CustomerDashboardResponse(BaseModel):
    """Response for customer dashboard"""
    customer_id: str
    name: Optional[str]
    phone_number: str
    trust_score: int
    credit_limit: float
    available_credit: float
    kyc_status: str
    status: str

class OTPSendRequest(BaseModel):
    """Schema for sending OTP"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')

class OTPSendResponse(BaseModel):
    """Response for OTP send"""
    success: bool
    message: str
    otp_sent: bool

class OTPVerifyRequest(BaseModel):
    """Schema for verifying OTP"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    otp: str = Field(..., min_length=4, max_length=6)

class OTPVerifyResponse(BaseModel):
    """Response for OTP verification"""
    success: bool
    message: str
    access_token: Optional[str] = None
    customer_id: Optional[str] = None