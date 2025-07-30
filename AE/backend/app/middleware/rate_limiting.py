import logging
import time

import redis.asyncio as redis
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimitService:
    """Service for handling rate limiting operations."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def increment_and_check(self, key: str, limit: int) -> tuple:
        """Increment counter and check if limit exceeded."""
        try:
            current_count = await self.redis.incr(key)
            if current_count == 1:
                await self.redis.expire(key, 60)
            return current_count, max(0, limit - current_count)
        except Exception as e:
            # Log error but don't fail
            logging.error(f"Redis error in rate limiting: {str(e)}")
            return 1, limit - 1  # Assume first request if Redis fails


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        if redis_client:
            self.redis = redis_client
        else:
            # Check for Redis URL first
            if settings.REDIS_URL:
                self.redis = redis.Redis.from_url(
                    settings.REDIS_URL, decode_responses=True
                )
            else:
                self.redis = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True,
                )
        self.rate_limit_service = RateLimitService(self.redis)

    def _get_user_tier(self, request: Request) -> tuple:
        """Extract user ID and tier from request."""
        user_id = None
        tier = "basic"  # Default to basic tier

        # Try to extract user from token
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            # In a real implementation, you'd extract user_id and tier from token
            # For now, we'll just use a placeholder
            user_id = "anonymous"  # This would come from decoding the JWT token

        return user_id, tier

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for non-API requests
        if not request.url.path.startswith(settings.API_V1_STR):
            return await call_next(request)

        try:
            # Get user info using the helper function
            user_id, tier = self._get_user_tier(request)

            # Choose the appropriate rate limit based on tier
            limit = (
                settings.RATE_LIMIT_PREMIUM
                if tier == "premium"
                else settings.RATE_LIMIT_BASIC
            )

            # Create a rate limit key
            window = int(time.time() / 60)  # 1-minute window
            key = f"rate_limit:{user_id or 'anonymous'}:{request.url.path}:{window}"

            # Get current rate limit for this window
            (
                current_count,
                remaining,
            ) = await self.rate_limit_service.increment_and_check(key, limit)

            # Check if rate limit is exceeded
            if current_count > limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": (
                                "You have exceeded your rate limit. "
                                "Please try again later."
                            ),
                        },
                    },
                )

            # Process the request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-Rate-Limit-Limit"] = str(limit)
            response.headers["X-Rate-Limit-Remaining"] = str(remaining)
            response.headers["X-Rate-Limit-Reset"] = str((window + 1) * 60)

            return response

        except Exception as e:
            # Catch-all to ensure middleware never fails the application
            logging.exception(f"Error in rate limit middleware: {str(e)}")
            return await call_next(request)
