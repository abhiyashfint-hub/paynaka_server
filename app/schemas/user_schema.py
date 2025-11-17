from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ============ CUSTOMER SCHEMAS ============

class CustomerCheckRequest(BaseModel):
    """Check if customer exists for a vendor"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    vendor_id: str = Field(..., min_length=1)

class CustomerCheckResponse(BaseModel):
    """Response for customer existence check"""
    exists: bool
    message: str
    customer_id: Optional[str] = None
    vendor_id: str

class CustomerRegisterRequest(BaseModel):
    """Register new customer with vendor"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    name: str = Field(..., min_length=2, max_length=100)
    vendor_id: str = Field(..., min_length=1)
    otp: str = Field(..., min_length=4, max_length=6)

class CustomerRegisterResponse(BaseModel):
    """Response after customer registration"""
    success: bool
    message: str
    customer_id: str
    credit_limit: float
    available_credit: float

class CustomerDashboardRequest(BaseModel):
    """Request customer dashboard"""
    customer_id: str
    vendor_id: str

class CustomerDashboardResponse(BaseModel):
    """Customer dashboard data"""
    customer_id: str
    customer_name: str
    vendor_id: str
    vendor_name: str
    credit_limit: float
    used_credit: float
    available_credit: float
    transaction_count: int

class PayOnCreditRequest(BaseModel):
    """Pay on credit"""
    customer_id: str
    vendor_id: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class PayOnCreditResponse(BaseModel):
    """Response after payment"""
    success: bool
    message: str
    transaction_id: str
    new_balance: float
    amount_paid: float

# ============ OTP SCHEMAS ============

class OTPSendRequest(BaseModel):
    """Send OTP to phone"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')

class OTPSendResponse(BaseModel):
    """OTP send response"""
    success: bool
    message: str
    expires_in: int = 300  # 5 minutes

class OTPVerifyRequest(BaseModel):
    """Verify OTP"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    otp: str = Field(..., min_length=4, max_length=6)

class OTPVerifyResponse(BaseModel):
    """OTP verification response"""
    success: bool
    message: str
    verified: bool

# ============ VENDOR SCHEMAS ============

class VendorInfoResponse(BaseModel):
    """Vendor information"""
    vendor_id: str
    vendor_name: str
    category: str
    default_credit_limit: float
    status: str