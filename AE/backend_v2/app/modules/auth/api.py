from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    EmailVerification,
    Login,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    RefreshToken,
    TokenPair,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.modules.auth.service import (
    change_user_password,
    login_user,
    logout_user,
    refresh_tokens,
    register_user,
    request_password_reset,
    reset_password,
    update_user_profile,
    verify_email,
)
from app.utils.response import (
    create_success_response,
    created_response,
    no_content_response,
)

router = APIRouter(tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    This endpoint allows creating a new user account. A verification email
    will be sent if email verification is enabled.

    - **email**: Valid email address (must be unique)
    - **username**: Username for the account (must be unique)
    - **password**: Strong password (at least 8 characters, including digits and uppercase letters)
    - **full_name**: Optional full name of the user
    """
    user = register_user(db, user_create)
    # Fix: Use the safe_dict method to serialize the User model before returning
    return created_response(user.safe_dict())


@router.post("/login", response_model=TokenPair, summary="Login with form data")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate a user using form data.

    This endpoint is compatible with OAuth2 password flow and returns an access token
    and refresh token if authentication is successful.

    - **username**: Username or email
    - **password**: User password
    """
    _, tokens = login_user(db, form_data.username, form_data.password)
    # Fix: Ensure tokens is a dictionary, not a TokenPair object
    return create_success_response(tokens.dict() if hasattr(tokens, "dict") else tokens)


@router.post("/login/json", response_model=TokenPair, summary="Login with JSON")
async def login_json(login_data: Login, db: Session = Depends(get_db)):
    """
    Authenticate a user using JSON.

    Alternative login endpoint that accepts JSON data instead of form data.

    - **username**: Username or email
    - **password**: User password
    """
    _, tokens = login_user(db, login_data.username, login_data.password)
    # Fix: Ensure tokens is a dictionary, not a TokenPair object
    return create_success_response(tokens.dict() if hasattr(tokens, "dict") else tokens)


@router.post("/refresh", response_model=TokenPair, summary="Refresh access token")
async def refresh(refresh_data: RefreshToken, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.

    This endpoint allows getting a new access token when the current one expires,
    without requiring the user to log in again.

    - **refresh_token**: Valid refresh token
    """
    tokens = refresh_tokens(db, refresh_data.refresh_token)
    # Fix: Ensure tokens is a dictionary, not a TokenPair object
    return create_success_response(tokens.dict() if hasattr(tokens, "dict") else tokens)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Logout")
async def logout(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """
    Logout user by revoking tokens.

    This endpoint revokes all tokens for the current user, effectively logging them out
    from all devices.

    Requires authentication.
    """
    logout_user(db, current_user.id)
    return no_content_response()


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.

    Returns information about the currently authenticated user.

    Requires authentication.
    """
    # FIX: Use safe_dict() to serialize the User model
    return create_success_response(current_user.safe_dict())


@router.put("/profile", response_model=UserResponse, summary="Update user profile")
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update user profile.

    Update the current user's profile information.

    - **email**: New email address (optional)
    - **username**: New username (optional)
    - **full_name**: New full name (optional)
    - **password**: New password (optional)

    Requires authentication.
    """
    updated_user = update_user_profile(db, current_user.id, user_update)
    # FIX: Use safe_dict() to serialize the User model
    return create_success_response(
        updated_user.safe_dict(), message="Profile updated successfully"
    )


@router.post("/password/change", response_model=UserResponse, summary="Change password")
async def change_password_endpoint(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Change user password.

    Allows authenticated users to change their password by providing the current
    password and a new password.

    - **current_password**: Current password for verification
    - **new_password**: New password to set

    Requires authentication.
    """
    user = change_user_password(
        db, current_user.id, password_data.current_password, password_data.new_password
    )
    # FIX: Use safe_dict() to serialize the User model
    return create_success_response(
        user.safe_dict(), message="Password changed successfully"
    )


@router.post("/password/reset/request", summary="Request password reset")
async def request_reset(email_data: PasswordReset, db: Session = Depends(get_db)):
    """
    Request password reset.

    Requests a password reset token for the provided email address.
    A password reset email will be sent if the email is associated with an account.

    - **email**: Email of the account to reset password for
    """
    # This service function returns None if email not found (security by obscurity)
    request_password_reset(db, email_data.email)

    # Always return success to prevent user enumeration
    return create_success_response(
        data={"message": "If the email exists, a password reset token has been sent."},
        message="Password reset request processed",
    )


@router.post("/password/reset", response_model=UserResponse, summary="Reset password")
async def reset_user_password(
    reset_data: PasswordResetConfirm, db: Session = Depends(get_db)
):
    """
    Reset password with token.

    Resets the user's password using a valid password reset token.

    - **token**: Valid password reset token
    - **new_password**: New password to set
    """
    user = reset_password(db, reset_data.token, reset_data.new_password)
    # FIX: Use safe_dict() to serialize the User model
    return create_success_response(
        user.safe_dict(), message="Password reset successfully"
    )


@router.post(
    "/email/verify", response_model=UserResponse, summary="Verify email address"
)
async def verify_email_endpoint(
    verification_data: EmailVerification, db: Session = Depends(get_db)
):
    """
    Verify email address with token.

    Verifies the user's email address using a valid verification token.

    - **token**: Valid email verification token
    """
    user = verify_email(db, verification_data.token)
    # FIX: Use safe_dict() to serialize the User model
    return create_success_response(
        user.safe_dict(), message="Email verified successfully"
    )
