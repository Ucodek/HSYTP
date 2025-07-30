"""
Main API router for version 1 of the API.

This module defines the main FastAPI router for API version 1, including sub-routers
for different modules (authentication, etc.) and provides a root endpoint with API information.
"""
from fastapi import APIRouter, Depends
from fastcore.config import get_settings

from app.modules.auth.api import router as auth_router
from app.modules.instruments.api import router as instruments_router

# Create main router
api_router = APIRouter()

# Include module routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(
    instruments_router, prefix="/instruments", tags=["instruments"]
)


# Add root endpoint for API information
@api_router.get("/", summary="API Information")
async def api_info(settings=Depends(get_settings)):
    """
    Get basic API information.

    Returns information about the API including name, version, and links to
    health checks, metrics, and documentation.

    Args:
        settings: Application configuration settings dependency.

    Returns:
        dict: Dictionary containing API information fields.
    """

    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "health_path": settings.HEALTH_PATH,
        "metrics_path": settings.METRICS_PATH,
        "docs_path": "/api/docs",
    }
