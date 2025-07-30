from typing import Annotated, Optional

from fastapi import Depends, Header, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config.base import settings
from app.core.security import ALGORITHM
from app.db.session import get_db
from app.errors.error_codes import ErrorCode
from app.errors.exceptions import AuthenticationError, AuthorizationError
from app.modules.auth.crud import get_user
from app.modules.auth.models import User, UserRole

# OAuth2 scheme for token validation - make sure it uses the correct token URL
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=True,
)

# OAuth2 scheme for optional token validation (doesn't error on missing token)
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from the JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        Authenticated user object

    Raises:
        AuthenticationError: If token is invalid or user doesn't exist
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user ID from 'sub' claim
        user_id: str = payload.get("sub")

        if user_id is None:
            raise AuthenticationError(
                detail="Invalid token payload",
                error_code=ErrorCode.AUTH_INVALID_TOKEN,
            )

        # Convert to integer
        user_id_int = int(user_id)

    except (JWTError, ValueError):
        raise AuthenticationError(
            detail="Could not validate credentials",
            error_code=ErrorCode.AUTH_INVALID_TOKEN,
        )

    # Get user from database
    user = get_user(db, user_id_int)

    if user is None:
        raise AuthenticationError(
            detail="User not found",
            error_code=ErrorCode.AUTH_INVALID_TOKEN,
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current user and verify the account is active.

    Args:
        current_user: Authenticated user object

    Returns:
        Active user object

    Raises:
        AuthenticationError: If user account is not active
    """
    if not current_user.is_active:
        raise AuthenticationError(
            detail="Inactive user account",
            error_code=ErrorCode.AUTH_USER_INACTIVE,
        )

    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current user and verify the account is verified.

    Args:
        current_user: Active user object

    Returns:
        Verified user object

    Raises:
        AuthenticationError: If user account is not verified
    """
    if not current_user.is_verified:
        raise AuthenticationError(
            detail="Email not verified",
            error_code=ErrorCode.AUTH_EMAIL_NOT_VERIFIED,
        )

    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current user and verify the user is an admin.

    Args:
        current_user: Active user object

    Returns:
        Admin user object

    Raises:
        AuthorizationError: If user doesn't have admin role
    """
    if current_user.role != UserRole.ADMIN:
        raise AuthorizationError(
            detail="Admin privileges required",
            error_code=ErrorCode.PERM_INSUFFICIENT_RIGHTS,
        )

    return current_user


async def optional_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(optional_oauth2_scheme),
) -> Optional[User]:
    """
    Get the current user if authenticated, or None if not.

    This dependency doesn't error on missing or invalid tokens,
    making it useful for endpoints that can work with both
    authenticated and anonymous users.

    Args:
        db: Database session
        token: Optional JWT token

    Returns:
        User object if authenticated, None otherwise
    """
    if token is None:
        return None

    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user ID
        user_id = payload.get("sub")
        if user_id is None:
            return None

        # Get and return user if active
        user = get_user(db, int(user_id))
        if user is not None and user.is_active:
            return user

    except (JWTError, ValueError):
        # Return None for any token validation errors
        return None

    return None


# Common dependency for extracting request ID (for logging/tracing)
async def get_request_id(
    request: Request, x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
) -> Optional[str]:
    """
    Get request ID from header or request state.

    Args:
        request: FastAPI request object
        x_request_id: Request ID from header

    Returns:
        Request ID or None
    """
    # Use header if provided
    if x_request_id:
        return x_request_id

    # Otherwise check request state (set by middleware)
    return getattr(request.state, "request_id", None)


# Type annotations for commonly used dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(get_current_verified_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
OptionalUser = Annotated[Optional[User], Depends(optional_current_user)]
RequestId = Annotated[Optional[str], Depends(get_request_id)]
