# Error handling package initialization
from app.errors.error_codes import ErrorCode
from app.errors.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BaseAPIException,
    BusinessError,
    DatabaseError,
    ExternalServiceError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from app.errors.handlers import register_exception_handlers

__all__ = [
    "BaseAPIException",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "DatabaseError",
    "ExternalServiceError",
    "RateLimitError",
    "BusinessError",
    "APIError",
    "ErrorCode",
    "register_exception_handlers",
]
