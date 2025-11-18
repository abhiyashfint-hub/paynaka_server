"""Authentication routes"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.user_schema import (
    OTPSendRequest,
    OTPSendResponse,
    OTPVerifyRequest,
    OTPVerifyResponse
)
from app.models.customer_model import Customer
from app.core.auth import create_access_token
from datetime import timedelta
import random

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory OTP storage (use Redis in production)
otp_storage = {}

@router.post("/send-otp", response_model=OTPSendResponse)
async def send_otp(request: OTPSendRequest):
    """Send OTP to phone number"""
    try:
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Store OTP (in production, use Redis with expiration)
        otp_storage[request.phone_number] = otp
        
        # TODO: Integrate with SMS provider (Twilio, MSG91, etc.)
        # For now, just log it (remove in production)
        print(f"📱 OTP for {request.phone_number}: {otp}")
        
        return OTPSendResponse(
            success=True,
            message="OTP sent successfully",
            otp_sent=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending OTP: {str(e)}"
        )

@router.post("/verify-otp", response_model=OTPVerifyResponse)
async def verify_otp(request: OTPVerifyRequest):
    """Verify OTP and return access token"""
    try:
        # Get stored OTP
        stored_otp = otp_storage.get(request.phone_number)
        
        if not stored_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP not found or expired"
            )
        
        # Verify OTP
        if stored_otp != request.otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )
        
        # Remove OTP after successful verification
        del otp_storage[request.phone_number]
        
        # Find or create customer
        customer = await Customer.find_one(
            Customer.phone_number == request.phone_number
        )
        
        if not customer:
            # Auto-register customer
            customer = Customer(
                phone_number=request.phone_number,
                trust_score=500,
                credit_limit=5000.0,
                available_credit=5000.0,
                status="active"
            )
            await customer.insert()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(customer.id), "phone": customer.phone_number},
            expires_delta=timedelta(days=30)
        )
        
        return OTPVerifyResponse(
            success=True,
            message="OTP verified successfully",
            access_token=access_token,
            customer_id=str(customer.id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying OTP: {str(e)}"
        )