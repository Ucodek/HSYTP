from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.crud import (
    authenticate_user,
    change_password,
    cleanup_expired_tokens,
    create_token,
    create_user,
    delete_user,
    get_active_tokens,
    get_token,
    get_user,
    get_user_by_email,
    get_user_by_email_or_username,
    get_user_by_username,
    get_users,
    get_valid_token,
    revoke_all_user_tokens,
    revoke_token,
    update_user,
)
from app.modules.auth.models import TokenType, User, UserRole
from app.modules.auth.schemas import UserCreate, UserUpdate


# User CRUD tests
def test_get_user(db_session: Session, test_user: User):
    """Test retrieving a user by ID."""
    # Act
    retrieved_user = get_user(db_session, test_user.id)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id
    assert retrieved_user.username == test_user.username
    assert retrieved_user.email == test_user.email


def test_get_user_not_found(db_session: Session):
    """Test retrieving a non-existent user."""
    # Act
    non_existent_user = get_user(db_session, 999999)

    # Assert
    assert non_existent_user is None


def test_get_user_by_email(db_session: Session, test_user: User):
    """Test retrieving a user by email."""
    # Act
    retrieved_user = get_user_by_email(db_session, test_user.email)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id


def test_get_user_by_username(db_session: Session, test_user: User):
    """Test retrieving a user by username."""
    # Act
    retrieved_user = get_user_by_username(db_session, test_user.username)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id


def test_get_user_by_email_or_username_with_email(db_session: Session, test_user: User):
    """Test retrieving a user by email using the combined lookup function."""
    # Act
    retrieved_user = get_user_by_email_or_username(db_session, test_user.email)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id


def test_get_user_by_email_or_username_with_username(
    db_session: Session, test_user: User
):
    """Test retrieving a user by username using the combined lookup function."""
    # Act
    retrieved_user = get_user_by_email_or_username(db_session, test_user.username)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id


def test_get_users_pagination(db_session: Session, test_user: User, test_admin: User):
    """Test retrieving users with pagination."""
    # Create a few more users for pagination testing
    for i in range(3):
        create_user(
            db_session,
            UserCreate(
                email=f"test{i}@example.com",
                username=f"testuser{i}",
                password="Password123",
                full_name=f"Test User {i}",
            ),
        )

    # Act - get first page
    users_page_1 = get_users(db_session, skip=0, limit=2)
    # Get second page
    users_page_2 = get_users(db_session, skip=2, limit=2)

    # Assert
    assert len(users_page_1) == 2
    assert len(users_page_2) == 2
    # Different users on different pages
    assert users_page_1[0].id != users_page_2[0].id
    assert users_page_1[1].id != users_page_2[1].id


def test_get_users_with_filters(db_session: Session, test_user: User, test_admin: User):
    """Test retrieving users with filters."""
    # Create inactive user
    inactive_user = User(
        email="inactive@example.com",
        username="inactiveuser",
        hashed_password="doesnotmatter",
        is_active=False,
        role=UserRole.USER,
    )
    db_session.add(inactive_user)
    db_session.commit()

    # Act
    active_users = get_users(db_session, is_active=True)
    inactive_users = get_users(db_session, is_active=False)
    admin_users = get_users(db_session, role=UserRole.ADMIN)

    # Assert
    assert len(active_users) >= 2  # At least test_user and test_admin
    assert all(user.is_active for user in active_users)

    assert len(inactive_users) == 1
    assert not inactive_users[0].is_active

    assert len(admin_users) == 1
    assert admin_users[0].role == UserRole.ADMIN


def test_create_user_success(db_session: Session):
    """Test successful user creation."""
    # Arrange
    user_data = UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="Password123",
        full_name="New User",
    )

    # Act
    created_user = create_user(db_session, user_data)

    # Assert
    assert created_user is not None
    assert created_user.email == "newuser@example.com"
    assert created_user.username == "newuser"
    assert created_user.full_name == "New User"
    # Password should be hashed
    assert created_user.hashed_password != "Password123"
    assert created_user.role == UserRole.USER


def test_create_user_duplicate_email(db_session: Session, test_user: User):
    """Test creating a user with duplicate email fails."""
    # Arrange
    user_data = UserCreate(
        email=test_user.email,  # Duplicate email
        username="uniqueusername",
        password="Password123",
        full_name="Another User",
    )

    # Act & Assert
    with pytest.raises(IntegrityError):
        create_user(db_session, user_data)
        db_session.flush()


