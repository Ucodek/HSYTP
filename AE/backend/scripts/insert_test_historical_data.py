import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from app.core.config import settings
from app.crud.historical import historical_data
from app.crud.instruments import instrument as instrument_crud
from app.db.session import AsyncSessionLocal
from app.schemas.historical import HistoricalDataCreate

# Fix for Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Test symbol to use (must exist in database)
TEST_SYMBOL = "AAPL"
# Number of days of data to generate
DAYS_OF_DATA = 30
# Data points per day
POINTS_PER_DAY = 24  # For hourly data


async def generate_and_insert_test_data():
    """Generate and insert test historical data for TimescaleDB verification."""
    print(f"Connecting to database: {settings.SQLALCHEMY_DATABASE_URI}")

    async with AsyncSessionLocal() as db:
        # 1. Get the instrument
        instrument = await instrument_crud.get_by_symbol(db, symbol=TEST_SYMBOL)

        if not instrument:
            print(f"Instrument {TEST_SYMBOL} not found. Creating it first...")
            from app.schemas.instruments import InstrumentCreate

            instrument_data = InstrumentCreate(
                symbol=TEST_SYMBOL,
                name={"en-US": "Apple Inc."},
                type="stock",
                country="USA",
                currency="USD",
            )
            instrument = await instrument_crud.create(db, obj_in=instrument_data)
            print(f"Created instrument {TEST_SYMBOL} with ID {instrument.id}")

        # 2. Check if historical data already exists for this instrument
        result = await db.execute(
            text("SELECT COUNT(*) FROM historical_data WHERE instrument_id = :id"),
            {"id": instrument.id},
        )
        existing_count = result.scalar() or 0

        if existing_count > 0:
            print(
                f"Found {existing_count} existing historical data points for "
                f"{TEST_SYMBOL}"
            )
            user_input = input(
                "Delete existing data before inserting test data? (y/n): "
            )

            if user_input.lower() == "y":
                await db.execute(
                    text("DELETE FROM historical_data WHERE instrument_id = :id"),
                    {"id": instrument.id},
                )
                await db.commit()
                print(f"Deleted existing historical data for {TEST_SYMBOL}")
            else:
                print("Keeping existing data")

        # 3. Generate and insert test data
        print(f"Generating {DAYS_OF_DATA} days of hourly data for {TEST_SYMBOL}...")

        # Starting price and date
        current_price = 150.0
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=DAYS_OF_DATA)

        # Generate data points
        data_points = []
        current_date = start_date

        while current_date < end_date:
            # Add some randomness to price movements
            price_change = random.uniform(-5.0, 5.0)
            current_price = max(
                current_price + price_change, 1.0
            )  # Ensure price is positive

            # Generate OHLCV data
            open_price = current_price
            high_price = open_price * random.uniform(1.0, 1.05)
            low_price = open_price * random.uniform(0.95, 1.0)
            close_price = random.uniform(low_price, high_price)
            volume = int(random.uniform(500000, 5000000))

            data_point = HistoricalDataCreate(
                instrument_id=instrument.id,
                timestamp=current_date,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume,
                adjusted_close=close_price,
            )

            data_points.append(data_point)

            # Move to next hour
            current_date += timedelta(hours=1)

        # 4. Insert in batches for better performance
        batch_size = 100
        for i in range(0, len(data_points), batch_size):
            batch = data_points[i : i + batch_size]
            total_batches = (len(data_points) - 1) // batch_size + 1
            current_batch = i // batch_size + 1
            print(
                f"Inserting batch {current_batch}/{total_batches} "
                f"({len(batch)} records)..."
            )
            await historical_data.create_many(db, obj_in_list=batch)

        print(f"Successfully inserted {len(data_points)} historical data points")

        # 5. Verify data was inserted
        result = await db.execute(
            text("SELECT COUNT(*) FROM historical_data WHERE instrument_id = :id"),
            {"id": instrument.id},
        )
        new_count = result.scalar() or 0

        print(f"Total historical data points for {TEST_SYMBOL}: {new_count}")
        print(
            "Done! Now run scripts/verify_timescaledb.py to check the hypertable "
            "configuration"
        )


if __name__ == "__main__":
    asyncio.run(generate_and_insert_test_data())
