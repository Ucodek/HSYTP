import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import settings
from app.models.instruments import InstrumentPrice
from app.models.market import MarketIndex, MarketIndexPrice
from tests.conftest import TestingSessionLocal

# Test data constants
TEST_MARKET_INDEX = {
    "symbol": "TESTIDX",
    "name": {"en-US": "Test Market Index", "tr-TR": "Test Piyasa Endeksi"},
    "country": "USA",
    "currency": "USD",
    "description": {"en-US": "A test market index for unit tests"},
}

# Test instrument with price for market movers tests
TEST_INSTRUMENT_GAINER = {
    "symbol": "GAINR",
    "name": {"en-US": "Gainer Inc."},
    "type": "stock",
    "country": "USA",
    "currency": "USD",
}

TEST_INSTRUMENT_LOSER = {
    "symbol": "LOSER",
    "name": {"en-US": "Loser Inc."},
    "type": "stock",
    "country": "USA",
    "currency": "USD",
}

TEST_INSTRUMENT_ACTIVE = {
    "symbol": "ACTVS",
    "name": {"en-US": "Active Corp."},
    "type": "stock",
    "country": "USA",
    "currency": "USD",
}


@pytest.fixture
async def test_market_index(setup_database) -> MarketIndex:
    """Create a test market index with price data."""
    async with TestingSessionLocal() as db:
        # Create test market index
        from app.crud.market import market_index
        from app.schemas.market import MarketIndexCreate

        # Check if test index already exists
        existing_index = await market_index.get_by_symbol(
            db, symbol=TEST_MARKET_INDEX["symbol"]
        )
        if existing_index:
            # Get index with price data
            index_with_price = await market_index.get_by_symbol_with_price(
                db, symbol=TEST_MARKET_INDEX["symbol"]
            )
            if index_with_price:
                return index_with_price
            # If index exists but no price, continue to add price

        # Create new test index if it doesn't exist
        if not existing_index:
            index_in = MarketIndexCreate(**TEST_MARKET_INDEX)
            existing_index = await market_index.create(db, obj_in=index_in)

        # Add price data for the index
        price = MarketIndexPrice(
            index_id=existing_index.id,
            last_price=1000.50,
            price_change=25.75,
            change_percent=2.64,
            volume=12345678,
            previous_close=974.75,
            period_high=1010.25,
            period_low=970.50,
            w52_high=1100.00,
            w52_low=800.00,
            data_timestamp="2023-03-21T12:00:00Z",
        )
        db.add(price)
        await db.commit()

        # Get fresh index with price data
        return await market_index.get_by_symbol_with_price(
            db, symbol=TEST_MARKET_INDEX["symbol"]
        )


@pytest.fixture
async def test_market_movers(setup_database) -> dict:
    """Create test instruments with price data for market movers tests."""
    async with TestingSessionLocal() as db:
        from app.crud.instruments import instrument as instrument_crud
        from app.schemas.instruments import InstrumentCreate

        # Clear existing price data for these test instruments to avoid conflicts
        # Use text() to properly declare SQL as textual expression
        delete_query = text(
            "DELETE FROM instrument_prices WHERE instrument_id IN "
            "(SELECT id FROM instruments WHERE symbol IN "
            f"('{TEST_INSTRUMENT_GAINER['symbol']}', "
            f"'{TEST_INSTRUMENT_LOSER['symbol']}', "
            f"'{TEST_INSTRUMENT_ACTIVE['symbol']}'))"
        )
        await db.execute(delete_query)
        await db.commit()

        instruments = {}

        # Process each test instrument
        for name, data in [
            ("gainer", TEST_INSTRUMENT_GAINER),
            ("loser", TEST_INSTRUMENT_LOSER),
            ("active", TEST_INSTRUMENT_ACTIVE),
        ]:
            # Get or create instrument
            instrument = await instrument_crud.get_by_symbol(db, symbol=data["symbol"])
            if not instrument:
                instrument_in = InstrumentCreate(**data)
                instrument = await instrument_crud.create(db, obj_in=instrument_in)

            instruments[name] = instrument

        # Add price data
        price_data = [
            # Gainer with positive change
            InstrumentPrice(
                instrument_id=instruments["gainer"].id,
                price=150.75,
                price_change=7.50,
                change_percent=5.23,
                volume=5000000,
                data_timestamp="2023-03-21T12:00:00Z",
            ),
            # Loser with negative change
            InstrumentPrice(
                instrument_id=instruments["loser"].id,
                price=45.25,
                price_change=-3.75,
                change_percent=-7.65,
                volume=3000000,
                data_timestamp="2023-03-21T12:00:00Z",
            ),
            # Active with high volume
            InstrumentPrice(
                instrument_id=instruments["active"].id,
                price=78.50,
                price_change=1.25,
                change_percent=1.62,
                volume=10000000,
                data_timestamp="2023-03-21T12:00:00Z",
            ),
        ]

        # Add all prices at once
        db.add_all(price_data)
        await db.commit()

        # Refresh the instruments to get their relationships loaded
        for name in instruments:
            await db.refresh(instruments[name])

        return instruments


