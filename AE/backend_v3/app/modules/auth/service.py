"""
Authentication service module.

This module provides the core authentication functionality including user registration,
login, token management, password changes, and account management operations.
It implements the BaseUserAuthentication class to integrate with the fastcore security system.
"""

from fastcore.errors.exceptions import (
    ConflictError,
    ForbiddenError,
    InvalidCredentialsError,
    NotFoundError,
)
from fastcore.schemas.response.token import TokenResponse
from fastcore.security.password import get_password_hash, verify_password
from fastcore.security.tokens.service import (
    create_token_pair,
    decode_token,
    refresh_access_token,
    revoke_all_tokens_for_user,
    revoke_token,
)
from fastcore.security.users import BaseUserAuthentication

from .models import User
from .repository import UserRepository
from .schemas import PasswordChange, UserCreate, UserLogin, UserResponse, UserUpdate

# fastcore.security.tokens.service includes create_token, create_access_token, create_refresh_token,
# create_token_pair, validate_token, refresh_access_token, revoke_token

# fastcore.errors.exceptions includes InvalidTokenError, ExpiredTokenError, RevokedTokenError,
# InvalidCredentialsError

# fastcore.errors.exceptions includes AppError, ValidationError, NotFoundError, UnauthorizedError,
# ForbiddenError, ConflictError, BadRequestError, DBErrors


class AuthService(BaseUserAuthentication[User]):
    """
    Authentication service handling user authentication and management.

    This service provides methods for user registration, login, token management,
    user profile updates, password changes, and account deletion.

    Args:
        session: The database session used for database operations.
    """

    def __init__(self, session):
        self.repo = UserRepository(session)

    # --- For fastcore security module (Must to use it) ---
    async def authenticate(self, credentials) -> User | None:
        """
        Authenticate a user with username and password.

        Args:
            credentials (dict): Dictionary containing 'username' and 'password'.

        Returns:
            User | None: The authenticated user object if successful, None otherwise.
        """
        user = await self.repo.get_by_username(credentials["username"])
        if user and verify_password(credentials["password"], user.hashed_password):
            return user
        return None

    async def get_user_by_id(self, user_id) -> User:
        """
        Get a user by their ID.

        Args:
            user_id (int): The user's unique identifier.

        Returns:
            User: The user object.
        """
        return await self.repo.get_by_id(user_id)

    def get_user_id(self, user) -> int:
        """
        Extract the user ID from a user object.

        Args:
            user (User): The user object.

        Returns:
            int: The user's ID.
        """
        return user.id

    # --- Other necessary methods ---

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.

        Args:
            user_data (UserCreate): The user registration data.

        Returns:
            UserResponse: The newly created user.

        Raises:
            ConflictError: If a user with the same username or email already exists.
        """

        existing_user = await self.repo.get_by_username_or_email(
            username=user_data.username, email=user_data.email
        )

        if existing_user:
            raise ConflictError(
                message="User with this username or email already exists."
            )

        # Create a new user
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = get_password_hash(user_data.password)

        # Save the user to the database
        new_user = await self.repo.create(user_dict)
        await self.repo.session.commit()
        await self.repo.session.refresh(new_user)

        return UserResponse(**new_user.safe_dict())

    async def login_user(self, credentials: UserLogin) -> TokenResponse:
        """
        Login a user and return authentication tokens.

        Args:
            credentials (UserLogin): The user login credentials.

        Returns:
            TokenResponse: Object containing access and refresh tokens.

        Raises:
            InvalidCredentialsError: If the username or password is incorrect.
            ForbiddenError: If the user account is inactive or locked.
        """

        user = await self.repo.get_by_username(credentials.username)

        if not user or not verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsError(message="Invalid username or password.")
        if not user.is_active or user.is_locked:
            raise ForbiddenError(message="User account is inactive or locked.")

        # tokens = await self.create_token_pair(user.id)

        # return UserResponseWithTokens(**user.safe_dict(), tokens=tokens)
        return TokenResponse(**await self.create_token_pair(user.id))

    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate,  # dont allow to update password
    ) -> UserResponse:
        """
        Update user details.

        Args:
            user_id (int): The ID of the user to update.
            user_update (UserUpdate): The user data to update.

        Returns:
            UserResponse: The updated user.

        Raises:
            NotFoundError: If the user is not found.
        """

        user = await self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError(message="User not found.")

        update_data = user_update.model_dump(exclude_unset=True)

        user = await self.repo.update(user_id, update_data)
        await self.repo.session.commit()
        await self.repo.session.refresh(user)

        return UserResponse(**user.safe_dict())

    async def change_password(
        self,
        user_id: int,
        password_data: PasswordChange,
    ) -> None:
        """
        Change user password.

        Args:
            user_id (int): The ID of the user.
            password_data (PasswordChange): The password change data containing current and new passwords.

        Raises:
            NotFoundError: If the user is not found.
            InvalidCredentialsError: If the current password is incorrect.
        """

        user = await self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError(message="User not found.")
        if not verify_password(password_data.current_password, user.hashed_password):
            raise InvalidCredentialsError(message="Current password is incorrect.")

        # new_hashed_password = get_password_hash(password_data.password)
        # user.hashed_password = new_hashed_password

        # await self.repo.session.commit()
        # await self.repo.session.refresh(user)

        await self.repo.update_password(user, password_data.password)
        await self.repo.session.commit()
        await self.repo.session.refresh(user)

    async def delete_user(self, user_id: int) -> None:
        """
        Delete a user.

        Args:
            user_id (int): The ID of the user to delete.

        Raises:
            NotFoundError: If the user is not found.
        """

        user = await self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError(message="User not found.")

        await revoke_all_tokens_for_user(user_id, self.repo.session)

        await self.repo.delete(user_id)
        await self.repo.session.commit()

    async def logout_user(self, token: str) -> None:
        """
        Logout a user by revoking the token.

        Args:
            token (str): The JWT token to revoke.
        """

        await revoke_token(token, self.repo.session)

    async def logout_all_user_sessions(self, user_id: int) -> None:
        """
        Logout all tokens for a user.

        Args:
            user_id (int): The ID of the user.

        Raises:
            NotFoundError: If the user is not found.
        """

        user = await self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError(message="User not found.")

        await revoke_all_tokens_for_user(user_id, self.repo.session)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh the access token using the refresh token.

        Args:
            refresh_token (str): The refresh token.

        Returns:
            TokenResponse: Object containing new access and refresh tokens.

        Raises:
            NotFoundError: If the user is not found.
            ForbiddenError: If the user account is inactive or locked.
        """

        # This will raise if the token is invalid/expired/revoked
        await refresh_access_token(refresh_token, self.repo.session)

        payload = decode_token(refresh_token)
        user_id = payload.get("sub")

        user = await self.repo.get_by_id(int(user_id))

        if not user:
            raise NotFoundError(message="User not found.")
        if not user.is_active or user.is_locked:
            raise ForbiddenError(message="User account is inactive or locked.")

        # tokens = await self.create_token_pair(user.id)

        # return UserResponseWithTokens(**user.safe_dict(), tokens=tokens)
        return TokenResponse(**await self.create_token_pair(user.id))

    async def create_token_pair(self, user_id: int) -> dict:
        """
        Create a new token pair (access and refresh tokens) for the user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: Dictionary containing access_token and refresh_token.
        """

        return await create_token_pair({"sub": str(user_id)}, self.repo.session)
