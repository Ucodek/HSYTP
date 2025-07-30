"""Main API router for version 1 of the API."""
from typing import Optional

from fastapi import APIRouter, Header, status
from fastapi.responses import JSONResponse

from app.api.dependencies import CurrentActiveUser
from app.modules.auth.api import router as auth_router
from app.modules.instruments.api import router as instruments_router
from app.utils.i18n import get_language, get_translation
from app.utils.response import create_success_response

# Create main router
api_router = APIRouter()

# Include module routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(
    instruments_router, prefix="/instruments", tags=["instruments"]
)

# Placeholder for future module routers
# api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
# api_router.include_router(market_router, prefix="/market", tags=["market"])


# Add root endpoint for API information and healthcheck
@api_router.get("/", summary="API Information")
async def api_info(
    accept_language: Optional[str] = Header(None, description="Preferred language")
):
    """
    Get basic API information.

    Returns information about the API including version and documentation links.
    The response is localized based on the Accept-Language header.
    """
    language = get_language(accept_language)
    return create_success_response(
        {
            "name": get_translation("api.name", language),
            "version": "1.0.0",
            "description": get_translation("api.description", language),
            "docs_url": "/api/docs",
        }
    )


# Add current user endpoint
@api_router.get("/me", summary="Current User Information")
async def current_user_info(
    current_user: CurrentActiveUser,
    accept_language: Optional[str] = Header(None, description="Preferred language"),
):
    """
    Get information about the current authenticated user.

    This endpoint returns information about the currently authenticated user.
    The response is localized based on the Accept-Language header.

    Requires authentication.
    """
    language = get_language(accept_language)
    return create_success_response(
        current_user.safe_dict(), message=get_translation("api.current_user", language)
    )


# Health check specific to the API
@api_router.get("/health", summary="API Health Check")
async def api_health():
    """
    Simple health check for the API.

    Used for monitoring and load balancer health checks.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "service": "api"},
    )
