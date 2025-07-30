from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import ALL_METHODS

from app.core.config.base import settings


def setup_cors_middleware(
    app: FastAPI,
    allow_origins: Optional[List[str]] = None,
    allow_origin_regex: Optional[str] = None,
    allow_methods: Optional[List[str]] = None,
    allow_headers: Optional[List[str]] = None,
    allow_credentials: bool = True,
    expose_headers: Optional[List[str]] = None,
    max_age: int = 600,
) -> None:
    """
    Configure CORS for the application.

    Args:
        app: FastAPI application
        allow_origins: List of allowed origins
        allow_origin_regex: Regex pattern for allowed origins
        allow_methods: List of allowed HTTP methods
        allow_headers: List of allowed HTTP headers
        allow_credentials: Whether to allow credentials
        expose_headers: Headers that should be exposed to the browser
        max_age: Maximum time (seconds) the results can be cached
    """
    # Use settings if not explicitly provided
    if allow_origins is None:
        allow_origins = settings.CORS_ORIGINS

    if allow_methods is None:
        allow_methods = ["*"]  # Allow all methods by default

    if allow_headers is None:
        allow_headers = [
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With",
            "X-Request-ID",
        ]

    if expose_headers is None:
        expose_headers = [
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ]

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=allow_origin_regex,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        allow_credentials=allow_credentials,
        expose_headers=expose_headers,
        max_age=max_age,
    )


def setup_cors_all_origins(app: FastAPI) -> None:
    """
    Configure CORS to allow all origins (for development only).

    Args:
        app: FastAPI application
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=ALL_METHODS,
        allow_headers=["*"],
        allow_credentials=False,  # Must be False when allow_origins contains "*"
    )


def setup_cors_from_settings(app: FastAPI) -> None:
    """
    Configure CORS from application settings.

    Args:
        app: FastAPI application
    """
    setup_cors_middleware(app)
