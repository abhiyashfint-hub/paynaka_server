from fastapi import FastAPI
from app.routes.health_routes import router as health_router
from app.routes.user_routes import router as user_router
from app.routes.vendor_routes import router as vendor_router
from app.routes.transaction_routes import router as transaction_router

app = FastAPI(title="Paynaka API Server")

# Register routes
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(vendor_router, prefix="/vendors", tags=["Vendors"])
app.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])

@app.get("/")
def root():
    return {"message": "Paynaka API is live!"}
