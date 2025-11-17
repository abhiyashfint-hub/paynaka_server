from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health_routes import router as health_router
from app.routes.user_routes import router as user_router
from app.routes.vendor_routes import router as vendor_router
from app.routes.transaction_routes import router as transaction_router

app = FastAPI(
    title="Paynaka Backend API",
    version="1.0.0",
    description="Backend for Paynaka - Where Trust Becomes Credit"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(vendor_router, prefix="/vendors", tags=["Vendors"])
app.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])

@app.get("/")
def root():
    return {
        "message": "Paynaka Backend Running",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }
