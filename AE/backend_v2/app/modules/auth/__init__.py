"""
Authentication module for user management, authentication and authorization.

This module provides:
- User registration and management
- JWT-based authentication
- Token refresh and revocation
- Password reset functionality
- Email verification
- Role-based authorization
"""

# API router for app inclusion
from app.modules.auth.api import router as auth_router

# Core authentication dependencies
from app.modules.auth.dependencies import (
    CurrentActiveUser,
    CurrentAdminUser,
    CurrentUser,
    CurrentVerifiedUser,
    OptionalUser,
    get_current_active_user,
    get_current_admin_user,
    get_current_user,
    get_current_verified_user,
    optional_current_user,
)

# Models
from app.modules.auth.models import Token, TokenType, User, UserRole

# Schemas for external use
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

# Key service functions that might be needed by other modules
from app.modules.auth.service import (
    login_user,
    logout_user,
    refresh_tokens,
    register_user,
)

__all__ = [
    # Models
    "User",
    "Token",
    "UserRole",
    "TokenType",
    # Dependencies and dependency types
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_current_admin_user",
    "optional_current_user",
    "CurrentUser",
    "CurrentActiveUser",
    "CurrentVerifiedUser",
    "CurrentAdminUser",
    "OptionalUser",
    # Schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "Login",
    "RefreshToken",
    "TokenPair",
    "PasswordReset",
    "PasswordResetConfirm",
    "PasswordChange",
    "EmailVerification",
    # Service functions
    "register_user",
    "login_user",
    "logout_user",
    "refresh_tokens",
    # Router
    "auth_router",
]
