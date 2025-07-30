import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.instruments import Instrument
from app.models.users import User
from tests.conftest import TestingSessionLocal

# Test constants
TEST_INSTRUMENT = {
    "symbol": "AAPL",
    "name": {"en-US": "Apple Inc."},
    "type": "stock",
    "country": "USA",
    "currency": "USD",
}

NEW_INSTRUMENT = {
    "symbol": "MSFT",
    "name": {"en-US": "Microsoft Corporation"},
    "type": "stock",
    "country": "USA",
    "currency": "USD",
    "sector": "Technology",
    "industry": "Software",
}

UPDATE_INSTRUMENT = {
    "name": {"en-US": "Microsoft Corp Updated"},
    "sector": "Updated Technology",
}


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

    # Fallback to old structure if needed - makes test more resilient
    if access_token is None:
        access_token = tokens.get("access_token")

    if access_token is None:
        raise ValueError("Could not extract access token from response")

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def test_instrument(setup_database) -> Instrument:
    """Create a test instrument"""
    async with TestingSessionLocal() as db:
        from app.crud.instruments import instrument as instrument_crud
        from app.schemas.instruments import InstrumentCreate

        # Check if test instrument already exists
        db_instrument = await instrument_crud.get_by_symbol(
            db, symbol=TEST_INSTRUMENT["symbol"]
        )
        if not db_instrument:
            # Create test instrument
            instrument_in = InstrumentCreate(**TEST_INSTRUMENT)
            db_instrument = await instrument_crud.create(db, obj_in=instrument_in)
        return db_instrument


