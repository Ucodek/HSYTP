import logging
import uuid
from datetime import timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config.base import settings
from app.core.security import create_access_token
from app.errors.error_codes import ErrorCode
from app.errors.exceptions import AuthenticationError, NotFoundError, ValidationError
from app.modules.auth.crud import (
    authenticate_user,
    change_password,
    create_token,
    create_user,
    get_token,
    get_user_by_email,
    get_user_by_username,
    get_valid_token,
    revoke_all_user_tokens,
    revoke_token,
    update_user,
)
from app.modules.auth.models import TokenType, User
from app.modules.auth.schemas import TokenPair, UserCreate, UserUpdate

logger = logging.getLogger(__name__)


def register_user(db: Session, user_data: UserCreate) -> User:
    """
    Register a new user.

    Args:
        db: Database session
        user_data: User data

    Returns:
        Created user

    Raises:
        ValidationError: If the username or email is already registered
    """
    # Check if username already exists
    if get_user_by_username(db, user_data.username):
        raise ValidationError(
            detail="Username already registered",
            error_code=ErrorCode.VAL_DUPLICATE_ENTRY,
        )

    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise ValidationError(
            detail="Email already registered", error_code=ErrorCode.VAL_DUPLICATE_ENTRY
        )

    # Create user
    user = create_user(db, user_data)

    # Generate verification token if needed and email verification is enabled
    if not user.is_verified:
        generate_email_verification_token(db, user.id)
        # Here you would send the verification email - implement in email service
        logger.info(f"Generated verification token for user {user.id}")

    return user


def login_user(db: Session, username: str, password: str) -> Tuple[User, TokenPair]:
    """
    Authenticate a user and generate tokens.

    Args:
        db: Database session
        username: Username or email
        password

    Returns:
        Tuple of (user, token_pair)

    Raises:
        AuthenticationError: If authentication fails
    """
    # Authenticate user - this uses get_user_by_email_or_username internally
    user = authenticate_user(db, username, password)

    if not user:
        raise AuthenticationError(
            detail="Invalid username or password",
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
        )

    if not user.is_active:
        raise AuthenticationError(
            detail="User account is inactive", error_code=ErrorCode.AUTH_USER_INACTIVE
        )

    # Check if account is locked
    if hasattr(user, "is_locked") and user.is_locked:
        raise AuthenticationError(
            detail="Account locked due to security concerns",
            error_code=ErrorCode.BIZ_ACCOUNT_LOCKED,
        )

    # Generate tokens for authenticated user
    token_pair = generate_token_pair(db, user.id)

    return user, token_pair


def refresh_tokens(db: Session, refresh_token: str) -> TokenPair:
    """
    Refresh access and refresh tokens.

    Args:
        db: Database session
        refresh_token: Refresh token

    Returns:
        New token pair

    Raises:
        AuthenticationError: If the refresh token is invalid or expired
    """
    # Get valid token (this will handle expiration and revocation checks)
    token_db = get_valid_token(db, refresh_token, TokenType.REFRESH)

    if not token_db:
        # Get the token without validity check to determine the exact error
        basic_token = get_token(db, refresh_token, TokenType.REFRESH)

        if not basic_token:
            raise AuthenticationError(
                detail="Invalid refresh token", error_code=ErrorCode.AUTH_INVALID_TOKEN
            )
        elif basic_token.is_revoked:
            raise AuthenticationError(
                detail="Refresh token has been revoked",
                error_code=ErrorCode.AUTH_INVALID_TOKEN,
            )
        else:
            raise AuthenticationError(
                detail="Refresh token has expired",
                error_code=ErrorCode.AUTH_EXPIRED_TOKEN,
            )

    # Revoke old refresh token for security
    revoke_token(db, token_db)

    # Generate new token pair with different expiration to ensure different tokens
    # Generate new access token with a different expiration time to make it unique
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)
    refresh_token_expires = timedelta(days=7)  # 1 week

    # Create a completely new token pair
    token_pair = generate_token_pair(
        db,
        token_db.user_id,
        access_token_expires=access_token_expires,
        refresh_token_expires=refresh_token_expires,
    )

    return token_pair


def generate_token_pair(
    db: Session,
    user_id: int,
    access_token_expires: Optional[timedelta] = None,
    refresh_token_expires: Optional[timedelta] = None,
) -> TokenPair:
    """
    Generate access and refresh token pair for a user.

    Args:
        db: Database session
        user_id: User ID
        access_token_expires: Optional custom expiration for access token
        refresh_token_expires: Optional custom expiration for refresh token

    Returns:
        Token pair containing access and refresh tokens
    """
    # Set expiration times
    if access_token_expires is None:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if refresh_token_expires is None:
        refresh_token_expires = timedelta(days=7)  # 1 week

    # Generate tokens
    access_token = create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )
    refresh_token = str(uuid.uuid4())

    # Save tokens to database
    create_token(
        db,
        user_id=user_id,
        token=access_token,
        token_type=TokenType.ACCESS,
        expires_delta=access_token_expires,
    )

    refresh_token_db = create_token(
        db,
        user_id=user_id,
        token=refresh_token,
        token_type=TokenType.REFRESH,
        expires_delta=refresh_token_expires,
    )

    # Create token response
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_at=refresh_token_db.expires_at,
    )


def logout_user(db: Session, user_id: int) -> None:
    """
    Logout a user by revoking all their tokens.

    Args:
        db: Database session
        user_id: User ID
    """
    revoked_count = revoke_all_user_tokens(db, user_id)
    logger.info(f"Logged out user {user_id}, revoked {revoked_count} tokens")


