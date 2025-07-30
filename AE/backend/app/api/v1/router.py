from fastapi import APIRouter

from app.api.v1.endpoints import auth, instruments, market

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(
    instruments.router, prefix="/instruments", tags=["instruments"]
)
api_router.include_router(market.router, prefix="/market", tags=["market"])
