from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class OTPRequest(BaseModel):
    phone: str

@router.post("/send-otp")
async def send_otp(data: OTPRequest):
    return {
        "success": True,
        "otp_sent": True,
        "mock_otp": "123456"
    }

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str

@router.post("/verify-otp")
async def verify_otp(data: VerifyOTPRequest):
    if data.otp == "123456":
        return {"success": True, "verified": True}
    return {"success": False, "error": "Invalid OTP"}
