"""
API router for authentication endpoints.

Defines HTTP endpoints for user registration, login, logout, token refresh, profile management, and password change.
"""

from fastapi import APIRouter, Depends, Request, Response
from fastcore.errors.exceptions import InvalidTokenError
from fastcore.schemas.response import DataResponse, TokenResponse

from .dependencies import get_auth_service, get_current_user
from .schemas import (
    PasswordChange,
    RefreshToken,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from .service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=DataResponse[UserResponse])
async def register_user(
    user_data: UserCreate, service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.

    Args:
        user_data (UserCreate): The user creation data.
        service (AuthService): The authentication service dependency.

    Returns:
        DataResponse[UserResponse]: The created user response.
    """
    user = await service.register_user(user_data)
    return DataResponse(data=user, message="User registered successfully")


@router.post("/login", response_model=DataResponse[TokenResponse])
async def login_user(
    credentials: UserLogin,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """
    Login a user and return authentication tokens.

    Args:
        credentials (UserLogin): The user's login credentials.
        service (AuthService): The authentication service dependency.

    Returns:
        DataResponse[TokenResponse]: The authentication token response.
    """

    tokens = await service.login_user(credentials)

    # Set the access token in the response cookie (HTTPOnly)
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=False,  # TODO: Set to True in production
        samesite="Strict",
        max_age=tokens.access_expires_in,
    )

    return DataResponse(data=tokens, message="Login successful")


@router.post("/logout", response_model=DataResponse[None])
async def logout_user(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
    # user: UserResponse = Depends(get_current_user),
):
    """
    Logout the current user by revoking the current token.

    Args:
        request (Request): The HTTP request object.
        service (AuthService): The authentication service dependency.
        user (UserResponse): The current user dependency.

    Returns:
        DataResponse[None]: Success message.
    """
    token = request.headers.get("authorization", "").replace("Bearer ", "")

    try:
        await service.logout_user(token)
    except InvalidTokenError as e:
        # Pass the error silently if the token is invalid
        # This is to ensure that the logout process does not fail
        # even if the token is already invalid or expired
        # and the user is logged out
        # without any issues.
        pass

    # Clear the access token cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # TODO: Set to True in production
        samesite="Strict",
    )

    return DataResponse(data=None, message="Logged out successfully")


@router.post("/logout-all", response_model=DataResponse[None])
async def logout_all_user_sessions(
    response: Response,
    service: AuthService = Depends(get_auth_service),
    user: UserResponse = Depends(get_current_user),
):
    """
    Logout all sessions for the current user by revoking all tokens.

    Args:
        service (AuthService): The authentication service dependency.
        user (UserResponse): The current user dependency.

    Returns:
        DataResponse[None]: Success message.
    """
    await service.logout_all_user_sessions(user.id)

    # Clear the access token cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # TODO: Set to True in production
        samesite="Strict",
    )

    return DataResponse(data=None, message="All sessions logged out successfully")


@router.post("/refresh", response_model=DataResponse[TokenResponse])
async def refresh_token(
    body: RefreshToken,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """
    Refresh the access token using the refresh token.

    Args:
        body (RefreshToken): The refresh token data.
        service (AuthService): The authentication service dependency.

    Returns:
        TokenResponse: The new authentication token response.
    """
    tokens = await service.refresh_token(body.refresh_token)

    # Set the new access token in the response cookie (HTTPOnly)
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=False,  # TODO: Set to True in production
        samesite="Strict",
        max_age=tokens.access_expires_in,
    )

    return DataResponse(data=tokens, message="Token refreshed successfully")


@router.get("/me", response_model=DataResponse[UserResponse])
async def get_me(user: UserResponse = Depends(get_current_user)):
    """
    Get the current user's profile information.

    Args:
        user (UserResponse): The current user dependency.

    Returns:
        DataResponse[UserResponse]: The user profile response.
    """
    return DataResponse(data=user, message="User profile fetched successfully")


@router.patch("/me", response_model=DataResponse[UserResponse])
async def update_me(
    user_update: UserUpdate,
    service: AuthService = Depends(get_auth_service),
    user: UserResponse = Depends(get_current_user),
):
    """
    Update the current user's profile information.

    Args:
        user_update (UserUpdate): The update data.
        service (AuthService): The authentication service dependency.
        user (UserResponse): The current user dependency.

    Returns:
        DataResponse[UserResponse]: The updated user profile response.
    """
    updated_user = await service.update_user(user.id, user_update)
    return DataResponse(data=updated_user, message="User profile updated successfully")


@router.post("/change-password", response_model=DataResponse[None])
async def change_password(
    password_data: PasswordChange,
    service: AuthService = Depends(get_auth_service),
    user: UserResponse = Depends(get_current_user),
):
    """
    Change the current user's password.

    Args:
        password_data (PasswordChange): The password change data.
        service (AuthService): The authentication service dependency.
        user (UserResponse): The current user dependency.

    Returns:
        DataResponse[None]: Success message.
    """
    await service.change_password(user.id, password_data)
    return DataResponse(data=None, message="Password changed successfully")


@router.delete("/me", response_model=DataResponse[None])
async def delete_me(
    service: AuthService = Depends(get_auth_service),
    user: UserResponse = Depends(get_current_user),
):
    """
    Delete the current user account.

    Args:
        service (AuthService): The authentication service dependency.
        user (UserResponse): The current user dependency.

    Returns:
        DataResponse[None]: Success message.
    """
    await service.delete_user(user.id)
    return DataResponse(data=None, message="User deleted successfully")
