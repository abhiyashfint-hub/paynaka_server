from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory temporary database
CUSTOMERS = {}  # phone → customer data
ID_COUNTER = 1


# --------------------------
# SCHEMAS
# --------------------------
class CheckRequest(BaseModel):
    phone: str
    vendor_id: str


class RegisterRequest(BaseModel):
    name: str
    phone: str
    vendor_id: str


# --------------------------
# CHECK CUSTOMER
# --------------------------
@router.post("/customer/check")
async def check_customer(payload: CheckRequest):
    phone = payload.phone

    if phone in CUSTOMERS:
        return {
            "exists": True,
            "customer_id": CUSTOMERS[phone]["customer_id"]
        }

    return {"exists": False}


# --------------------------
# REGISTER CUSTOMER
# --------------------------
@router.post("/customer/register")
async def register_customer(payload: RegisterRequest):
    global ID_COUNTER

    new_id = f"CUST-{ID_COUNTER}"
    ID_COUNTER += 1

    CUSTOMERS[payload.phone] = {
        "customer_id": new_id,
        "name": payload.name,
        "vendor_id": payload.vendor_id,
        "credit_limit": 2000,
        "balance_remaining": 2000,
        "outstanding": 0
    }

    return {"success": True, "customer_id": new_id}


# --------------------------
# DASHBOARD
# --------------------------
@router.get("/customer/dashboard")
async def customer_dashboard(customer_id: str, vendor_id: str):
    for data in CUSTOMERS.values():
        if data["customer_id"] == customer_id:
            return {
                "name": data["name"],
                "credit_limit": data["credit_limit"],
                "balance_remaining": data["balance_remaining"],
                "outstanding": data["outstanding"]
            }

    return {"error": "Customer not found"}
