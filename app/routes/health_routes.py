"""Health check routes"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Paynaka API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Paynaka Backend Running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }