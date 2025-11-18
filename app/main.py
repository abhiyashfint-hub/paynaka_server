"""
Paynaka FastAPI Application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers (correct imports)
from app.routes.health_routes import router as health_routes
from app.routes.customer_router import router as customer_router
from app.routes.auth_router import router as auth_router
from app.routes.vendor_routes import router as vendor_router
from app.routes.user_routes import router as user_router
from app.routes.qr_routes import router as qr_routes

# DB + Settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings


# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# -------------------------------
# Lifespan Events
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Paynaka Backend...")
    try:
        await connect_to_mongo()
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    logger.info("🛑 Shutting down Paynaka Backend...")
    await close_mongo_connection()
    logger.info("✅ MongoDB connection closed")


# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Paynaka - Where Trust Becomes Credit",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# Routers
# -------------------------------
app.include_router(health_routes, prefix="/api/v1")
app.include_router(customer_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(vendor_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(qr_routes, prefix="/api/v1")      # QR routes


# -------------------------------
# Default Root Route
# -------------------------------
@app.get("/")
async def root():
    return {
        "message": "Paynaka Backend Running",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs"
    }


# -------------------------------
# Development Entry
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