def test_create_user_duplicate_username(db_session: Session, test_user: User):
    """Test creating a user with duplicate username fails."""
    # Arrange
    user_data = UserCreate(
        email="unique@example.com",
        username=test_user.username,  # Duplicate username
        password="Password123",
        full_name="Another User",
    )

    # Act & Assert
    with pytest.raises(IntegrityError):
        create_user(db_session, user_data)
        db_session.flush()


def test_update_user_success(db_session: Session, test_user: User):
    """Test successful user update."""
    # Arrange
    update_data = UserUpdate(
        full_name="Updated Name",
        is_active=True,
    )

    # Act
    updated_user = update_user(db_session, test_user.id, update_data)

    # Assert
    assert updated_user is not None
    assert updated_user.full_name == "Updated Name"
    # Other fields should remain unchanged
    assert updated_user.email == test_user.email
    assert updated_user.username == test_user.username


def test_update_user_with_password(db_session: Session, test_user: User):
    """Test updating user with password change."""
    # Arrange
    original_password_hash = test_user.hashed_password
    update_data = UserUpdate(
        password="NewPassword123",
    )

    # Act
    updated_user = update_user(db_session, test_user.id, update_data)

    # Assert
    assert updated_user is not None
    assert updated_user.hashed_password != original_password_hash
    # Authentication should work with new password
    assert (
        authenticate_user(db_session, test_user.username, "NewPassword123") is not None
    )


def test_update_user_with_duplicate_email(
    db_session: Session, test_user: User, test_admin: User
):
    """Test updating user with an email that belongs to another user."""
    # Arrange
    update_data = UserUpdate(
        email=test_admin.email,  # This email is already taken
    )

    # Act
    updated_user = update_user(db_session, test_user.id, update_data)

    # Assert
    assert updated_user is None  # Update should fail


def test_update_user_with_duplicate_username(
    db_session: Session, test_user: User, test_admin: User
):
    """Test updating user with a username that belongs to another user."""
    # Arrange
    update_data = UserUpdate(
        username=test_admin.username,  # This username is already taken
    )

    # Act
    updated_user = update_user(db_session, test_user.id, update_data)

    # Assert
    assert updated_user is None  # Update should fail


def test_delete_user(db_session: Session):
    """Test user deletion."""
    # Arrange
    user_data = UserCreate(
        email="todelete@example.com",
        username="userdelete",
        password="Password123",
        full_name="Delete Me",
    )
    user_to_delete = create_user(db_session, user_data)
    user_id = user_to_delete.id

    # Act
    result = delete_user(db_session, user_id)
    deleted_user = get_user(db_session, user_id)

    # Assert
    assert result is True
    assert deleted_user is None  # User should no longer exist


def test_delete_user_not_found(db_session: Session):
    """Test deleting a non-existent user."""
    # Act
    result = delete_user(db_session, 999999)

    # Assert
    assert result is False


def test_authenticate_user_success(db_session: Session, test_user: User):
    """Test successful user authentication."""
    # Act
    authenticated_user = authenticate_user(
        db_session, test_user.username, "Password123"
    )

    # Assert
    assert authenticated_user is not None
    assert authenticated_user.id == test_user.id


def test_authenticate_user_with_email(db_session: Session, test_user: User):
    """Test authentication using email instead of username."""
    # Act
    authenticated_user = authenticate_user(db_session, test_user.email, "Password123")

    # Assert
    assert authenticated_user is not None
    assert authenticated_user.id == test_user.id


def test_authenticate_user_wrong_password(db_session: Session, test_user: User):
    """Test authentication with incorrect password."""
    # Act
    authenticated_user = authenticate_user(
        db_session, test_user.username, "WrongPassword"
    )

    # Assert
    assert authenticated_user is None


def test_authenticate_user_nonexistent(db_session: Session):
    """Test authentication with non-existent user."""
    # Act
    authenticated_user = authenticate_user(db_session, "nonexistent", "Password123")

    # Assert
    assert authenticated_user is None