def test_get_market_indices(
    client: TestClient, auth_headers: dict, test_market_index: MarketIndex
):
    """Test getting a list of market indices."""
    response = client.get(
        f"{settings.API_V1_STR}/market/indices",
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Check response follows standardized format
    content = response.json()
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "pagination" in content["meta"]
    assert "data" in content

    data = content["data"]
    assert isinstance(data, list)

    # Check only if any items are returned and basic structure is correct
    if len(data) > 0:
        assert "symbol" in data[0]
        assert "name" in data[0]

        # Check if our test index exists in the response
        test_index = next(
            (idx for idx in data if idx["symbol"] == TEST_MARKET_INDEX["symbol"]),
            None,
        )
        assert test_index is not None, "Test market index not found"


def test_get_market_index_by_symbol(
    client: TestClient, auth_headers: dict, test_market_index: MarketIndex
):
    """Test getting a specific market index by symbol."""
    response = client.get(
        f"{settings.API_V1_STR}/market/indices/{TEST_MARKET_INDEX['symbol']}",
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Check response follows standardized format
    content = response.json()
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content

    data = content["data"]
    assert data["symbol"] == TEST_MARKET_INDEX["symbol"]
    assert data["name"] == TEST_MARKET_INDEX["name"]
    assert data["country"] == TEST_MARKET_INDEX["country"]

    # Check if price data is included
    assert "price" in data
    assert data["price"] is not None
    assert "last_price" in data["price"]
    assert data["price"]["last_price"] == 1000.50
    assert data["price"]["change_percent"] == 2.64


def test_get_nonexistent_market_index(client: TestClient, auth_headers: dict):
    """Test getting a market index that doesn't exist."""
    response = client.get(
        f"{settings.API_V1_STR}/market/indices/NONEXISTENT",
        headers=auth_headers,
    )
    assert response.status_code == 404

    # Check for standardized error response format
    content = response.json()
    assert content["success"] is False
    assert "error" in content
    assert "code" in content["error"]
    assert "message" in content["error"]
    assert "not found" in content["error"]["message"].lower()


def test_filter_market_indices_by_country(
    client: TestClient, auth_headers: dict, test_market_index: MarketIndex
):
    """Test filtering market indices by country."""
    # Test with the country of our test index
    response = client.get(
        f"{settings.API_V1_STR}/market/indices?country={TEST_MARKET_INDEX['country']}",
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Check for standardized response format
    content = response.json()
    assert content["success"] is True
    assert "meta" in content
    assert "pagination" in content["meta"]
    assert "data" in content

    data = content["data"]
    # Only verify that our test index is in the response
    if len(data) > 0:
        test_index = next(
            (idx for idx in data if idx["symbol"] == TEST_MARKET_INDEX["symbol"]),
            None,
        )
        assert test_index is not None, "Test market index not found"
        assert test_index["country"] == TEST_MARKET_INDEX["country"]

    # Test with a non-existent country
    response = client.get(
        f"{settings.API_V1_STR}/market/indices?country=NONEXISTENT",
        headers=auth_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["success"] is True
    assert "data" in content
    assert len(content["data"]) == 0


def test_get_market_movers_gainers(
    client: TestClient, auth_headers: dict, test_market_movers: dict
):
    """Test getting market movers - gainers."""
    response = client.get(
        f"{settings.API_V1_STR}/market/movers?type=gainers",
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Check response follows standardized format
    content = response.json()
    assert content["success"] is True
    assert "meta" in content
    assert "timestamp" in content["meta"]
    assert "data" in content

    data = content["data"]
    assert data["type"] == "gainers"
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_market_movers_losers(
    client: TestClient, auth_headers: dict, test_market_movers: dict
):
    """Test getting market movers - losers."""
    response = client.get(
        f"{settings.API_V1_STR}/market/movers?type=losers",
        headers=auth_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert content["success"] is True
    assert "meta" in content
    assert "data" in content

    data = content["data"]
    assert data["type"] == "losers"
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_market_movers_active(
    client: TestClient, auth_headers: dict, test_market_movers: dict
):
    """Test getting market movers - most active."""
    response = client.get(
        f"{settings.API_V1_STR}/market/movers?type=active",
        headers=auth_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert content["success"] is True
    assert "meta" in content
    assert "data" in content

    data = content["data"]
    assert data["type"] == "active"
    assert "data" in data
    assert isinstance(data["data"], list)


def test_invalid_market_mover_type(client: TestClient, auth_headers: dict):
    """Test getting market movers with an invalid type."""
    response = client.get(
        f"{settings.API_V1_STR}/market/movers?type=invalid",
        headers=auth_headers,
    )
    assert response.status_code == 422  # Validation error from FastAPI

    # Check for standardized error response format
    content = response.json()
    assert content["success"] is False
    assert "error" in content
    assert "code" in content["error"]
    assert "details" in content["error"]
