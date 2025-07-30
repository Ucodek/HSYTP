import time

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.crud.users import user as user_crud
from app.models.users import User
from app.schemas.users import UserCreate
from tests.conftest import TestingSessionLocal

# Test constants
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "TestPassword123"  # Follows password validation rules


@pytest.fixture
async def test_user(setup_database) -> User:
    """Create a test user for authentication tests"""
    async with TestingSessionLocal() as db:
        # Check if test user already exists
        user = await user_crud.get_by_email(db, email=TEST_USER_EMAIL)
        if not user:
            # Create test user
            user_in = UserCreate(
                email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD, is_active=True
            )
            user = await user_crud.create(db, obj_in=user_in)
        return user


def test_login(client: TestClient, test_user: User):
    """Test login endpoint"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    content = response.json()
    # Check response format according to PRD
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content
    data = content["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient, test_user: User):
    """Test login with incorrect password"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": TEST_USER_EMAIL, "password": "wrong_password"},
    )
    assert response.status_code == 401
    content = response.json()
    # Check for error structure in standardized format
    assert content["success"] is False
    assert "error" in content
    assert "message" in content["error"]
    assert "Incorrect email or password" in content["error"]["message"]


def test_register(client: TestClient):
    """Test user registration"""
    email = "new_user@example.com"
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email,
            "password": "NewPassword123",
            "is_active": True,
            "subscription_tier": "basic",
        },
    )
    assert response.status_code == 200
    content = response.json()
    # Check response format according to PRD
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content
    data = content["data"]
    assert data["email"] == email
    assert "id" in data
    assert "created_at" in data


def test_register_existing_email(client: TestClient, test_user: User):
    """Test registration with an existing email should fail"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": TEST_USER_EMAIL,  # Use the same email as test_user
            "password": "DifferentPass123",
            "is_active": True,
            "subscription_tier": "basic",
        },
    )
    assert response.status_code == 409  # Conflict
    content = response.json()
    # Check for error structure in standardized format
    assert content["success"] is False
    assert "error" in content
    assert "message" in content["error"]
    assert "exists" in content["error"]["message"].lower()


def test_register_invalid_password(client: TestClient):
    """Test registration with invalid password format"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "another_user@example.com",
            "password": "weak",  # Password too short/simple
            "is_active": True,
            "subscription_tier": "basic",
        },
    )
    assert response.status_code == 422  # Unprocessable Entity
    content = response.json()
    # Check for error structure in standardized format
    assert content["success"] is False
    assert "error" in content
    assert "details" in content["error"]


def test_refresh_token(client: TestClient, test_user: User):
    """Test refreshing an access token with a refresh token"""
    # First login to get the tokens
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    tokens = login_response.json()
    refresh_token = tokens["data"]["refresh_token"]  # Get refresh token from data field

    # Wait a brief moment to ensure the token timestamp will be different
    time.sleep(1)

    # Use the refresh token to get a new access token
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    content = response.json()
    # Check response format according to PRD
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content
    data = content["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify the new tokens are different
    assert (
        data["access_token"] != tokens["data"]["access_token"]
    )  # Compare with data field
    assert data["refresh_token"] != refresh_token


def test_get_me(client: TestClient, test_user: User):
    """Test getting current user profile"""
    # First login to get the token
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    tokens = login_response.json()
    access_token = tokens["data"]["access_token"]  # Get access token from data field

    # Use the token to get the current user
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    content = response.json()
    # Check response format according to PRD
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content
    data = content["data"]
    assert data["email"] == TEST_USER_EMAIL
    assert data["id"] == test_user.id


def test_logout(client: TestClient, test_user: User):
    """Test logging out (revoking a refresh token)"""
    # First login to get the tokens
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    tokens = login_response.json()
    access_token = tokens["data"]["access_token"]  # Get access token from data field
    refresh_token = tokens["data"]["refresh_token"]  # Get refresh token from data field

    # Logout
    response = client.post(
        f"{settings.API_V1_STR}/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    content = response.json()
    # Check response format according to PRD
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content
    data = content["data"]
    assert "detail" in data
    assert "success" in data["detail"].lower()

    # Try to use the revoked refresh token
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401  # Unauthorized
    content = response.json()
    # Check for error structure in standardized format
    assert content["success"] is False
    assert "error" in content
    assert "message" in content["error"]
