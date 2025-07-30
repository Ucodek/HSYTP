import logging
import time

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.utils import setup_logging
from app.db.session import get_db
from app.db.utils import check_database_connection, get_database_stats
from app.middleware.rate_limiting import RateLimitMiddleware
from app.utils.response import create_error_response

# Set up logging first
setup_logging(settings.LOG_LEVEL if hasattr(settings, "LOG_LEVEL") else "INFO")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# Add middleware
app.add_middleware(RateLimitMiddleware)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request details and timing."""
    start_time = time.time()

    # Generate a unique request ID
    request_id = f"{time.time():.0f}-{request.client.host}"

    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log request details
        logging.info(
            f"Request processed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": process_time * 1000,
                "client_ip": request.client.host,
            },
        )

        # Add X-Process-Time header to response
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logging.exception(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "duration_ms": process_time * 1000,
                "exception": str(e),
            },
        )
        raise


# Add a custom exception handler for better JSON error messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    # Check for JSON decode errors specifically
    for error in errors:
        if error["type"] == "json_invalid":
            return JSONResponse(
                status_code=400,
                content=create_error_response(
                    code="INVALID_JSON",
                    message="Invalid JSON format. Please ensure your JSON doesn't have "
                    "trailing commas, and that all strings are properly quoted.",
                    status_code=400,
                ),
            )

    # Process validation errors to ensure they're JSON serializable
    formatted_errors = []
    for error in errors:
        # Convert the error to a clean dict with only serializable values
        formatted_error = {
            "type": error.get("type", "validation_error"),
            "loc": error.get("loc", []),
            "msg": str(error.get("msg", "Validation error")),
            "input": str(error.get("input", "")),
        }
        formatted_errors.append(formatted_error)

    # Default response for other validation errors
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            code="VALIDATION_ERROR",
            message="Validation error on request data",
            details=formatted_errors,
            status_code=422,
        ),
    )


# Add exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and return a consistent error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            code=f"HTTP_{exc.status_code}",
            message=exc.detail,
            status_code=exc.status_code,
        ),
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Enhanced health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint to verify the API is running."""
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": getattr(settings, "ENVIRONMENT", "development"),
    }


@app.get("/health/db", tags=["health"])
async def db_health_check(db: AsyncSession = Depends(get_db)):
    """Check database connection."""
    if await check_database_connection(db):
        return {"status": "ok", "database": "connected"}

    raise HTTPException(status_code=503, detail="Database connection failed")


@app.get("/health/stats", tags=["health"])
async def health_stats(db: AsyncSession = Depends(get_db)):
    """Get detailed health statistics."""
    db_stats = await get_database_stats(db)

    return {
        "status": "ok",
        "api": {
            "version": settings.APP_VERSION,
            "environment": getattr(settings, "ENVIRONMENT", "development"),
        },
        "database": db_stats,
    }
