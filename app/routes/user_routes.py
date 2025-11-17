from fastapi import APIRouter, HTTPException, status
from app.schemas.user_schema import (
    CustomerCheckRequest,
    CustomerCheckResponse,
    CustomerRegisterRequest,
    CustomerRegisterResponse,
    CustomerDashboardRequest,
    CustomerDashboardResponse,
    PayOnCreditRequest,
    PayOnCreditResponse,
    OTPSendRequest,
    OTPSendResponse,
    OTPVerifyRequest,
    OTPVerifyResponse,
    VendorInfoResponse
)
from app.core.database import db
from bson import ObjectId
from datetime import datetime
import random

router = APIRouter()

# In-memory OTP storage (use Redis in production)
otp_storage = {}

# Fixed vendor for testing (V001)
VENDOR_V001 = {
    "vendor_id": "V001",
    "vendor_name": "Raj General Store",
    "category": "Grocery",
    "default_credit_limit": 500.0,
    "status": "active"
}

# ============ QR SCAN ENDPOINT ============

@router.get("/scan/{vendor_id}")
async def scan_vendor_qr(vendor_id: str):
    """
    Customer scans QR code
    Returns vendor info
    """
    # For now, only V001 is supported
    if vendor_id != "V001":
        raise HTTPException(
            status_code=404,
            detail="Vendor not found"
        )
    
    return VendorInfoResponse(**VENDOR_V001)

# ============ CUSTOMER CHECK ============

@router.post("/check", response_model=CustomerCheckResponse)
async def check_customer(request: CustomerCheckRequest):
    """
    Check if customer already exists with this vendor
    """
    try:
        # Check in customer_vendor_relations collection
        relation = await db.customer_vendor_relations.find_one({
            "customer_phone": request.phone_number,
            "vendor_id": request.vendor_id
        })
        
        if relation:
            return CustomerCheckResponse(
                exists=True,
                message="Customer exists",
                customer_id=str(relation["customer_id"]),
                vendor_id=request.vendor_id
            )
        else:
            return CustomerCheckResponse(
                exists=False,
                message="New customer",
                customer_id=None,
                vendor_id=request.vendor_id
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking customer: {str(e)}"
        )

# ============ OTP ENDPOINTS ============

@router.post("/send-otp", response_model=OTPSendResponse)
async def send_otp(request: OTPSendRequest):
    """
    Send OTP to customer phone
    """
    try:
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Store OTP with expiration
        otp_storage[request.phone_number] = {
            "otp": otp,
            "created_at": datetime.utcnow()
        }
        
        # TODO: Send via SMS provider (Twilio, MSG91, etc.)
        # For testing, print to console
        print(f"📱 OTP for {request.phone_number}: {otp}")
        
        return OTPSendResponse(
            success=True,
            message="OTP sent successfully",
            expires_in=300
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending OTP: {str(e)}"
        )

@router.post("/verify-otp", response_model=OTPVerifyResponse)
async def verify_otp(request: OTPVerifyRequest):
    """
    Verify OTP entered by customer
    """
    try:
        stored_otp_data = otp_storage.get(request.phone_number)
        
        if not stored_otp_data:
            return OTPVerifyResponse(
                success=False,
                message="OTP expired or not found",
                verified=False
            )
        
        if stored_otp_data["otp"] != request.otp:
            return OTPVerifyResponse(
                success=False,
                message="Invalid OTP",
                verified=False
            )
        
        # OTP is valid
        return OTPVerifyResponse(
            success=True,
            message="OTP verified successfully",
            verified=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying OTP: {str(e)}"
        )

# ============ CUSTOMER REGISTRATION ============

