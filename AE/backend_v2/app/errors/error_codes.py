from enum import Enum


class ErrorCodePrefix(str, Enum):
    """Prefixes for different categories of error codes."""

    AUTHENTICATION = "AUTH"
    AUTHORIZATION = "PERM"
    VALIDATION = "VAL"
    RESOURCE = "RES"
    DATABASE = "DB"
    EXTERNAL = "EXT"
    INTERNAL = "INT"
    RATE_LIMIT = "RATE"
    BUSINESS = "BIZ"


class ErrorCode:
    """
    Standard error codes for the API.

    Format: PREFIX_DESCRIPTION

    Examples:
    - AUTH_INVALID_CREDENTIALS
    - RES_NOT_FOUND
    - VAL_INVALID_INPUT
    """

    # Authentication errors
    AUTH_INVALID_CREDENTIALS = f"{ErrorCodePrefix.AUTHENTICATION}_INVALID_CREDENTIALS"
    AUTH_EXPIRED_TOKEN = f"{ErrorCodePrefix.AUTHENTICATION}_EXPIRED_TOKEN"
    AUTH_INVALID_TOKEN = f"{ErrorCodePrefix.AUTHENTICATION}_INVALID_TOKEN"
    AUTH_MISSING_TOKEN = f"{ErrorCodePrefix.AUTHENTICATION}_MISSING_TOKEN"
    AUTH_USER_INACTIVE = f"{ErrorCodePrefix.AUTHENTICATION}_USER_INACTIVE"
    AUTH_EMAIL_NOT_VERIFIED = (
        f"{ErrorCodePrefix.AUTHENTICATION}_EMAIL_NOT_VERIFIED"  # Add this line
    )

    # Authorization errors
    PERM_INSUFFICIENT_RIGHTS = f"{ErrorCodePrefix.AUTHORIZATION}_INSUFFICIENT_RIGHTS"
    PERM_FORBIDDEN_ACTION = f"{ErrorCodePrefix.AUTHORIZATION}_FORBIDDEN_ACTION"

    # Validation errors
    VAL_INVALID_INPUT = f"{ErrorCodePrefix.VALIDATION}_INVALID_INPUT"
    VAL_MISSING_FIELD = f"{ErrorCodePrefix.VALIDATION}_MISSING_FIELD"
    VAL_FIELD_TOO_LONG = f"{ErrorCodePrefix.VALIDATION}_FIELD_TOO_LONG"
    VAL_FIELD_TOO_SHORT = f"{ErrorCodePrefix.VALIDATION}_FIELD_TOO_SHORT"
    VAL_INVALID_FORMAT = f"{ErrorCodePrefix.VALIDATION}_INVALID_FORMAT"
    VAL_DUPLICATE_ENTRY = f"{ErrorCodePrefix.VALIDATION}_DUPLICATE_ENTRY"

    # Resource errors
    RES_NOT_FOUND = f"{ErrorCodePrefix.RESOURCE}_NOT_FOUND"
    RES_ALREADY_EXISTS = f"{ErrorCodePrefix.RESOURCE}_ALREADY_EXISTS"
    RES_STATE_CONFLICT = f"{ErrorCodePrefix.RESOURCE}_STATE_CONFLICT"

    # Database errors
    DB_CONNECTION_ERROR = f"{ErrorCodePrefix.DATABASE}_CONNECTION_ERROR"
    DB_QUERY_ERROR = f"{ErrorCodePrefix.DATABASE}_QUERY_ERROR"
    DB_INTEGRITY_ERROR = f"{ErrorCodePrefix.DATABASE}_INTEGRITY_ERROR"
    DB_TRANSACTION_ERROR = f"{ErrorCodePrefix.DATABASE}_TRANSACTION_ERROR"

    # External service errors
    EXT_SERVICE_UNAVAILABLE = f"{ErrorCodePrefix.EXTERNAL}_SERVICE_UNAVAILABLE"
    EXT_REQUEST_TIMEOUT = f"{ErrorCodePrefix.EXTERNAL}_REQUEST_TIMEOUT"
    EXT_INVALID_RESPONSE = f"{ErrorCodePrefix.EXTERNAL}_INVALID_RESPONSE"

    # Internal errors
    INT_SERVER_ERROR = f"{ErrorCodePrefix.INTERNAL}_SERVER_ERROR"
    INT_NOT_IMPLEMENTED = f"{ErrorCodePrefix.INTERNAL}_NOT_IMPLEMENTED"
    INT_SERVICE_ERROR = f"{ErrorCodePrefix.INTERNAL}_SERVICE_ERROR"

    # Rate limiting errors
    RATE_TOO_MANY_REQUESTS = f"{ErrorCodePrefix.RATE_LIMIT}_TOO_MANY_REQUESTS"

    # Business logic errors
    BIZ_INVALID_OPERATION = f"{ErrorCodePrefix.BUSINESS}_INVALID_OPERATION"
    BIZ_RULE_VIOLATION = f"{ErrorCodePrefix.BUSINESS}_RULE_VIOLATION"
    BIZ_INSUFFICIENT_FUNDS = f"{ErrorCodePrefix.BUSINESS}_INSUFFICIENT_FUNDS"
    BIZ_ACCOUNT_LOCKED = f"{ErrorCodePrefix.BUSINESS}_ACCOUNT_LOCKED"


