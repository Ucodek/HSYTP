"""
Database models for the authentication module.

Defines ORM models for user authentication and authorization.
"""

from fastcore.db.base import BaseModel
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship


class User(BaseModel):
    """
    SQLAlchemy ORM model for application users.

    Attributes:
        email (str): User's email address (unique).
        username (str): User's username (unique).
        hashed_password (str): Hashed user password.
        full_name (str): Full name of the user.
        is_active (bool): Whether the user is active.
        is_verified (bool): Whether the user is verified.
        is_locked (bool): Whether the user is locked.
    """

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)

    # Relations
    tokens = relationship("Token", cascade="all, delete-orphan", back_populates="user")

    def __repr__(self):
        """Return a string representation of the user."""
        return f"<User {self.username}>"

    def safe_dict(self) -> dict:
        """
        Return a dictionary of safe user fields for API responses.

        Returns:
            dict: Dictionary of user fields safe for exposure.
        """
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_locked": self.is_locked,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