def update_user_profile(db: Session, user_id: int, user_update: UserUpdate) -> User:
    """
    Update a user's profile.

    Args:
        db: Database session
        user_id: User ID
        user_update: Updated user data

    Returns:
        Updated user

    Raises:
        NotFoundError: If the user is not found
        ValidationError: If the update would create duplicate email/username
    """
    # CRUD function already handles uniqueness checks and returns None if update fails
    updated_user = update_user(db, user_id, user_update)

    if not updated_user:
        raise NotFoundError(
            detail="User not found or update failed due to constraints",
            error_code=ErrorCode.RES_NOT_FOUND,
        )

    # If email was changed, user needs to verify the new email
    if user_update.email is not None and not updated_user.is_verified:
        generate_email_verification_token(db, user_id)
        # Here you would send the verification email - implement in email service
        logger.info(f"Generated new verification token for updated email")

    return updated_user


def change_user_password(
    db: Session, user_id: int, current_password: str, new_password: str
) -> User:
    """
    Change a user's password.

    Args:
        db: Database session
        user_id: User ID
        current_password: Current password
        new_password: New password

    Returns:
        Updated user

    Raises:
        NotFoundError: If the user is not found
        AuthenticationError: If the current password is incorrect
    """
    # Get the user first
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError(detail="User not found", error_code=ErrorCode.RES_NOT_FOUND)

    # CRUD change_password checks the current password and throws appropriate error
    return change_password(db, user, new_password)


def request_password_reset(db: Session, email: str) -> Optional[str]:
    """
    Request a password reset.

    Args:
        db: Database session
        email: User email

    Returns:
        Reset token or None if user is not found
    """
    # Get user by email
    user = get_user_by_email(db, email)

    if not user:
        # Don't leak information about user existence
        logger.info(f"Password reset requested for non-existent email: {email}")
        return None

    # Revoke any existing reset tokens
    revoke_all_user_tokens(db, user.id, TokenType.RESET_PASSWORD)

    # Create reset token
    reset_token = str(uuid.uuid4())

    # Save token to database
    create_token(
        db,
        user_id=user.id,
        token=reset_token,
        token_type=TokenType.RESET_PASSWORD,
        expires_delta=timedelta(hours=24),
    )

    logger.info(f"Generated password reset token for user {user.id}")
    # Here you would send the reset email - implement in email service

    return reset_token


def reset_password(db: Session, token: str, new_password: str) -> User:
    """
    Reset a user's password using a reset token.

    Args:
        db: Database session
        token: Reset token
        new_password: New password

    Returns:
        Updated user

    Raises:
        AuthenticationError: If the token is invalid or expired
        NotFoundError: If the user is not found
    """
    # Get valid token (handles expiration and revocation)
    token_db = get_valid_token(db, token, TokenType.RESET_PASSWORD)

    if not token_db:
        # Get the token without validity check to determine the exact error
        basic_token = get_token(db, token, TokenType.RESET_PASSWORD)

        if not basic_token:
            raise AuthenticationError(
                detail="Invalid reset token", error_code=ErrorCode.AUTH_INVALID_TOKEN
            )
        elif basic_token.is_revoked:
            raise AuthenticationError(
                detail="Reset token has been revoked",
                error_code=ErrorCode.AUTH_INVALID_TOKEN,
            )
        else:
            raise AuthenticationError(
                detail="Reset token has expired",
                error_code=ErrorCode.AUTH_EXPIRED_TOKEN,
            )

    # Get user
    user = token_db.user
    if not user:
        raise NotFoundError(detail="User not found", error_code=ErrorCode.RES_NOT_FOUND)

    # Revoke token to prevent reuse
    revoke_token(db, token_db)

    # Set new password and revoke all user tokens for security
    updated_user = change_password(db, user, new_password)
    logger.info(f"Reset password for user {user.id}")

    return updated_user


def verify_email(db: Session, token: str) -> User:
    """
    Verify a user's email using a verification token.

    Args:
        db: Database session
        token: Verification token

    Returns:
        Updated user

    Raises:
        AuthenticationError: If the token is invalid or expired
        NotFoundError: If the user is not found
    """
    # Get valid token (handles expiration and revocation)
    token_db = get_valid_token(db, token, TokenType.VERIFY_EMAIL)

    if not token_db:
        # Get the token without validity check to determine the exact error
        basic_token = get_token(db, token, TokenType.VERIFY_EMAIL)

        if not basic_token:
            raise AuthenticationError(
                detail="Invalid verification token",
                error_code=ErrorCode.AUTH_INVALID_TOKEN,
            )
        elif basic_token.is_revoked:
            raise AuthenticationError(
                detail="Verification token has been revoked",
                error_code=ErrorCode.AUTH_INVALID_TOKEN,
            )
        else:
            raise AuthenticationError(
                detail="Verification token has expired",
                error_code=ErrorCode.AUTH_EXPIRED_TOKEN,
            )

    # Get user
    user = token_db.user
    if not user:
        raise NotFoundError(detail="User not found", error_code=ErrorCode.RES_NOT_FOUND)

    # Update user verification status
    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)

    # Revoke token to prevent reuse
    revoke_token(db, token_db)
    logger.info(f"Verified email for user {user.id}")

    return user


def generate_email_verification_token(db: Session, user_id: int) -> str:
    """
    Generate an email verification token for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Verification token
    """
    # Revoke any existing verification tokens
    revoke_all_user_tokens(db, user_id, TokenType.VERIFY_EMAIL)

    # Create verification token
    verification_token = str(uuid.uuid4())

    # Save token to database
    create_token(
        db,
        user_id=user_id,
        token=verification_token,
        token_type=TokenType.VERIFY_EMAIL,
        expires_delta=timedelta(days=7),  # 7 days to verify email
    )

    return verification_token
