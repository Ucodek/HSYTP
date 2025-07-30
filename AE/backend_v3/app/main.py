"""
Main entry point for the FastAPI application.

This module configures and creates the FastAPI app, loads settings, and includes the main API router.
"""

from fastapi import FastAPI
from fastcore.config.settings import get_settings
from fastcore.factory.app import configure_app

from app.api.v1.router import api_router
from app.scheduler.manager import setup_scheduler


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # for fastcore package
    # Configure the app with default settings
    configure_app(app, settings)

    setup_scheduler(app, settings)

    # Include API router
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
