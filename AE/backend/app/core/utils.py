import logging
from typing import Any


def setup_logging(log_level: str = "INFO") -> None:
    """Set up structured logging with appropriate format."""
    logging_level = getattr(logging, log_level.upper())
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Reduce verbosity of some libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


def debug_settings(settings: Any) -> None:
    """Print debug information about settings, but hide sensitive values."""
    # Instead of scattered print statements in config.py
    settings_dict = {
        k: v
        for k, v in settings.model_dump().items()
        if k.lower() not in {"password", "secret", "key"}
    }

    logging.debug(f"Application configuration: {settings_dict}")
    logging.info(f"Database connection: {settings.SQLALCHEMY_DATABASE_URI}")
    logging.info(f"Application running as: {settings.APP_NAME} v{settings.APP_VERSION}")
