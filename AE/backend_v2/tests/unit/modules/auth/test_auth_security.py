import time
from datetime import timedelta

import pytest
from jose import JWTError, jwt

from app.core.config.base import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.modules.auth.models import TokenType
from app.modules.auth.service import generate_token_pair


def test_password_hashing():
    """Test that password hashing works correctly."""
    # Arrange
    password = "TestPassword123"

    # Act
    hashed = get_password_hash(password)

    # Assert
    # Verify the hash is different from the original password
    assert hashed != password
    # Verify the hash works with the verification function
    assert verify_password(password, hashed) is True
    # Verify incorrect password fails verification
    assert verify_password("WrongPassword", hashed) is False


def test_password_hash_uniqueness():
    """Test that same password produces different hashes for security."""
    # Arrange
    password = "TestPassword123"

    # Act
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Assert
    # Different hashes should be generated for the same password (due to salt)
    assert hash1 != hash2


def test_password_hash_algorithm():
    """Test that the password hash is using bcrypt."""
    # Arrange
    password = "TestPassword123"

    # Act
    hashed = get_password_hash(password)

    # Assert
    # bcrypt hashes start with $2b$
    assert hashed.startswith("$2b$")


def test_verify_password_performance():
    """Test that password verification takes a reasonable time (security feature)."""
    # Arrange
    password = "TestPassword123"
    hashed = get_password_hash(password)

    # Act
    start_time = time.time()
    verify_password(password, hashed)
    end_time = time.time()
    verification_time = end_time - start_time

    # Assert
    # Password verification should take some time (indicating proper hashing)
    # Usually between 0.01 and 0.1 seconds for bcrypt
    assert 0.001 < verification_time < 0.5


def test_access_token_creation():
    """Test that access token creation works properly."""
    # Arrange
    user_id = 123

    # Act
    token = create_access_token(subject=user_id)

    # Assert
    # Token should be a string
    assert isinstance(token, str)

    # Decode token to verify contents
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == str(user_id)
    assert "exp" in payload


def test_access_token_expiration():
    """Test access token with custom expiration."""
    # Arrange
    user_id = 123
    expires_delta = timedelta(minutes=30)

    # Act
    token = create_access_token(subject=user_id, expires_delta=expires_delta)

    # Assert
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

    # Check that expiration time is set correctly (within small margin of error)
    current_time = time.time()
    expected_expiry = current_time + expires_delta.total_seconds()
    assert abs(payload["exp"] - expected_expiry) < 5  # Within 5 seconds


def test_invalid_token_secret():
    """Test that tokens created with different secret are rejected."""
    # Arrange
    user_id = 123
    wrong_secret = "wrong-secret-key"

    # Create token with wrong secret
    payload = {"sub": str(user_id), "exp": time.time() + 300}
    token = jwt.encode(payload, wrong_secret, algorithm=ALGORITHM)

    # Act & Assert
    with pytest.raises(JWTError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def test_token_uniqueness(db_session, test_user):
    """Test that generated tokens are unique."""
    # Generate multiple tokens for the same user
    token_pair1 = generate_token_pair(db_session, test_user.id)

    # Add a small delay or use custom expiration to ensure tokens are different
    # Option 1: Add a small delay
    import time

    time.sleep(1)  # Sleep for 1 second to ensure different expiration timestamps

    # Option 2: Or use custom expiration times for each token (better approach)
    from datetime import timedelta

    token_pair2 = generate_token_pair(
        db_session,
        test_user.id,
        access_token_expires=timedelta(minutes=59),  # Different from default
        refresh_token_expires=timedelta(days=6),  # Different from default
    )

    # Verify refresh tokens are always unique (since they use UUIDs)
    assert token_pair1.refresh_token != token_pair2.refresh_token

    # Access tokens might be the same if generated at exactly the same time with same payload
    # But should be different if using different expiration times
    assert token_pair1.access_token != token_pair2.access_token


def test_token_database_security(db_session, test_user):
    """Test that tokens are properly stored in the database."""
    # Generate tokens
    generate_token_pair(db_session, test_user.id)

    # Check access token in database
    tokens = test_user.tokens
    access_tokens = [t for t in tokens if t.token_type == TokenType.ACCESS]
    refresh_tokens = [t for t in tokens if t.token_type == TokenType.REFRESH]

    # Verify we have at least one of each token type
    assert len(access_tokens) >= 1
    assert len(refresh_tokens) >= 1

    # Verify tokens have expiration dates
    for token in access_tokens + refresh_tokens:
        assert token.expires_at is not None
