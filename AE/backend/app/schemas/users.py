from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    is_active: Optional[bool] = True
    subscription_tier: Optional[str] = "basic"


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    def password_strength(cls, v):
        """Validate password strength."""
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserUpdate(BaseModel):
    """Schema for user update."""

    email: Optional[EmailStr] = None
    subscription_tier: Optional[str] = None
    password: Optional[str] = None

    @field_validator("password")
    def password_strength(cls, v):
        """Validate password strength if provided."""
        if v is None:
            return v

        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserInDBBase(UserBase):
    """Base schema for users stored in DB."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Updated from class Config


class User(UserInDBBase):
    """API response schema for users."""

    pass


class UserInDB(UserInDBBase):
    """Internal schema for users in DB including hashed password."""

    hashed_password: str


# Updated Token schemas
class Token(BaseModel):
    """Schema for access token."""

    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for token payload."""

    sub: Optional[int] = None
    exp: Optional[datetime] = None


class TokenRefresh(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str


class RefreshTokenCreate(BaseModel):
    """Schema for creating a refresh token."""

    token: str
    user_id: int
    expires_at: datetime


class RefreshTokenInDB(RefreshTokenCreate):
    """Schema for refresh token as stored in DB."""

    id: int
    created_at: datetime
    is_revoked: bool = False

    model_config = ConfigDict(from_attributes=True)  # Updated from class Config