def test_change_password(db_session: Session, test_user: User):
    """Test changing user password."""
    # Arrange
    original_password_hash = test_user.hashed_password

    # Act
    updated_user = change_password(db_session, test_user, "NewPasswordXYZ123")

    # Assert
    assert updated_user is not None
    assert updated_user.hashed_password != original_password_hash
    # Authentication should work with new password
    assert (
        authenticate_user(db_session, test_user.username, "NewPasswordXYZ123")
        is not None
    )
    # Old password should no longer work
    assert authenticate_user(db_session, test_user.username, "Password123") is None


# Token CRUD tests
def test_create_token(db_session: Session, test_user: User):
    """Test creating a token."""
    # Act
    token_value = str(uuid4())
    token = create_token(
        db_session,
        test_user.id,
        token_value,
        TokenType.ACCESS,
        expires_delta=timedelta(hours=1),
    )

    # Assert
    assert token is not None
    assert token.token == token_value
    assert token.token_type == TokenType.ACCESS
    assert token.user_id == test_user.id
    assert token.is_revoked is False

    # Fix: Ensure both datetimes are timezone-aware for comparison
    # If token.expires_at is naive, make it timezone-aware
    expires_at = token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    # Now compare with a timezone-aware current time
    assert expires_at > datetime.now(timezone.utc)


def test_create_token_default_expiry(db_session: Session, test_user: User):
    """Test creating a token with default expiration based on token type."""
    # Act
    token_value = str(uuid4())
    token = create_token(
        db_session,
        test_user.id,
        token_value,
        TokenType.ACCESS,  # Should use default expiry for ACCESS tokens
    )

    # Assert
    assert token is not None

    # Fix: Make both datetimes timezone-aware for comparison
    # If token.expires_at is naive, make it timezone-aware
    expires_at = token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    # Default expiry for ACCESS should be around 30 minutes
    expected_expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
    # Allow 5 seconds margin for test execution
    assert abs((expires_at - expected_expiry).total_seconds()) < 5


def test_get_token(db_session: Session, test_user: User):
    """Test retrieving a token by value and type."""
    # Arrange
    token_value = str(uuid4())
    created_token = create_token(
        db_session, test_user.id, token_value, TokenType.REFRESH
    )

    # Act
    retrieved_token = get_token(db_session, token_value, TokenType.REFRESH)

    # Assert
    assert retrieved_token is not None
    assert retrieved_token.id == created_token.id
    assert retrieved_token.token == token_value


def test_get_token_not_found(db_session: Session):
    """Test retrieving a non-existent token."""
    # Act
    non_existent_token = get_token(db_session, "non-existent-token", TokenType.ACCESS)

    # Assert
    assert non_existent_token is None


def test_get_valid_token(db_session: Session, test_user: User):
    """Test retrieving a valid (non-expired, non-revoked) token."""
    # Arrange
    token_value = str(uuid4())
    # Create a valid token
    create_token(
        db_session,
        test_user.id,
        token_value,
        TokenType.REFRESH,
        expires_delta=timedelta(hours=1),
    )

    # Act
    valid_token = get_valid_token(db_session, token_value, TokenType.REFRESH)

    # Assert
    assert valid_token is not None
    assert valid_token.token == token_value
    assert valid_token.is_valid is True  # Should use the model's property


def test_get_valid_token_revoked(db_session: Session, test_user: User):
    """Test that a revoked token is not considered valid."""
    # Arrange
    token_value = str(uuid4())
    token = create_token(
        db_session,
        test_user.id,
        token_value,
        TokenType.REFRESH,
        expires_delta=timedelta(hours=1),
    )
    # Revoke the token
    token.is_revoked = True
    db_session.add(token)
    db_session.commit()

    # Act
    valid_token = get_valid_token(db_session, token_value, TokenType.REFRESH)

    # Assert
    assert valid_token is None  # Should not be found as it's revoked


def test_get_valid_token_expired(db_session: Session, test_user: User):
    """Test that an expired token is not considered valid."""
    # Arrange
    token_value = str(uuid4())
    # Create a token that's already expired
    expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    token = create_token(db_session, test_user.id, token_value, TokenType.REFRESH)
    token.expires_at = expires_at
    db_session.add(token)
    db_session.commit()

    # Act
    valid_token = get_valid_token(db_session, token_value, TokenType.REFRESH)

    # Assert
    assert valid_token is None  # Should not be found as it's expired


