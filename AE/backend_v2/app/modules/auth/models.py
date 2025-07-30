import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"
    # Future enhancement:
    # MODERATOR = "moderator"


class User(BaseModel):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_locked = Column(
        Boolean, default=False, nullable=False
    )  # Add this field for account locking

    # Relations
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

    # Add helpful property methods
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN

    # Consider adding a safe_dict method for serialization without sensitive data
    def safe_dict(self) -> dict:
        """Return user data without sensitive information."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_locked": self.is_locked,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TokenType(str, enum.Enum):
    """Token type enumeration."""

    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    VERIFY_EMAIL = "verify_email"


class Token(BaseModel):
    """Token model for storing JWT tokens."""

    __tablename__ = "tokens"

    token = Column(String(255), index=True, nullable=False)
    token_type = Column(Enum(TokenType), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Foreign keys
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relations
    user = relationship("User", back_populates="tokens")

    def __repr__(self):
        return f"<Token {self.token_type} for user {self.user_id}>"

    @property
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        # Make sure expires_at is timezone-aware before comparison
        if self.expires_at.tzinfo is None:
            # If the database returns naive datetimes, make them timezone-aware
            expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = self.expires_at

        return datetime.now(timezone.utc) > expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the token is valid."""
        return not self.is_revoked and not self.is_expired
