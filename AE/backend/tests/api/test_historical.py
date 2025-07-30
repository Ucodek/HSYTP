from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import settings
from app.models.historical import HistoricalData
from tests.conftest import TestingSessionLocal

# Test data constants
TEST_INSTRUMENT = {
    "symbol": "AAPL",
    "name": {"en-US": "Apple Inc."},
    "type": "stock",
    "country": "USA",
    "currency": "USD",
}


# Define a function to create test data dynamically
def generate_test_data(days_back=5, count=2):
    """Generate test data for a range of days."""
    data = []
    for i in range(days_back, days_back - count, -1):
        data.append(
            {
                "timestamp": (
                    datetime.now(timezone.utc) - timedelta(days=i)
                ).isoformat(),
                "open": 150.0 + i,
                "high": 153.0 + i,
                "low": 148.0 + i,
                "close": 152.0 + i,
                "volume": 10000000 + (i * 1000000),
                "adjusted_close": 152.0 + i,
            }
        )
    return data


# Use the function to generate test data
TEST_HISTORICAL_DATA = generate_test_data(days_back=5, count=2)


@pytest.fixture
async def test_historical_data(setup_database) -> dict:
    """Create test instrument with historical data."""
    async with TestingSessionLocal() as db:
        from app.crud.instruments import instrument as instrument_crud
        from app.schemas.instruments import InstrumentCreate

        # Get or create test instrument
        instrument = await instrument_crud.get_by_symbol(
            db, symbol=TEST_INSTRUMENT["symbol"]
        )
        if not instrument:
            instrument_in = InstrumentCreate(**TEST_INSTRUMENT)
            instrument = await instrument_crud.create(db, obj_in=instrument_in)

        # Clear any existing historical data
        await db.execute(
            text(f"DELETE FROM historical_data WHERE instrument_id = {instrument.id}")
        )
        await db.commit()

        # Add historical data
        for data_point in TEST_HISTORICAL_DATA:
            db_obj = HistoricalData(
                instrument_id=instrument.id,
                timestamp=datetime.fromisoformat(
                    data_point["timestamp"].replace("Z", "+00:00")
                ),
                open=data_point["open"],
                high=data_point["high"],
                low=data_point["low"],
                close=data_point["close"],
                volume=data_point["volume"],
                adjusted_close=data_point["adjusted_close"],
            )
            db.add(db_obj)

        await db.commit()

        # Verify data was added
        result = await db.execute(
            text(
                f"SELECT COUNT(*) FROM historical_data "
                f"WHERE instrument_id = {instrument.id}"
            )
        )
        count = result.scalar()

        return {"instrument": instrument, "data_points": count}


def test_get_historical_data(
    client: TestClient, auth_headers: dict, test_historical_data: dict
):
    """Test getting historical data for an instrument."""
    instrument = test_historical_data["instrument"]

    response = client.get(
        f"{settings.API_V1_STR}/instruments/{instrument.symbol}/historical",
        headers=auth_headers,
    )
    assert response.status_code == 200
    content = response.json()

    # Check for standardized response format
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data_timestamp" in content["meta"]
    assert "data" in content

    data = content["data"]
    assert data["symbol"] == instrument.symbol
    assert data["instrument_id"] == instrument.id
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == test_historical_data["data_points"]

    # Check data structure
    for point in data["data"]:
        assert "timestamp" in point
        assert "open" in point
        assert "high" in point
        assert "low" in point
        assert "close" in point
        assert "volume" in point


@pytest.mark.parametrize(
    "params,expected_status",
    [
        ({}, 200),  # Default parameters
        ({"period": "1y", "interval": "1d"}, 200),  # Custom parameters
        (
            {"period": "invalid"},
            422,
        ),  # Invalid period - FastAPI validation returns 422, not 400
        (
            {"interval": "invalid"},
            422,
        ),  # Invalid interval - FastAPI validation returns 422, not 400
    ],
)
def test_get_historical_data_params(
    client: TestClient,
    auth_headers: dict,
    test_historical_data: dict,
    params: dict,
    expected_status: int,
):
    """Test historical data API with various parameters."""
    instrument = test_historical_data["instrument"]

    # Build query string
    query_params = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{settings.API_V1_STR}/instruments/{instrument.symbol}/historical"
    if query_params:
        url += f"?{query_params}"

    response = client.get(url, headers=auth_headers)
    assert response.status_code == expected_status

    if expected_status == 200:
        content = response.json()
        # Update for standardized response format
        assert content["success"] is True
        assert "meta" in content
        assert "data" in content
        data = content["data"]
        assert data["symbol"] == instrument.symbol
        assert "data" in data
    elif expected_status == 422:
        # Check for validation error response format
        content = response.json()
        # Check for standardized error response format
        assert content["success"] is False
        assert "error" in content
        assert "code" in content["error"]
        assert content["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in content["error"]


def test_get_historical_data_nonexistent_instrument(
    client: TestClient, auth_headers: dict
):
    """Test getting historical data for a nonexistent instrument."""
    response = client.get(
        f"{settings.API_V1_STR}/instruments/NONEXISTENT/historical",
        headers=auth_headers,
    )
    assert response.status_code == 404
    content = response.json()
    # Check for standardized error response format
    assert content["success"] is False
    assert "error" in content
    assert "message" in content["error"]
    assert "not found" in content["error"]["message"].lower()
