from unittest.mock import patch

import pytest

from app.errors.exceptions import AuthenticationError, ValidationError
from app.modules.auth.crud import get_token
from app.modules.auth.models import TokenType
from app.modules.auth.schemas import UserCreate, UserUpdate
from app.modules.auth.service import (
    change_user_password,
    generate_email_verification_token,
    generate_token_pair,
    login_user,
    logout_user,
    refresh_tokens,
    register_user,
    request_password_reset,
    reset_password,
    update_user_profile,
    verify_email,
)


def test_register_user_success(db_session):
    """Test successful user registration."""
    user_data = UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="Password123",
        full_name="New User",
    )

    user = register_user(db_session, user_data)

    assert user is not None
    assert user.email == "newuser@example.com"
    assert user.username == "newuser"
    assert user.full_name == "New User"
    assert hasattr(user, "hashed_password")
    assert user.hashed_password != "Password123"  # Password should be hashed


def test_register_user_duplicate_email(db_session, test_user):
    """Test registration with duplicate email."""
    user_data = UserCreate(
        email=test_user.email,  # Use existing email
        username="uniqueusername",
        password="Password123",
        full_name="Another User",
    )

    with pytest.raises(ValidationError) as excinfo:
        register_user(db_session, user_data)

    assert "Email already registered" in str(excinfo.value.detail)


def test_register_user_duplicate_username(db_session, test_user):
    """Test registration with duplicate username."""
    user_data = UserCreate(
        email="unique@example.com",
        username=test_user.username,  # Use existing username
        password="Password123",
        full_name="Another User",
    )

    with pytest.raises(ValidationError) as excinfo:
        register_user(db_session, user_data)

    assert "Username already registered" in str(excinfo.value.detail)


def test_login_user_success(db_session, test_user):
    """Test successful login."""
    user, token_pair = login_user(db_session, test_user.username, "Password123")

    assert user.id == test_user.id
    assert token_pair.access_token is not None
    assert token_pair.refresh_token is not None
    assert token_pair.token_type == "bearer"


def test_login_user_with_email(db_session, test_user):
    """Test login with email instead of username."""
    user, token_pair = login_user(db_session, test_user.email, "Password123")

    assert user.id == test_user.id
    assert token_pair.access_token is not None


def test_login_user_invalid_credentials(db_session, test_user):
    """Test login with invalid credentials."""
    with pytest.raises(AuthenticationError) as excinfo:
        login_user(db_session, test_user.username, "WrongPassword")

    assert "Invalid username or password" in str(excinfo.value.detail)


def test_login_user_inactive_account(db_session, test_user):
    """Test login with inactive account."""
    # Set user to inactive
    test_user.is_active = False
    db_session.add(test_user)
    db_session.commit()

    with pytest.raises(AuthenticationError) as excinfo:
        login_user(db_session, test_user.username, "Password123")

    assert "User account is inactive" in str(excinfo.value.detail)

    # Reset user to active for other tests
    test_user.is_active = True
    db_session.add(test_user)
    db_session.commit()


def test_update_user_profile(db_session, test_user):
    """Test updating user profile."""
    update_data = UserUpdate(full_name="Updated Full Name", username="updatedusername")

    updated_user = update_user_profile(db_session, test_user.id, update_data)

    assert updated_user.full_name == "Updated Full Name"
    assert updated_user.username == "updatedusername"
    # Email should remain unchanged
    assert updated_user.email == test_user.email


def test_change_user_password(db_session, test_user):
    """Test changing user password."""
    updated_user = change_user_password(
        db_session,
        test_user.id,
        "Password123",  # Current password
        "NewPassword123",  # New password
    )

    assert updated_user.id == test_user.id

    # Try logging in with new password
    user, _ = login_user(db_session, updated_user.username, "NewPassword123")
    assert user.id == test_user.id

    # Try logging in with old password (should fail)
    with pytest.raises(AuthenticationError):
        login_user(db_session, updated_user.username, "Password123")


# Password Reset Tests
def test_request_password_reset_existing_email(db_session, test_user):
    """Test requesting password reset for an existing email."""
    result = request_password_reset(db_session, test_user.email)

    # Should return a token string
    assert result is not None
    assert isinstance(result, str)

    # Token should be in db and associated with the user
    tokens = [
        t
        for t in test_user.tokens
        if t.token_type == TokenType.RESET_PASSWORD and not t.is_revoked
    ]
    assert len(tokens) > 0


def test_request_password_reset_non_existent_email(db_session):
    """Test requesting password reset for a non-existent email."""
    non_existent_email = "nonexistent@example.com"

    # Should return None for non-existent email (to prevent user enumeration)
    result = request_password_reset(db_session, non_existent_email)
    assert result is None


def test_reset_password_valid_token(db_session, test_user):
    """Test resetting password with a valid reset token."""
    # First request a reset token
    token = request_password_reset(db_session, test_user.email)
    assert token is not None

    # Now reset the password
    new_password = "NewValidPassword123"
    user = reset_password(db_session, token, new_password)

    # Verify the user was returned and updated
    assert user is not None
    assert user.id == test_user.id

    # Verify we can login with the new password
    login_user_result, _ = login_user(db_session, test_user.username, new_password)
    assert login_user_result.id == test_user.id

    # Verify we can't login with the old password
    with pytest.raises(AuthenticationError):
        login_user(db_session, test_user.username, "Password123")


def test_reset_password_invalid_token(db_session):
    """Test resetting password with an invalid token."""
    invalid_token = "invalid-token-that-doesnt-exist"

    # Should raise AuthenticationError
    with pytest.raises(AuthenticationError) as excinfo:
        reset_password(db_session, invalid_token, "NewValidPassword123")

    assert "Invalid reset token" in str(excinfo.value.detail)


