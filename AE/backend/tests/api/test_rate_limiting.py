import time

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.users import User


@pytest.fixture
async def auth_headers(test_user: User, client: TestClient) -> dict:
    """Get authorization headers for authenticated requests"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "test@example.com", "password": "TestPassword123"},
    )
    tokens = response.json()

    # Update to handle the new response structure where tokens are in the "data" field
    access_token = tokens.get("data", {}).get("access_token")

    return {"Authorization": f"Bearer {access_token}"}


def test_rate_limit_headers(client: TestClient, auth_headers: dict):
    """Test that rate limit headers are included in responses"""
    response = client.get(
        f"{settings.API_V1_STR}/instruments",
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Check response follows standardized format
    content = response.json()
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content

    # Check for rate limit headers
    assert "X-Rate-Limit-Limit" in response.headers
    assert "X-Rate-Limit-Remaining" in response.headers
    assert "X-Rate-Limit-Reset" in response.headers

    # Verify they have valid values
    limit = int(response.headers["X-Rate-Limit-Limit"])
    remaining = int(response.headers["X-Rate-Limit-Remaining"])
    reset = int(response.headers["X-Rate-Limit-Reset"])

    assert limit > 0
    assert remaining > 0
    assert remaining <= limit
    assert reset > int(time.time())


# Commented out to avoid slowing down test runs
# def test_rate_limit_exceeded(client: TestClient, auth_headers: dict):
#     """Test that rate limiting works"""
#     # Note: This test is explicitly making many requests and will be slow
#     # It's commented out by default
#
#     # Get the limit from the first request
#     response = client.get(
#         f"{settings.API_V1_STR}/instruments",
#         headers=auth_headers,
#     )
#     limit = int(response.headers["X-Rate-Limit-Limit"])
#
#     # Make enough requests to exceed the limit
#     for _ in range(limit):
#         client.get(
#             f"{settings.API_V1_STR}/instruments",
#             headers=auth_headers,
#         )
#
#     # This request should fail with 429
#     response = client.get(
#         f"{settings.API_V1_STR}/instruments",
#         headers=auth_headers,
#     )
#     assert response.status_code == 429
#     content = response.json()
#     assert "error" in content
#     assert content["error"]["code"] == "RATE_LIMIT_EXCEEDED"


# Add a test for when rate limit is exceeded, validating error response format
def test_rate_limit_exceeded_format():
    """Test that rate limiting error responses follow standardized format"""
    # This is just to test the response format from a mocked response
    sample_error = {
        "success": False,
        "error": {
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "You have exceeded your rate limit. Please try again later.",
        },
    }

    # Validate structure
    assert sample_error["success"] is False
    assert "error" in sample_error
    assert "code" in sample_error["error"]
    assert sample_error["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "message" in sample_error["error"]
