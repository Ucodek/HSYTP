import logging
from typing import Callable

from fastapi import FastAPI

from app.core.logging import setup_logging
from app.db.session import ensure_database_exists

logger = logging.getLogger(__name__)


def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Factory function for creating a handler to run on application startup.

    Args:
        app: FastAPI application instance

    Returns:
        Callable that runs startup routines
    """

    async def start_app() -> None:
        # Setup application logging
        setup_logging()

        logger.info("Running application startup tasks")

        # First ensure the database exists
        try:
            logger.info("Ensuring database exists")
            await ensure_database_exists()
        except Exception as e:
            logger.error(f"Error ensuring database exists: {e}")
            # Continue anyway since tables creation will fail appropriately if needed

        # Create database tables if they don't exist
        # In production, you may want to use migrations instead
        # try:
        #     logger.info("Initializing database")
        #     init_db()  # Use the dedicated init_db function
        # except Exception as e:
        #     logger.error(f"Error creating database tables: {e}")
        #     raise

        # Initialize any other services or connections
        logger.info("Application startup complete")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Factory function for creating a handler to run on application shutdown.

    Args:
        app: FastAPI application instance

    Returns:
        Callable that runs shutdown routines
    """

    async def stop_app() -> None:
        logger.info("Running application shutdown tasks")

        # Close any open resources or connections

        logger.info("Application shutdown complete")

    return stop_app


def register_startup_and_shutdown_events(app: FastAPI) -> None:
    """
    Register startup and shutdown event handlers.

    Args:
        app: FastAPI application instance
    """
    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))
