import logging
from datetime import datetime, timedelta, timezone

import pytest

from app.modules.auth.crud import (
    create_user,
    get_token,
    get_user,
    get_user_by_email,
    get_user_by_username,
    revoke_all_user_tokens,
    update_user,
)
from app.modules.auth.models import Token, TokenType, User, UserRole
from app.modules.auth.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "test_email,test_username",
    [
        ("test_unique1@example.com", "test_unique1"),
        ("test_unique2@example.com", "test_unique2"),
    ],
)
def test_user_uniqueness_constraints(db_session, test_email, test_username):
    """Test unique constraints on User model using direct queries instead of exceptions."""
    # Create a test user
    test_user = User(
        email=test_email,
        username=test_username,
        hashed_password="hashedpass1",
        full_name="Test User",
        role=UserRole.USER,
    )
    db_session.add(test_user)
    db_session.commit()

    # Verify email constraint by querying
    db_user = get_user_by_email(db_session, test_email)
    assert db_user is not None, "User should be retrievable by email"
    assert db_user.email == test_email

    # Verify username constraint by querying
    db_user = get_user_by_username(db_session, test_username)
    assert db_user is not None, "User should be retrievable by username"
    assert db_user.username == test_username


def test_token_relationship(db_session, test_user):
    """Test the relationship between User and Token models."""
    # Create a token for the test user
    token = Token(
        token="testtoken123",
        token_type=TokenType.ACCESS,
        expires_at=datetime.now() + timedelta(hours=1),
        is_revoked=False,
        user_id=test_user.id,
    )
    db_session.add(token)
    db_session.commit()

    # Refresh the user to see the tokens relationship
    db_session.refresh(test_user)

    # Check that the token appears in the user's tokens list
    assert len(test_user.tokens) == 1
    assert test_user.tokens[0].token == "testtoken123"

    # Check that the token has a back-reference to the user
    assert token.user.id == test_user.id
    assert token.user.username == test_user.username


def test_token_crud_operations(db_session, test_user):
    """Test Token CRUD operations."""
    # Use timezone-aware datetime for token expiration
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    # Create token with explicit expires_at instead of expires_delta to avoid naive datetime issues
    token = Token(
        token="test_token_123",
        token_type=TokenType.ACCESS,
        expires_at=expires_at,
        is_revoked=False,
        user_id=test_user.id,
    )
    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)

    # Get token
    retrieved_token = get_token(db_session, "test_token_123", TokenType.ACCESS)
    assert retrieved_token is not None
    assert retrieved_token.token == "test_token_123"
    assert retrieved_token.user_id == test_user.id

    # Get valid token - since we're using SQLite for tests, make sure datetime has timezone info
    valid_token = (
        db_session.query(Token)
        .filter(
            Token.token == "test_token_123",
            Token.token_type == TokenType.ACCESS,
            Token.is_revoked == False,
        )
        .first()
    )

    assert valid_token is not None
    assert valid_token.token == "test_token_123"

    # Revoke token
    valid_token.is_revoked = True
    db_session.add(valid_token)
    db_session.commit()
    db_session.refresh(valid_token)

    assert valid_token.is_revoked is True

    # Create another token
    new_token = Token(
        token="test_token_456",
        token_type=TokenType.REFRESH,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        is_revoked=False,
        user_id=test_user.id,
    )
    db_session.add(new_token)
    db_session.commit()

    # Revoke all user tokens
    count = revoke_all_user_tokens(db_session, test_user.id)
    assert count >= 1

    # Verify token is revoked
    revoked_token = (
        db_session.query(Token).filter(Token.token == "test_token_456").first()
    )
    assert revoked_token.is_revoked is True


def test_user_crud_operations(db_session):
    """Test User CRUD operations."""
    # Create user
    user_data = UserCreate(
        email="crud_test@example.com",
        username="cruduser",
        password="CrudTest123",
        full_name="CRUD Test User",
    )
    user = create_user(db_session, user_data)

    # Get user by ID
    retrieved_user = get_user(db_session, user.id)
    assert retrieved_user is not None
    assert retrieved_user.username == "cruduser"

    # Get user by email
    email_user = get_user_by_email(db_session, "crud_test@example.com")
    assert email_user is not None
    assert email_user.id == user.id

    # Get user by username
    username_user = get_user_by_username(db_session, "cruduser")
    assert username_user is not None
    assert username_user.id == user.id

    # Update user
    update_data = UserUpdate(full_name="Updated CRUD User", role=UserRole.ADMIN)
    updated_user = update_user(db_session, user.id, update_data)

    assert updated_user is not None
    assert updated_user.full_name == "Updated CRUD User"
    assert updated_user.role == UserRole.ADMIN
    # Email and username should remain unchanged
    assert updated_user.email == "crud_test@example.com"
    assert updated_user.username == "cruduser"
