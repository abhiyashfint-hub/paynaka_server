"""Customer routes"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.user_schema import (
    CustomerCheckRequest,
    CustomerCheckResponse,
    CustomerRegisterRequest,
    CustomerRegisterResponse,
    CustomerDashboardResponse
)
from app.models.customer_model import Customer
from datetime import datetime

router = APIRouter(prefix="/customer", tags=["Customer"])

@router.post("/check", response_model=CustomerCheckResponse)
async def check_customer(request: CustomerCheckRequest):
    """Check if customer exists by phone number"""
    try:
        customer = await Customer.find_one(Customer.phone_number == request.phone_number)
        
        if customer:
            return CustomerCheckResponse(
                exists=True,
                message="Customer found",
                customer_id=str(customer.id)
            )
        else:
            return CustomerCheckResponse(
                exists=False,
                message="Customer not found",
                customer_id=None
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking customer: {str(e)}"
        )

@router.post("/register", response_model=CustomerRegisterResponse)
async def register_customer(request: CustomerRegisterRequest):
    """Register a new customer"""
    try:
        # Check if customer already exists
        existing_customer = await Customer.find_one(
            Customer.phone_number == request.phone_number
        )
        
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this phone number already exists"
            )
        
        # Create new customer
        new_customer = Customer(
            phone_number=request.phone_number,
            name=request.name,
            email=request.email,
            trust_score=500,
            credit_limit=5000.0,
            available_credit=5000.0,
            kyc_status="pending",
            status="active",
            created_at=datetime.utcnow()
        )
        
        await new_customer.insert()
        
        return CustomerRegisterResponse(
            success=True,
            message="Customer registered successfully",
            customer_id=str(new_customer.id),
            trust_score=new_customer.trust_score,
            credit_limit=new_customer.credit_limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering customer: {str(e)}"
        )

@router.get("/dashboard/{customer_id}", response_model=CustomerDashboardResponse)
async def get_customer_dashboard(customer_id: str):
    """Get customer dashboard data"""
    try:
        customer = await Customer.get(customer_id)
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return CustomerDashboardResponse(
            customer_id=str(customer.id),
            name=customer.name,
            phone_number=customer.phone_number,
            trust_score=customer.trust_score,
            credit_limit=customer.credit_limit,
            available_credit=customer.available_credit,
            kyc_status=customer.kyc_status,
            status=customer.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard: {str(e)}"
        )