"""
Paynaka FastAPI Application
Main application file that initializes FastAPI, CORS, routes, and database
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import database connection
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings

# Import routers
from app.routes import health_routes
from app.routes import customer_router
from app.routes import auth_router
from app.routes import vendor_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Paynaka Backend...")
    try:
        await connect_to_mongo()
        logger.info("✅ Application started successfully")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Paynaka Backend...")
    await close_mongo_connection()
    logger.info("✅ Application shut down successfully")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Paynaka - Where Trust Becomes Credit",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_routes.router, prefix="/api/v1")
app.include_router(customer_router.router, prefix="/api/v1")
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(vendor_router.router, prefix="/api/v1")

# Root endpoint (also in health_routes, but duplicated here for clarity)
@app.get("/")
async def root():
    """Root endpoint - confirms API is running"""
    return {
        "message": "Paynaka Backend Running",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
from app.routes import qr_routes  # Add this import

# Include QR router
app.include_router(qr_routes.router, prefix="/api/v1")