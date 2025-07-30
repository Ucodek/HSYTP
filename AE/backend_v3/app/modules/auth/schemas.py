"""
Pydantic schemas for the authentication module.

Defines request and response models for user operations and validation logic.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def validate_password_strength(password: str) -> str:
    """
    Validate password strength with consistent rules.

    Args:
        password (str): The password to validate.

    Returns:
        str: The validated password.

    Raises:
        ValueError: If password doesn't meet strength requirements.
    """
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")
    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must contain at least one special character")
    return password


class UserBase(BaseModel):
    """
    Base user schema with common fields.

    Attributes:
        email (EmailStr): User's email address.
        username (str): User's username.
        full_name (Optional[str]): Full name of the user.
        is_active (bool): Whether the user is active.
        is_verified (bool): Whether the user is verified.
        is_locked (bool): Whether the user is locked.
    """

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_locked: bool = False


class PasswordMixin(BaseModel):
    """
    Mixin for schemas that contain password validation.
    """

    @field_validator("password", check_fields=False)
    def password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided."""
        if v is None:
            return v
        return validate_password_strength(v)


class UserCreate(UserBase, PasswordMixin):
    """
    Schema for user creation.

    Attributes:
        password (str): The user's password.
    """

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(UserBase):
    """
    Schema for user update (partial updates allowed).
    """

    # Make all fields optional for partial updates
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_locked: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")


class UserResponse(UserBase):
    """
    Schema for user response.

    Attributes:
        id (int): User ID.
        created_at (Optional[datetime]): Creation timestamp.
        updated_at (Optional[datetime]): Last update timestamp.
    """

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Update to Pydantic v2 syntax
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """
    Schema for user login.

    Attributes:
        username (str): The user's username.
        password (str): The user's password.
    """

    username: str
    password: str


class PasswordChange(PasswordMixin):
    """
    Schema for password change request.

    Attributes:
        current_password (str): The user's current password.
        password (str): The new password.
    """

    current_password: str
    password: str = Field(..., min_length=8, max_length=100)


class RefreshToken(BaseModel):
    """
    Schema for refresh token request.

    Attributes:
        refresh_token (str): The refresh token.
    """

    refresh_token: str
    model_config = ConfigDict(from_attributes=True)