def test_revoke_token(db_session: Session, test_user: User):
    """Test revoking a token."""
    # Arrange
    token_value = str(uuid4())
    token = create_token(db_session, test_user.id, token_value, TokenType.REFRESH)

    # Act
    revoked_token = revoke_token(db_session, token)

    # Assert
    assert revoked_token.is_revoked is True

    # Verify token is actually revoked in database
    db_token = get_token(db_session, token_value, TokenType.REFRESH)
    assert db_token.is_revoked is True


def test_revoke_all_user_tokens(db_session: Session, test_user: User):
    """Test revoking all tokens for a user."""
    # Arrange - create multiple tokens for the user
    for _ in range(3):
        create_token(db_session, test_user.id, str(uuid4()), TokenType.ACCESS)
        create_token(db_session, test_user.id, str(uuid4()), TokenType.REFRESH)

    # Act
    revoked_count = revoke_all_user_tokens(db_session, test_user.id)

    # Assert
    assert revoked_count >= 6  # Should have revoked all 6 tokens

    # Check all tokens for user are revoked
    active_tokens = get_active_tokens(db_session, test_user.id)
    assert len(active_tokens) == 0


def test_revoke_all_user_tokens_specific_type(db_session: Session, test_user: User):
    """Test revoking all tokens of a specific type for a user."""
    # Arrange - create multiple tokens for the user
    for _ in range(2):
        create_token(db_session, test_user.id, str(uuid4()), TokenType.ACCESS)
        create_token(db_session, test_user.id, str(uuid4()), TokenType.REFRESH)

    # Act - revoke only REFRESH tokens
    revoked_count = revoke_all_user_tokens(db_session, test_user.id, TokenType.REFRESH)

    # Assert
    assert revoked_count >= 2  # Should have revoked 2 REFRESH tokens

    # Check ACCESS tokens still active, REFRESH tokens revoked
    active_access_tokens = get_active_tokens(db_session, test_user.id, TokenType.ACCESS)
    active_refresh_tokens = get_active_tokens(
        db_session, test_user.id, TokenType.REFRESH
    )
    assert len(active_access_tokens) >= 2
    assert len(active_refresh_tokens) == 0


def test_cleanup_expired_tokens(db_session: Session, test_user: User):
    """Test cleaning up expired tokens."""
    # Arrange
    # Create expired tokens
    expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
    token1 = create_token(db_session, test_user.id, str(uuid4()), TokenType.ACCESS)
    token2 = create_token(db_session, test_user.id, str(uuid4()), TokenType.REFRESH)
    token1.expires_at = expired_time
    token2.expires_at = expired_time
    db_session.add_all([token1, token2])
    db_session.commit()

    # Create active token
    create_token(
        db_session,
        test_user.id,
        str(uuid4()),
        TokenType.ACCESS,
        expires_delta=timedelta(hours=1),
    )

    # Act
    deleted_count = cleanup_expired_tokens(db_session)

    # Assert
    assert deleted_count >= 2  # Should have deleted 2 expired tokens

    # Check expired tokens are gone
    token1_exists = get_token(db_session, token1.token, TokenType.ACCESS)
    token2_exists = get_token(db_session, token2.token, TokenType.REFRESH)
    assert token1_exists is None
    assert token2_exists is None


def test_get_active_tokens(db_session: Session, test_user: User):
    """Test retrieving active tokens for a user."""
    # Arrange
    # Create active tokens
    active_tokens = []
    for _ in range(2):
        token = create_token(
            db_session,
            test_user.id,
            str(uuid4()),
            TokenType.ACCESS,
            expires_delta=timedelta(hours=1),
        )
        active_tokens.append(token)

    # Create revoked token
    revoked_token = create_token(
        db_session, test_user.id, str(uuid4()), TokenType.ACCESS
    )
    revoked_token.is_revoked = True
    db_session.add(revoked_token)

    # Create expired token
    expired_token = create_token(
        db_session, test_user.id, str(uuid4()), TokenType.ACCESS
    )

    # Use timezone-aware datetime for setting expiration
    expired_token.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db_session.add(expired_token)
    db_session.commit()

    # Act
    retrieved_active_tokens = get_active_tokens(db_session, test_user.id)

    # Assert
    assert len(retrieved_active_tokens) >= 2  # Should have at least 2 active tokens

    # All retrieved tokens should be active
    now = datetime.now(timezone.utc)
    for token in retrieved_active_tokens:
        assert token.is_revoked is False

        # Fix: Ensure both datetimes are timezone-aware for comparison
        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        assert expires_at > now
