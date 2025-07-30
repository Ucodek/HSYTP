from typing import Callable, List, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    parse_accept_language,
    set_language,
)


class LanguageMiddleware(BaseHTTPMiddleware):
    """
    Middleware to detect and set language preferences from request headers.

    This middleware:
    1. Extracts language preference from Accept-Language header
    2. Stores the language in request state for use in route handlers
    3. Optionally sets a language cookie in the response
    """

    def __init__(
        self,
        app: ASGIApp,
        default_language: str = DEFAULT_LANGUAGE,
        supported_languages: Optional[List[str]] = None,
        set_cookie: bool = False,
    ):
        """
        Initialize the language middleware.

        Args:
            app: ASGI application
            default_language: Default language to use if no preference is found
            supported_languages: List of supported language codes
            set_cookie: Whether to set a language cookie in the response
        """
        super().__init__(app)
        self.default_language = default_language
        self.supported_languages = supported_languages or SUPPORTED_LANGUAGES
        self.set_cookie = set_cookie

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process a request and determine the language preference.

        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler

        Returns:
            Response from the next middleware or route handler
        """
        # Extract language from Accept-Language header
        accept_language = request.headers.get("Accept-Language")
        language = parse_accept_language(
            accept_language, self.supported_languages, self.default_language
        )

        # Store the language in request state for use in route handlers
        request.state.language = language

        # Process the request
        response = await call_next(request)

        # Optionally set a language cookie in the response
        if self.set_cookie:
            set_language(response, language)

        # Add language header to response for debugging/transparency
        response.headers["Content-Language"] = language

        return response


def add_language_middleware(
    app: FastAPI,
    default_language: str = DEFAULT_LANGUAGE,
    supported_languages: Optional[List[str]] = None,
    set_cookie: bool = False,
) -> None:
    """
    Add language middleware to the FastAPI application.

    Args:
        app: FastAPI application
        default_language: Default language to use if no preference is found
        supported_languages: List of supported language codes
        set_cookie: Whether to set a language cookie in the response
    """
    app.add_middleware(
        LanguageMiddleware,
        default_language=default_language,
        supported_languages=supported_languages,
        set_cookie=set_cookie,
    )
