"""
Repository layer for the authentication module.

Provides database access methods for user-related operations.
"""

from functools import wraps
from typing import Any, Callable, TypeVar

from fastcore.db import BaseRepository
from fastcore.errors.exceptions import DBError
from fastcore.logging.manager import ensure_logger
from fastcore.security.password import get_password_hash

# TokenRepository includes get_by_token_id, get_by_user_id, get_refresh_token_for_user
# revoke_token_for_user, revoke_all_for_user
from fastcore.security.tokens.repository import TokenRepository
from sqlalchemy import select

from .models import User

# Configure logger
logger = ensure_logger(None, __name__)

# Type variables for generic function decorators
R = TypeVar("R")


def db_error_handler(func: Callable[..., R]) -> Callable[..., R]:
    """
    Decorator to handle database errors consistently.

    This decorator wraps repository methods to provide consistent error
    handling and logging without duplicating try-except blocks.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> R:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            method_name = func.__name__
            logger.error(f"Error in {method_name}: {e}")
            raise DBError(message=str(e))

    return wrapper


class UserRepository(BaseRepository[User]):
    """
    Repository for user-related database operations.
    """

    def __init__(self, session):
        """
        Initialize the UserRepository with a database session.

        Args:
            session: The database session to use for operations.
        """
        super().__init__(User, session)

    @db_error_handler
    async def get_by_username(self, username: str) -> User | None:
        """
        Get a user by username.

        Args:
            username (str): The username to search for.

        Returns:
            User | None: The user object if found, else None.
        """
        stmt = select(self.model).where(self.model.username == username)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    @db_error_handler
    async def get_by_email(self, email: str) -> User | None:
        """
        Get a user by email.

        Args:
            email (str): The email to search for.

        Returns:
            User | None: The user object if found, else None.
        """
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    @db_error_handler
    async def get_by_username_or_email(
        self, username: str | None = None, email: str | None = None
    ) -> User | None:
        """
        Get a user by username or email.

        Args:
            username (str | None): The username to search for.
            email (str | None): The email to search for.

        Returns:
            User | None: The user object if found, else None.
        """
        stmt = select(self.model).where(
            (self.model.username == username) | (self.model.email == email)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    @db_error_handler
    async def update_password(self, user: User, new_password: str) -> None:
        """
        Update the password of a user and revoke all tokens.

        Args:
            user (User): The user object.
            new_password (str): The new password.
        """
        # Hash the new password
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password

        # revoke all tokens for the user
        token_repo = TokenRepository(self.session)
        await token_repo.revoke_all_for_user(user.id)

        # Update the user password
        # await self.session.commit()
