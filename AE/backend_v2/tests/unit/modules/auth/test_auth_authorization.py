import pytest

from app.errors.exceptions import AuthenticationError, AuthorizationError
from app.modules.auth.dependencies import (
    get_current_admin_user,
    get_current_user,
    get_current_verified_user,
)
from app.modules.auth.models import UserRole


@pytest.mark.asyncio
async def test_get_current_user_dependency(db_session, test_user, monkeypatch):
    """Test that get_current_user returns the user from token."""
    # Create a mock token that would decode to the test user
    token = "valid_token_for_test_user"

    # Use monkeypatch fixture instead of context manager
    monkeypatch.setattr(
        "jose.jwt.decode", lambda *args, **kwargs: {"sub": str(test_user.id)}
    )

    # Call the dependency directly with our mocked token
    user = await get_current_user(token, db_session)

    # Verify the correct user is returned
    assert user is not None
    assert user.id == test_user.id
    assert user.username == test_user.username


@pytest.mark.asyncio
async def test_get_current_admin_user_as_admin(db_session, test_admin):
    """Test that get_current_admin_user allows admin users."""
    # Call the dependency with an admin user
    user = await get_current_admin_user(test_admin)

    # Verify the user is returned unchanged
    assert user is not None
    assert user.id == test_admin.id
    assert user.role == UserRole.ADMIN


@pytest.mark.asyncio
async def test_get_current_admin_user_as_regular_user(db_session, test_user):
    """Test that get_current_admin_user rejects regular users."""
    # Ensure test_user is not an admin
    test_user.role = UserRole.USER
    db_session.commit()

    # Attempt to use the admin dependency with a regular user
    with pytest.raises(AuthorizationError) as excinfo:
        await get_current_admin_user(test_user)

    # Verify the correct error is raised
    assert excinfo.value.status_code == 403
    assert "Admin privileges required" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_get_current_verified_user_verified(db_session, test_user):
    """Test that get_current_verified_user allows verified users."""
    # Ensure the user is verified
    test_user.is_verified = True
    db_session.commit()

    # Call the dependency with a verified user
    user = await get_current_verified_user(test_user)

    # Verify the user is returned unchanged
    assert user is not None
    assert user.id == test_user.id
    assert user.is_verified is True


@pytest.mark.asyncio
async def test_get_current_verified_user_unverified(db_session, test_user):
    """Test that get_current_verified_user rejects unverified users."""
    # Ensure the user is not verified
    test_user.is_verified = False
    db_session.add(test_user)
    db_session.commit()

    # Attempt to use the verified user dependency with an unverified user
    with pytest.raises(AuthenticationError) as excinfo:
        await get_current_verified_user(test_user)

    # Verify the correct error is raised
    assert excinfo.value.status_code == 401
    assert "Email not verified" in str(excinfo.value.detail)
