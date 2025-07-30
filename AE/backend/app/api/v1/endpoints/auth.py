from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.tokens import token as token_crud
from app.crud.users import user as user_crud
from app.models.users import User
from app.schemas.base import DataResponse
from app.schemas.users import Token, TokenRefresh, User as UserSchema, UserCreate
from app.utils.response import create_response

router = APIRouter()


@router.post("/login", response_model=DataResponse[Token])
async def login(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    # Create refresh token using the token CRUD
    refresh_token = await token_crud.create_refresh_token(db, user_id=user.id)

    return create_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token.token,
            "token_type": "bearer",
        }
    )


@router.post("/refresh", response_model=DataResponse[Token])
async def refresh_token(
    db: AsyncSession = Depends(get_db), token_data: TokenRefresh = Body(...)
) -> Any:
    """
    Get a new access token using refresh token.
    """
    # Get the refresh token from the database using the token CRUD
    token = await token_crud.get_by_token(db, token=token_data.refresh_token)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Check if token is revoked
    if token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    # Check if token is expired - Use timezone-aware datetimes
    current_time = datetime.now(timezone.utc)

    if token.expires_at < current_time:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired"
        )

    # Revoke the current refresh token
    await token_crud.revoke(db, token_id=token.id)

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=token.user_id, expires_delta=access_token_expires
    )

    # Create new refresh token
    new_refresh_token = await token_crud.create_refresh_token(db, user_id=token.user_id)

    return create_response(
        data={
            "access_token": access_token,
            "refresh_token": new_refresh_token.token,
            "token_type": "bearer",
        }
    )


@router.post("/logout", response_model=DataResponse[dict])
async def logout(
    db: AsyncSession = Depends(get_db),
    token_data: TokenRefresh = Body(...),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Logout a user by revoking their refresh token.
    """
    # Get the refresh token from the database
    token = await token_crud.get_by_token(db, token=token_data.refresh_token)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    # Check if the token belongs to the current user
    if token.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to revoke this token",
        )

    # Revoke the token
    await token_crud.revoke(db, token_id=token.id)

    return create_response(data={"detail": "Successfully logged out"})


@router.post("/logout-all", response_model=DataResponse[dict])
async def logout_all(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout a user from all devices by revoking all their refresh tokens.
    """
    await token_crud.revoke_by_user(db, user_id=current_user.id)
    return create_response(data={"detail": "Successfully logged out from all devices"})


@router.post("/register", response_model=DataResponse[UserSchema])
async def register(
    *, db: AsyncSession = Depends(get_db), user_in: UserCreate = Body(...)
) -> Any:
    """
    Register a new user.
    """
    # Check if user already exists
    user_exists = await user_crud.get_by_email(db, email=user_in.email)
    if user_exists:
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )

    # Create new user
    user = await user_crud.create(db, obj_in=user_in)

    return create_response(data=user)


@router.get("/me", response_model=DataResponse[UserSchema])
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user.
    """
    return create_response(data=current_user)