def test_get_instruments(client: TestClient, auth_headers: dict):
    """Test getting a list of instruments"""
    response = client.get(
        f"{settings.API_V1_STR}/instruments",
        headers=auth_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # Check for standardized response format
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "pagination" in content["meta"]
    assert "data" in content

    data = content["data"]
    assert isinstance(data, list)
    # Additional checks can be done on the data if needed


def test_get_instrument_by_symbol(
    client: TestClient, auth_headers: dict, test_instrument: Instrument
):
    """Test getting an instrument by symbol"""
    response = client.get(
        f"{settings.API_V1_STR}/instruments/{TEST_INSTRUMENT['symbol']}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # Check for standardized response format
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content

    data = content["data"]
    assert data["symbol"] == TEST_INSTRUMENT["symbol"]
    assert data["name"] == TEST_INSTRUMENT["name"]
    assert data["type"] == TEST_INSTRUMENT["type"]


def test_get_instruments_filter_by_type(
    client: TestClient, auth_headers: dict, test_instrument: Instrument
):
    """Test filtering instruments by type"""
    response = client.get(
        f"{settings.API_V1_STR}/instruments?type=stock",
        headers=auth_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # Check for standardized response format
    assert content["success"] is True
    assert "meta" in content
    assert "pagination" in content["meta"]
    assert "data" in content

    data = content["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(item["type"] == "stock" for item in data)


def test_get_instruments_filter_by_country(
    client: TestClient, auth_headers: dict, test_instrument: Instrument
):
    """Test filtering instruments by country"""
    response = client.get(
        f"{settings.API_V1_STR}/instruments?country=USA",
        headers=auth_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # Check for standardized response format
    assert content["success"] is True
    assert "meta" in content
    assert "pagination" in content["meta"]
    assert "data" in content

    data = content["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(item["country"] == "USA" for item in data)


def test_get_instruments_pagination(client: TestClient, auth_headers: dict):
    """Test instrument pagination"""
    # First, get all instruments
    response_all = client.get(
        f"{settings.API_V1_STR}/instruments",
        headers=auth_headers,
    )
    content_all = response_all.json()
    all_instruments = content_all["data"]  # Access data field in the response

    # Now get with limit=1
    response_limited = client.get(
        f"{settings.API_V1_STR}/instruments?limit=1",
        headers=auth_headers,
    )
    content_limited = response_limited.json()
    limited_instruments = content_limited["data"]  # Access data field in the response

    assert response_limited.status_code == 200
    assert len(limited_instruments) <= 1

    if len(all_instruments) > 1:
        assert len(limited_instruments) < len(all_instruments)


def test_get_nonexistent_instrument(client: TestClient, auth_headers: dict):
    """Test getting an instrument that doesn't exist"""
    response = client.get(
        f"{settings.API_V1_STR}/instruments/NONEXISTENT",
        headers=auth_headers,
    )
    assert response.status_code == 404
    content = response.json()
    # Check for standardized error response format
    assert content["success"] is False
    assert "error" in content
    assert "code" in content["error"]
    assert "message" in content["error"]
    assert "not found" in content["error"]["message"].lower()


def test_create_instrument(client: TestClient, auth_headers: dict):
    """Test creating a new instrument"""
    response = client.post(
        f"{settings.API_V1_STR}/instruments",
        headers=auth_headers,
        json=NEW_INSTRUMENT,
    )
    assert response.status_code == 201
    content = response.json()
    # Check for standardized response format
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content

    data = content["data"]
    assert data["symbol"] == NEW_INSTRUMENT["symbol"]
    assert data["name"] == NEW_INSTRUMENT["name"]
    assert data["type"] == NEW_INSTRUMENT["type"]
    assert data["country"] == NEW_INSTRUMENT["country"]
    assert data["sector"] == NEW_INSTRUMENT["sector"]

    # Verify it's in the database by getting it
    get_response = client.get(
        f"{settings.API_V1_STR}/instruments/{NEW_INSTRUMENT['symbol']}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200


def test_create_duplicate_instrument(
    client: TestClient, auth_headers: dict, test_instrument: Instrument
):
    """Test creating an instrument with a symbol that already exists"""
    duplicate_instrument = {
        "symbol": TEST_INSTRUMENT["symbol"],  # Same symbol as test_instrument
        "name": {"en-US": "Different Name"},
        "type": "stock",
        "country": "USA",
        "currency": "USD",
    }

    response = client.post(
        f"{settings.API_V1_STR}/instruments",
        headers=auth_headers,
        json=duplicate_instrument,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["success"] is False
    assert "error" in content
    assert "message" in content["error"]
    assert "already exists" in content["error"]["message"].lower()


def test_update_instrument(client: TestClient, auth_headers: dict):
    """Test updating an instrument"""
    # First, create an instrument to update
    client.post(
        f"{settings.API_V1_STR}/instruments",
        headers=auth_headers,
        json=NEW_INSTRUMENT,
    )

    # Now update it
    response = client.put(
        f"{settings.API_V1_STR}/instruments/{NEW_INSTRUMENT['symbol']}",
        headers=auth_headers,
        json=UPDATE_INSTRUMENT,
    )
    assert response.status_code == 200
    content = response.json()
    data = content["data"]  # Access data field in the response
    assert data["symbol"] == NEW_INSTRUMENT["symbol"]  # Symbol shouldn't change
    assert data["name"] == UPDATE_INSTRUMENT["name"]  # Name should be updated
    assert data["sector"] == UPDATE_INSTRUMENT["sector"]  # Sector should be updated


def test_update_nonexistent_instrument(client: TestClient, auth_headers: dict):
    """Test updating an instrument that doesn't exist"""
    response = client.put(
        f"{settings.API_V1_STR}/instruments/NONEXISTENT",
        headers=auth_headers,
        json=UPDATE_INSTRUMENT,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["success"] is False
    assert "error" in content
    assert "message" in content["error"]
    assert "not found" in content["error"]["message"].lower()


def test_delete_instrument(client: TestClient, auth_headers: dict):
    """Test deleting an instrument"""
    # First, create an instrument to delete
    client.post(  # Remove the variable assignment since it's unused
        f"{settings.API_V1_STR}/instruments",
        headers=auth_headers,
        json=NEW_INSTRUMENT,
    )

    # Now delete it
    response = client.delete(
        f"{settings.API_V1_STR}/instruments/{NEW_INSTRUMENT['symbol']}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    content = response.json()
    data = content["data"]  # Access data field in the response
    assert data["symbol"] == NEW_INSTRUMENT["symbol"]

    # Verify it's gone by trying to get it
    get_response = client.get(
        f"{settings.API_V1_STR}/instruments/{NEW_INSTRUMENT['symbol']}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


def test_delete_nonexistent_instrument(client: TestClient, auth_headers: dict):
    """Test deleting an instrument that doesn't exist"""
    response = client.delete(
        f"{settings.API_V1_STR}/instruments/NONEXISTENT",
        headers=auth_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["success"] is False
    assert "error" in content
    assert "message" in content["error"]
    assert "not found" in content["error"]["message"].lower()
