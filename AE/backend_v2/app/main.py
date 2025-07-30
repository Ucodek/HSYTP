from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config.base import settings
from app.core.startup import register_startup_and_shutdown_events
from app.errors.handlers import register_exception_handlers
from app.middleware.cors import setup_cors_middleware
from app.middleware.language import add_language_middleware
from app.middleware.logging_middleware import add_logging_middleware
from app.middleware.rate_limiting import add_rate_limiting_middleware
from app.monitoring.health import router as health_router
from app.monitoring.metrics import setup_metrics
from app.monitoring.tracing import setup_tracing


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Register startup and shutdown events
    register_startup_and_shutdown_events(app)

    # Configure CORS
    setup_cors_middleware(app)

    # Add monitoring middleware and endpoints
    setup_metrics(app)
    setup_tracing(app)

    # Add custom middleware (order matters)
    add_language_middleware(app)  # Add this line to enable language detection

    # Add logging middleware
    add_logging_middleware(app)

    # Add rate limiting middleware with our defined limits
    add_rate_limiting_middleware(app)

    # Register exception handlers
    register_exception_handlers(app)

    # Include routers
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
