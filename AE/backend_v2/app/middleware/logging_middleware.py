import logging
import time
import uuid
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request and response details."""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process a request and log information about it."""
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            # Skip logging for excluded paths
            return await call_next(request)

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Add request ID to request state for use in route handlers
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Log request details
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
            },
        )

        # Process the request
        try:
            response = await call_next(request)

            # Calculate request processing time
            process_time = time.time() - start_time

            # Add request ID to response headers for client-side tracking
            response.headers["X-Request-ID"] = request_id

            # Log response details
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "processing_time_ms": round(process_time * 1000, 2),
                    "content_length": response.headers.get("content-length", "unknown"),
                    "content_type": response.headers.get("content-type", "unknown"),
                },
            )

            return response

        except Exception as e:
            # Calculate request processing time
            process_time = time.time() - start_time

            # Log error details
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "exception": str(e),
                    "exception_type": type(e).__name__,
                    "processing_time_ms": round(process_time * 1000, 2),
                },
                exc_info=True,
            )

            # Re-raise the exception for the global exception handlers
            raise


class RequestLoggingMiddleware:
    """ASGI middleware for logging requests/responses (alternative implementation)."""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list[str]] = None,
    ):
        self.app = app
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process ASGI request and log information."""
        if scope["type"] != "http":
            # Pass through non-HTTP requests (like WebSockets)
            await self.app(scope, receive, send)
            return

        # Get path from scope
        path = scope.get("path", "")
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            # Skip logging for excluded paths
            await self.app(scope, receive, send)
            return

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store start time
        start_time = time.time()

        # Log request details
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": scope.get("method", "unknown"),
                "path": path,
                "client_host": scope.get("client", ("unknown", 0))[0],
                "scheme": scope.get("scheme", "unknown"),
            },
        )

        # Create a modified send function to capture response info
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Calculate request processing time
                process_time = time.time() - start_time

                # Get status code from response
                status_code = message.get("status", 0)

                # Get headers from response
                headers = {
                    k.decode(): v.decode() for k, v in message.get("headers", [])
                }

                # Add request ID to response headers
                message["headers"] = [
                    *message.get("headers", []),
                    (b"x-request-id", request_id.encode()),
                ]

                # Log response details
                logger.info(
                    f"Request completed",
                    extra={
                        "request_id": request_id,
                        "status_code": status_code,
                        "processing_time_ms": round(process_time * 1000, 2),
                        "content_type": headers.get("content-type", "unknown"),
                    },
                )

            # Forward the message
            await send(message)

        # Call the application with our modified send function
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            # Calculate request processing time
            process_time = time.time() - start_time

            # Log error details
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "exception": str(e),
                    "exception_type": type(e).__name__,
                    "processing_time_ms": round(process_time * 1000, 2),
                },
                exc_info=True,
            )

            # Re-raise the exception
            raise


def add_logging_middleware(app: FastAPI) -> None:
    """Add logging middleware to FastAPI application."""
    app.add_middleware(LoggingMiddleware)
