import logging
import time
from typing import Any, Callable, Dict, Optional, Tuple, Union

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.cache.redis_cache import RedisCache, get_redis_cache
from app.core.config.base import settings
from app.errors.error_codes import ErrorCode
from app.errors.exceptions import RateLimitError
from app.modules.auth.models import UserRole

logger = logging.getLogger(__name__)

# Default rate limits: [requests, period_in_seconds]
DEFAULT_RATE_LIMITS = {
    # For unauthenticated users (by IP address)
    "DEFAULT": (settings.RATE_LIMIT_DEFAULT, 60),  # Default requests per minute
    # Rate limits for different user roles
    UserRole.USER.value: (
        settings.RATE_LIMIT_USER,
        60,
    ),  # User role requests per minute
    UserRole.ADMIN.value: (
        settings.RATE_LIMIT_ADMIN,
        60,
    ),  # Admin role requests per minute
    # Per-endpoint rate limits (overrides)
    "AUTH": (20, 60),  # 20 auth requests per minute
    "SENSITIVE": (10, 60),  # 10 requests per minute for sensitive endpoints
}


class MemoryRateLimiter:
    """In-memory rate limiter for development and testing."""

    def __init__(self):
        self.requests: Dict[str, Dict[str, Union[int, float]]] = {}

    def increment(self, key: str, ttl: int) -> Tuple[int, int]:
        """Increment request count for a key."""
        current_time = time.time()

        # Initialize or get data
        if key not in self.requests:
            self.requests[key] = {"count": 0, "reset_at": current_time + ttl}

        # Clear expired counters
        if self.requests[key]["reset_at"] <= current_time:
            self.requests[key] = {"count": 0, "reset_at": current_time + ttl}

        # Increment counter
        self.requests[key]["count"] += 1

        # Calculate time remaining until reset
        remaining = max(0, int(self.requests[key]["reset_at"] - current_time))

        return self.requests[key]["count"], remaining


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(
        self,
        app: ASGIApp,
        redis_cache: Any = None,
        rate_limits: Optional[Dict[str, Tuple[int, int]]] = None,
        exclude_paths: Optional[list[str]] = None,
    ):
        """Initialize the rate limiting middleware."""
        super().__init__(app)
        self.redis = redis_cache
        self.rate_limits = rate_limits or DEFAULT_RATE_LIMITS
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/redoc"]
        self.memory_limiter = MemoryRateLimiter()

    def get_rate_limit_key(self, request: Request) -> Tuple[str, str, Tuple[int, int]]:
        """
        Get the rate limit key, category, and limits for the request.

        Returns:
            Tuple of (rate_limit_key, category, (max_requests, period_seconds))
        """
        # Determine category
        path = request.url.path
        category = "DEFAULT"

        # Check auth endpoints
        if "/auth/" in path:
            category = "AUTH"

        # Get user information if available
        user_id = None
        user_role = None

        if hasattr(request.state, "user"):
            user = getattr(request.state, "user")
            if user:
                user_id = getattr(user, "id", None)
                user_role = getattr(user, "role", None)
                if user_role:
                    # Use the user's role as the category if it's available
                    category = (
                        user_role.value if hasattr(user_role, "value") else user_role
                    )

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Create rate limit key based on category and identifier
        key_identifier = str(user_id) if user_id else client_ip
        rate_limit_key = f"ratelimit:{category}:{key_identifier}"

        # Get rate limit for category
        rate_limit = self.rate_limits.get(category, self.rate_limits["DEFAULT"])

        return rate_limit_key, category, rate_limit

    def check_rate_limit(
        self, key: str, max_requests: int, period_seconds: int
    ) -> Tuple[bool, int, int]:
        """
        Check if a request exceeds the rate limit.

        Args:
            key: Rate limit key
            max_requests: Maximum number of requests allowed
            period_seconds: Time period in seconds

        Returns:
            Tuple of (is_allowed, current_count, reset_seconds)
        """
        if self.redis:
            try:
                # Use Redis for distributed rate limiting - non-async version
                current = self.redis.client.incr(key)
                ttl = self.redis.client.ttl(key)

                # Set expiry if this is the first request
                if ttl < 0:
                    self.redis.client.expire(key, period_seconds)
                    ttl = period_seconds

                return current <= max_requests, current, ttl
            except Exception as e:
                logger.error(f"Redis rate limiting error: {str(e)}")
                # Fall back to memory rate limiting if Redis fails
                count, ttl = self.memory_limiter.increment(key, period_seconds)
                return count <= max_requests, count, ttl
        else:
            # Use in-memory rate limiting for development/testing
            count, ttl = self.memory_limiter.increment(key, period_seconds)
            return count <= max_requests, count, ttl

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process a request and apply rate limiting."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        try:
            # Get rate limit key and limits
            (
                rate_limit_key,
                category,
                (max_requests, period_seconds),
            ) = self.get_rate_limit_key(request)

            # Check rate limit
            is_allowed, current_count, reset_seconds = self.check_rate_limit(
                rate_limit_key, max_requests, period_seconds
            )

            # If rate limit exceeded, return 429 response
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded",
                    extra={
                        "client_ip": request.client.host
                        if request.client
                        else "unknown",
                        "path": request.url.path,
                        "category": category,
                        "current_count": current_count,
                        "limit": max_requests,
                    },
                )

                # Create rate limit error response
                error = RateLimitError(
                    detail=f"Rate limit exceeded. Try again in {reset_seconds} seconds.",
                    error_code=ErrorCode.RATE_TOO_MANY_REQUESTS,
                )

                # Convert to Response with correct status code and headers
                from fastapi.responses import JSONResponse

                response = JSONResponse(
                    status_code=error.status_code,
                    content={
                        "error": {"code": error.error_code, "message": error.detail}
                    },
                )

                # Add rate limit headers
                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(reset_seconds)

                return response

            # Process the request normally
            response = await call_next(request)

            # Add rate limit headers to successful response
            response.headers["X-RateLimit-Limit"] = str(max_requests)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, max_requests - current_count)
            )
            response.headers["X-RateLimit-Reset"] = str(reset_seconds)

            return response

        except Exception as e:
            # Catch-all to ensure middleware never fails the application
            logger.error(f"Error in rate limit middleware: {str(e)}")
            return await call_next(request)


def add_rate_limiting_middleware(
    app: ASGIApp, redis_cache: Optional[RedisCache] = None
) -> None:
    """Add rate limiting middleware to the application."""
    app.add_middleware(
        RateLimitingMiddleware,
        redis_cache=redis_cache or get_redis_cache(),
    )