@router.post("/register", response_model=CustomerRegisterResponse)
async def register_customer(request: CustomerRegisterRequest):
    """
    Register new customer with vendor
    Auto-approve ₹500 credit for V001
    """
    try:
        # Verify OTP first
        stored_otp_data = otp_storage.get(request.phone_number)
        
        if not stored_otp_data or stored_otp_data["otp"] != request.otp:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired OTP"
            )
        
        # Remove OTP after successful verification
        del otp_storage[request.phone_number]
        
        # Check if customer already exists
        existing = await db.customer_vendor_relations.find_one({
            "customer_phone": request.phone_number,
            "vendor_id": request.vendor_id
        })
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Customer already registered with this vendor"
            )
        
        # Generate unique customer ID
        customer_id = f"CUST_{int(datetime.utcnow().timestamp())}"
        
        # Create customer-vendor relation
        relation_doc = {
            "customer_id": customer_id,
            "customer_phone": request.phone_number,
            "customer_name": request.name,
            "vendor_id": request.vendor_id,
            "vendor_name": VENDOR_V001["vendor_name"],
            "credit_limit": 500.0,  # Auto-approve ₹500
            "used_credit": 0.0,
            "available_credit": 500.0,
            "transaction_count": 0,
            "status": "active",
            "auto_approved": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        await db.customer_vendor_relations.insert_one(relation_doc)
        
        return CustomerRegisterResponse(
            success=True,
            message="Customer registered successfully with ₹500 credit",
            customer_id=customer_id,
            credit_limit=500.0,
            available_credit=500.0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error registering customer: {str(e)}"
        )

# ============ CUSTOMER DASHBOARD ============

@router.post("/dashboard", response_model=CustomerDashboardResponse)
async def get_customer_dashboard(request: CustomerDashboardRequest):
    """
    Get customer dashboard with credit info
    """
    try:
        # Get customer-vendor relation
        relation = await db.customer_vendor_relations.find_one({
            "customer_id": request.customer_id,
            "vendor_id": request.vendor_id
        })
        
        if not relation:
            raise HTTPException(
                status_code=404,
                detail="Customer relationship not found"
            )
        
        return CustomerDashboardResponse(
            customer_id=relation["customer_id"],
            customer_name=relation["customer_name"],
            vendor_id=relation["vendor_id"],
            vendor_name=relation["vendor_name"],
            credit_limit=relation["credit_limit"],
            used_credit=relation["used_credit"],
            available_credit=relation["available_credit"],
            transaction_count=relation["transaction_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching dashboard: {str(e)}"
        )

# ============ PAY ON CREDIT ============

@router.post("/pay-credit", response_model=PayOnCreditResponse)
async def pay_on_credit(request: PayOnCreditRequest):
    """
    Customer pays on credit
    """
    try:
        # Get customer-vendor relation
        relation = await db.customer_vendor_relations.find_one({
            "customer_id": request.customer_id,
            "vendor_id": request.vendor_id
        })
        
        if not relation:
            raise HTTPException(
                status_code=404,
                detail="Customer relationship not found"
            )
        
        # Check available credit
        if request.amount > relation["available_credit"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient credit. Available: ₹{relation['available_credit']}"
            )
        
        # Create transaction
        transaction_doc = {
            "customer_id": request.customer_id,
            "vendor_id": request.vendor_id,
            "amount": request.amount,
            "transaction_type": "credit_purchase",
            "description": request.description or "Purchase on credit",
            "status": "completed",
            "created_at": datetime.utcnow(),
        }
        
        result = await db.transactions.insert_one(transaction_doc)
        transaction_id = str(result.inserted_id)
        
        # Update customer-vendor relation
        new_used_credit = relation["used_credit"] + request.amount
        new_available_credit = relation["available_credit"] - request.amount
        
        await db.customer_vendor_relations.update_one(
            {"_id": relation["_id"]},
            {
                "$set": {
                    "used_credit": new_used_credit,
                    "available_credit": new_available_credit,
                    "transaction_count": relation["transaction_count"] + 1,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return PayOnCreditResponse(
            success=True,
            message="Payment successful",
            transaction_id=transaction_id,
            new_balance=new_available_credit,
            amount_paid=request.amount
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing payment: {str(e)}"
        )

# Keep old ping for testing
@router.get("/ping")
async def user_ping():
    return {"message": "User route working"}