import uuid

from fastapi import status


def test_register_endpoint(client, unique_user_data):
    """Test the register endpoint."""
    response = client.post("/api/v1/auth/register", json=unique_user_data)

    assert response.status_code == status.HTTP_201_CREATED

    # The API is returning data nested in a response structure
    data = response.json()["data"]

    # Check the returned user data
    assert data["email"] == unique_user_data["email"]
    assert data["username"] == unique_user_data["username"]
    assert "password" not in data  # Ensure password is not returned


def test_login_endpoint(client, test_user):
    """Test the login endpoint with form data."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "Password123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_json_endpoint(client, test_user):
    """Test the login endpoint with JSON."""
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "username": test_user.username,
            "password": "Password123",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_get_me_endpoint(client, token_headers, test_user):
    """Test the get_me endpoint."""
    response = client.get("/api/v1/auth/me", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


def test_get_me_unauthorized(client):
    """Test the get_me endpoint without authentication."""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_token_authentication(client, test_user):
    """Test that tokens work for authentication."""
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={
            "username": test_user.username,
            "password": "Password123",
        },
    )
    assert login_response.status_code == status.HTTP_200_OK

    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["data"]["id"] == test_user.id


def test_logout_endpoint(client, token_headers):
    """Test the logout endpoint."""
    response = client.post("/api/v1/auth/logout", headers=token_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_refresh_token_endpoint(client, test_user):
    """Test the refresh token endpoint."""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={
            "username": test_user.username,
            "password": "Password123",
        },
    )
    refresh_token = login_response.json()["data"]["refresh_token"]

    # Then use refresh token to get new tokens
    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == status.HTTP_200_OK
    data = refresh_response.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data

    # Verify new tokens are different from original
    assert data["access_token"] != login_response.json()["data"]["access_token"]
    assert data["refresh_token"] != refresh_token


def test_update_profile_endpoint(client, token_headers, test_user):
    """Test updating user profile."""
    new_name = f"Updated Name {uuid.uuid4().hex[:8]}"
    response = client.put(
        "/api/v1/auth/profile", json={"full_name": new_name}, headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["full_name"] == new_name
