from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from app.errors.error_codes import ERROR_CODE_TO_STATUS, ERROR_MESSAGES, ErrorCode


class BaseAPIException(HTTPException):
    """Base API exception with status code and details."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or "ERROR"


class NotFoundError(BaseAPIException):
    """Resource not found error."""

    def __init__(self, detail: str = None, error_code: str = ErrorCode.RES_NOT_FOUND):
        if detail is None:
            detail = ERROR_MESSAGES.get(error_code, "Resource not found")
        super().__init__(
            status_code=ERROR_CODE_TO_STATUS.get(error_code, status.HTTP_404_NOT_FOUND),
            detail=detail,
            error_code=error_code,
        )


class AuthenticationError(BaseAPIException):
    """Authentication error."""

    def __init__(
        self, detail: str = None, error_code: str = ErrorCode.AUTH_INVALID_CREDENTIALS
    ):
        if detail is None:
            detail = ERROR_MESSAGES.get(error_code, "Authentication failed")
        super().__init__(
            status_code=ERROR_CODE_TO_STATUS.get(
                error_code, status.HTTP_401_UNAUTHORIZED
            ),
            detail=detail,
            error_code=error_code,
        )


class AuthorizationError(BaseAPIException):
    """Authorization error."""

    def __init__(
        self, detail: str = None, error_code: str = ErrorCode.PERM_INSUFFICIENT_RIGHTS
    ):
        if detail is None:
            detail = ERROR_MESSAGES.get(error_code, "Not authorized")
        super().__init__(
            status_code=ERROR_CODE_TO_STATUS.get(error_code, status.HTTP_403_FORBIDDEN),
            detail=detail,
            error_code=error_code,
        )


class ValidationError(BaseAPIException):
    """Validation error."""

    def __init__(
        self, detail: str = None, error_code: str = ErrorCode.VAL_INVALID_INPUT
    ):
        if detail is None:
            detail = ERROR_MESSAGES.get(error_code, "Validation error")
        super().__init__(
            status_code=ERROR_CODE_TO_STATUS.get(
                error_code, status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=detail,
            error_code=error_code,
        )


class DatabaseError(BaseAPIException):
    """Database error."""

    def __init__(self, detail: str = None, error_code: str = ErrorCode.DB_QUERY_ERROR):
        if detail is None:
            detail = ERROR_MESSAGES.get(error_code, "Database error")
        super().__init__(
            status_code=ERROR_CODE_TO_STATUS.get(
                error_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=detail,
            error_code=error_code,
        )


class ExternalServiceError(BaseAPIException):
    """External service error."""

    def __init__(
        self, detail: str = None, error_code: str = ErrorCode.EXT_SERVICE_UNAVAILABLE
    ):
        if detail is None:
            detail = ERROR_MESSAGES.get(error_code, "External service error")
        super().__init__(
            status_code=ERROR_CODE_TO_STATUS.get(
                error_code, status.HTTP_502_BAD_GATEWAY
            ),
            detail=detail,
            error_code=error_code,
        )


class RateLimitError(BaseAPIException):
    """Rate limit error."""

    def __init__(
        self, detail: str = None, error_code: str = ErrorCode.RATE_TOO_MANY_REQUESTS
    ):
        if detail is None:
            detail = ERROR_MESSAGES.get(error_code, "Too many requests")
        super().__init__(
            status_code=ERROR_CODE_TO_STATUS.get(
                error_code, status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=detail,
            error_code=error_code,
        )


class BusinessError(BaseAPIException):
    """Business logic error."""

    def __init__(
        self, detail: str = None, error_code: str = ErrorCode.BIZ_INVALID_OPERATION
    ):
        if detail is None:
            detail = ERROR_MESSAGES.get(error_code, "Business logic error")
        super().__init__(
            status_code=ERROR_CODE_TO_STATUS.get(
                error_code, status.HTTP_400_BAD_REQUEST
            ),
            detail=detail,
            error_code=error_code,
        )


class APIError(BaseAPIException):
    """Generic API error."""

    def __init__(
        self, detail: str = None, error_code: str = ErrorCode.INT_SERVER_ERROR
    ):
        if detail is None:
            detail = ERROR_MESSAGES.get(error_code, "API error")
        super().__init__(
            status_code=ERROR_CODE_TO_STATUS.get(
                error_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=detail,
            error_code=error_code,
        )