# Error code to HTTP status code mapping
ERROR_CODE_TO_STATUS = {
    # Authentication errors -> 401 Unauthorized
    ErrorCode.AUTH_INVALID_CREDENTIALS: 401,
    ErrorCode.AUTH_EXPIRED_TOKEN: 401,
    ErrorCode.AUTH_INVALID_TOKEN: 401,
    ErrorCode.AUTH_MISSING_TOKEN: 401,
    ErrorCode.AUTH_USER_INACTIVE: 401,
    ErrorCode.AUTH_EMAIL_NOT_VERIFIED: 401,  # Add this line
    # Authorization errors -> 403 Forbidden
    ErrorCode.PERM_INSUFFICIENT_RIGHTS: 403,
    ErrorCode.PERM_FORBIDDEN_ACTION: 403,
    # Validation errors -> 422 Unprocessable Entity
    ErrorCode.VAL_INVALID_INPUT: 422,
    ErrorCode.VAL_MISSING_FIELD: 422,
    ErrorCode.VAL_FIELD_TOO_LONG: 422,
    ErrorCode.VAL_FIELD_TOO_SHORT: 422,
    ErrorCode.VAL_INVALID_FORMAT: 422,
    ErrorCode.VAL_DUPLICATE_ENTRY: 422,
    # Resource errors -> 404 Not Found or 409 Conflict
    ErrorCode.RES_NOT_FOUND: 404,
    ErrorCode.RES_ALREADY_EXISTS: 409,
    ErrorCode.RES_STATE_CONFLICT: 409,
    # Database errors -> 500 Internal Server Error
    ErrorCode.DB_CONNECTION_ERROR: 500,
    ErrorCode.DB_QUERY_ERROR: 500,
    ErrorCode.DB_INTEGRITY_ERROR: 500,
    ErrorCode.DB_TRANSACTION_ERROR: 500,
    # External service errors -> 502 Bad Gateway or 504 Gateway Timeout
    ErrorCode.EXT_SERVICE_UNAVAILABLE: 502,
    ErrorCode.EXT_REQUEST_TIMEOUT: 504,
    ErrorCode.EXT_INVALID_RESPONSE: 502,
    # Internal errors -> 500 Internal Server Error
    ErrorCode.INT_SERVER_ERROR: 500,
    ErrorCode.INT_NOT_IMPLEMENTED: 501,
    ErrorCode.INT_SERVICE_ERROR: 500,
    # Rate limiting errors -> 429 Too Many Requests
    ErrorCode.RATE_TOO_MANY_REQUESTS: 429,
    # Business logic errors -> 400 Bad Request
    ErrorCode.BIZ_INVALID_OPERATION: 400,
    ErrorCode.BIZ_RULE_VIOLATION: 400,
    ErrorCode.BIZ_INSUFFICIENT_FUNDS: 400,
    ErrorCode.BIZ_ACCOUNT_LOCKED: 400,
}

# Human-readable error messages
ERROR_MESSAGES = {
    ErrorCode.AUTH_INVALID_CREDENTIALS: "Invalid username or password",
    ErrorCode.AUTH_EXPIRED_TOKEN: "Authentication token has expired",
    ErrorCode.AUTH_INVALID_TOKEN: "Invalid authentication token",
    ErrorCode.AUTH_MISSING_TOKEN: "Authentication token is missing",
    ErrorCode.AUTH_USER_INACTIVE: "User account is inactive",
    ErrorCode.AUTH_EMAIL_NOT_VERIFIED: "Email address has not been verified",  # Add this line
    ErrorCode.PERM_INSUFFICIENT_RIGHTS: "You don't have sufficient permissions to perform this action",
    ErrorCode.PERM_FORBIDDEN_ACTION: "This action is forbidden",
    ErrorCode.VAL_INVALID_INPUT: "Invalid input data",
    ErrorCode.VAL_MISSING_FIELD: "Required field is missing",
    ErrorCode.VAL_FIELD_TOO_LONG: "Field value exceeds maximum length",
    ErrorCode.VAL_FIELD_TOO_SHORT: "Field value is shorter than minimum length",
    ErrorCode.VAL_INVALID_FORMAT: "Field value has an invalid format",
    ErrorCode.VAL_DUPLICATE_ENTRY: "A record with this value already exists",
    ErrorCode.RES_NOT_FOUND: "The requested resource was not found",
    ErrorCode.RES_ALREADY_EXISTS: "The resource already exists",
    ErrorCode.RES_STATE_CONFLICT: "The resource is in an invalid state for this operation",
    ErrorCode.DB_CONNECTION_ERROR: "Database connection error",
    ErrorCode.DB_QUERY_ERROR: "Database query error",
    ErrorCode.DB_INTEGRITY_ERROR: "Database integrity constraint violation",
    ErrorCode.DB_TRANSACTION_ERROR: "Database transaction error",
    ErrorCode.EXT_SERVICE_UNAVAILABLE: "External service is currently unavailable",
    ErrorCode.EXT_REQUEST_TIMEOUT: "Request to external service timed out",
    ErrorCode.EXT_INVALID_RESPONSE: "Invalid response from external service",
    ErrorCode.INT_SERVER_ERROR: "Internal server error",
    ErrorCode.INT_NOT_IMPLEMENTED: "This feature is not implemented yet",
    ErrorCode.INT_SERVICE_ERROR: "Internal service error",
    ErrorCode.RATE_TOO_MANY_REQUESTS: "Too many requests, please try again later",
    ErrorCode.BIZ_INVALID_OPERATION: "This operation is not valid in the current context",
    ErrorCode.BIZ_RULE_VIOLATION: "The operation violates business rules",
    ErrorCode.BIZ_INSUFFICIENT_FUNDS: "Insufficient funds for this operation",
    ErrorCode.BIZ_ACCOUNT_LOCKED: "Account is locked",
}