def test_reset_password_revoked_token(db_session, test_user):
    """Test resetting password with a revoked token."""
    # First request a reset token
    token = request_password_reset(db_session, test_user.email)
    assert token is not None

    # Reset password once (which should revoke the token)
    reset_password(db_session, token, "NewValidPassword123")

    # Try to use the same token again
    with pytest.raises(AuthenticationError) as excinfo:
        reset_password(db_session, token, "AnotherPassword123")

    assert "Reset token has been revoked" in str(excinfo.value.detail)


@patch("app.modules.auth.service.get_valid_token")
def test_reset_password_expired_token(mock_get_valid_token, db_session):
    """Test resetting password with an expired token."""
    # Setup the mock to simulate an expired token
    mock_get_valid_token.return_value = None

    with pytest.raises(AuthenticationError) as excinfo:
        reset_password(db_session, "expired-token", "NewValidPassword123")

    assert "Invalid reset token" in str(excinfo.value.detail)


# Email Verification Tests
def test_verify_email_valid_token(db_session, test_user):
    """Test verifying email with a valid token."""
    # Setup: Ensure the user is not verified and create a verification token
    test_user.is_verified = False
    db_session.add(test_user)
    db_session.commit()

    # Generate verification token
    token = generate_email_verification_token(db_session, test_user.id)
    assert token is not None

    # Verify the email
    user = verify_email(db_session, token)

    # Assert the user is now verified
    assert user is not None
    assert user.id == test_user.id
    assert user.is_verified is True

    # Check that the token was revoked
    tokens = [t for t in test_user.tokens if t.token == token]
    assert all(t.is_revoked for t in tokens)


def test_verify_email_invalid_token(db_session):
    """Test verifying email with an invalid token."""
    invalid_token = "invalid-verification-token"

    # Should raise AuthenticationError
    with pytest.raises(AuthenticationError) as excinfo:
        verify_email(db_session, invalid_token)

    assert "Invalid verification token" in str(excinfo.value.detail)


def test_verify_email_revoked_token(db_session, test_user):
    """Test verifying email with a revoked token."""
    # Setup: Ensure the user is not verified and create a verification token
    test_user.is_verified = False
    db_session.add(test_user)
    db_session.commit()

    # Generate verification token
    token = generate_email_verification_token(db_session, test_user.id)

    # Use the token once
    verify_email(db_session, token)

    # Try to use the token again
    with pytest.raises(AuthenticationError) as excinfo:
        verify_email(db_session, token)

    assert "Verification token has been revoked" in str(excinfo.value.detail)


@patch("app.modules.auth.service.get_valid_token")
def test_verify_email_expired_token(mock_get_valid_token, db_session):
    """Test verifying email with an expired token."""
    # Setup the mock to simulate an expired token
    mock_get_valid_token.return_value = None

    with pytest.raises(AuthenticationError) as excinfo:
        verify_email(db_session, "expired-token")

    assert "Invalid verification token" in str(excinfo.value.detail)


# Token Management Tests
def test_generate_token_pair(db_session, test_user):
    """Test generating access and refresh token pair."""
    token_pair = generate_token_pair(db_session, test_user.id)

    # Check token structure
    assert token_pair.access_token is not None
    assert token_pair.refresh_token is not None
    assert token_pair.token_type == "bearer"

    # Verify tokens are stored in database
    tokens = test_user.tokens
    access_tokens = [
        t
        for t in tokens
        if t.token_type == TokenType.ACCESS and t.token == token_pair.access_token
    ]
    refresh_tokens = [
        t
        for t in tokens
        if t.token_type == TokenType.REFRESH and t.token == token_pair.refresh_token
    ]

    assert len(access_tokens) == 1
    assert len(refresh_tokens) == 1


def test_refresh_tokens_success(db_session, test_user):
    """Test successful token refresh."""
    # First generate a token pair
    initial_token_pair = generate_token_pair(db_session, test_user.id)

    # Then refresh using the refresh token
    new_token_pair = refresh_tokens(db_session, initial_token_pair.refresh_token)

    # Check that new tokens were generated
    assert new_token_pair.access_token is not None
    assert new_token_pair.refresh_token is not None
    assert new_token_pair.access_token != initial_token_pair.access_token
    assert new_token_pair.refresh_token != initial_token_pair.refresh_token

    # Verify old refresh token was revoked
    old_token = get_token(
        db_session, initial_token_pair.refresh_token, TokenType.REFRESH
    )
    assert old_token.is_revoked is True


def test_refresh_tokens_invalid_token(db_session):
    """Test refresh tokens with invalid refresh token."""
    invalid_token = "invalid-refresh-token"

    with pytest.raises(AuthenticationError) as excinfo:
        refresh_tokens(db_session, invalid_token)

    assert "Invalid refresh token" in str(excinfo.value.detail)


def test_logout_revokes_tokens(db_session, test_user):
    """Test that logout revokes all user tokens."""
    # Generate some tokens
    generate_token_pair(db_session, test_user.id)
    generate_token_pair(db_session, test_user.id)

    # Count tokens before logout
    active_tokens_before = [t for t in test_user.tokens if not t.is_revoked]
    assert len(active_tokens_before) > 0

    # Logout the user
    logout_user(db_session, test_user.id)

    # Check all tokens are revoked
    db_session.refresh(test_user)
    active_tokens_after = [t for t in test_user.tokens if not t.is_revoked]
    assert len(active_tokens_after) == 0
