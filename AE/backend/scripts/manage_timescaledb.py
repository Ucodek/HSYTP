import asyncio
import sys
import argparse
import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

# Fix for Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def verify_timescaledb():
    """Verify TimescaleDB configuration."""
    print("Verifying TimescaleDB setup...")
    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    try:
        async with engine.connect() as conn:
            # Check extension
            result = await conn.execute(
                text(
                    "SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'"
                )
            )
            version = result.scalar()
            if version:
                print(f"✓ TimescaleDB is installed (version: {version})")
            else:
                print("✗ TimescaleDB extension is not installed")
                return False

            # Check hypertable configuration
            result = await conn.execute(
                text(
                    "SELECT * FROM timescaledb_information.hypertables WHERE "
                    "hypertable_name = 'historical_data'"
                )
            )
            hypertable = result.fetchone()
            if hypertable:
                print("✓ historical_data is configured as a TimescaleDB hypertable")
            else:
                print("✗ historical_data is not configured as a hypertable")
                return False

            # Check data and chunks
            result = await conn.execute(text("SELECT COUNT(*) FROM historical_data"))
            count = result.scalar() or 0
            print(f"✓ historical_data table contains {count} rows")

            result = await conn.execute(
                text(
                    "SELECT COUNT(*) FROM timescaledb_information.chunks "
                    "WHERE hypertable_name = 'historical_data'"
                )
            )
            chunks = result.scalar() or 0
            print(f"✓ TimescaleDB has created {chunks} chunks for this data")

            # Check materialized view
            result = await conn.execute(text("SELECT to_regclass('daily_prices')"))
            if result.scalar():
                print("✓ daily_prices materialized view exists")
            else:
                print("✗ daily_prices materialized view does not exist")

            print("\nTimescaleDB verification complete")
            return True
    except Exception as e:
        print(f"Error verifying TimescaleDB: {e}")
        return False
    finally:
        await engine.dispose()


async def setup_hypertable():
    """Set up TimescaleDB hypertable for historical_data."""
    print("Setting up TimescaleDB hypertable...")

    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    try:
        async with engine.begin() as conn:
            # Check if historical_data table exists
            result = await conn.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables "
                    "WHERE table_name = 'historical_data')"
                )
            )
            table_exists = result.scalar()

            if not table_exists:
                print("✗ historical_data table doesn't exist")
                print("Please run migrations first: poetry run alembic upgrade head")
                return False

            print("✓ historical_data table exists")

            # Check if it's already a hypertable
            result = await conn.execute(
                text(
                    "SELECT COUNT(*) FROM timescaledb_information.hypertables WHERE hypertable_name = 'historical_data'"
                )
            )
            is_hypertable = result.scalar() > 0

            if is_hypertable:
                print("✓ historical_data is already a hypertable")
                return True

            # Convert to hypertable
            print("Converting historical_data to a hypertable...")
            await conn.execute(
                text(
                    "SELECT create_hypertable('historical_data', 'timestamp', "
                    "if_not_exists => TRUE, migrate_data => TRUE)"
                )
            )
            print("✓ Successfully converted historical_data to a hypertable")

            # Create index for better query performance
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_historical_data_instrument_time "
                    "ON historical_data(instrument_id, timestamp DESC)"
                )
            )
            print("✓ Created index for better query performance")

            return True

    except Exception as e:
        print(f"Error setting up hypertable: {e}")
        return False
    finally:
        await engine.dispose()


async def setup_materialized_view():
    """Create standard PostgreSQL materialized view for daily aggregates."""
    print("Creating materialized view...")

    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    try:
        async with engine.begin() as conn:
            # Drop existing view if it exists
            await conn.execute(text("DROP MATERIALIZED VIEW IF EXISTS daily_prices"))

            # Create materialized view
            await conn.execute(
                text(
                    """
                CREATE MATERIALIZED VIEW daily_prices AS
                SELECT
                    time_bucket('1 day', timestamp) AS day,
                    instrument_id,
                    first(open, timestamp) AS open,
                    max(high) AS high,
                    min(low) AS low,
                    last(close, timestamp) AS close,
                    sum(volume) AS volume,
                    last(adjusted_close, timestamp) AS adjusted_close
                FROM historical_data
                GROUP BY day, instrument_id
                ORDER BY day DESC
            """
                )
            )
            print("✓ Created materialized view: daily_prices")

            # Create index
            await conn.execute(
                text(
                    "CREATE INDEX idx_daily_prices_instrument_day "
                    "ON daily_prices(instrument_id, day)"
                )
            )
            print("✓ Created index on materialized view")

            return True

    except Exception as e:
        print(f"Error creating materialized view: {e}")
        return False
    finally:
        await engine.dispose()


async def refresh_materialized_view():
    """Refresh the daily_prices materialized view."""
    print("Refreshing materialized view...")

    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    try:
        start_time = time.time()
        async with engine.begin() as conn:
            # Check if the view exists
            result = await conn.execute(text("SELECT to_regclass('daily_prices')"))
            if not result.scalar():
                print("✗ daily_prices view does not exist. Run setup-view first.")
                return False

            # Refresh the view
            await conn.execute(text("REFRESH MATERIALIZED VIEW daily_prices"))

            result = await conn.execute(text("SELECT COUNT(*) FROM daily_prices"))
            count = result.scalar() or 0

            elapsed = time.time() - start_time
            print(
                f"✓ Refreshed daily_prices ({count} records) in {elapsed:.2f} seconds"
            )
            return True

    except Exception as e:
        print(f"Error refreshing view: {e}")
        return False
    finally:
        await engine.dispose()


# Main function to handle CLI arguments
async def main():
    parser = argparse.ArgumentParser(description="TimescaleDB Management Tool")
    parser.add_argument(
        "command",
        choices=["verify", "setup", "setup-view", "refresh", "all"],
        help="Command to run",
    )

    args = parser.parse_args()

    if args.command == "verify":
        await verify_timescaledb()
    elif args.command == "setup":
        await setup_hypertable()
    elif args.command == "setup-view":
        await setup_materialized_view()
    elif args.command == "refresh":
        await refresh_materialized_view()
    elif args.command == "all":
        # Run all steps
        if await verify_timescaledb():
            print("\nRunning setup...")
            if await setup_hypertable():
                print("\nSetting up materialized view...")
                if await setup_materialized_view():
                    print("\nRefreshing view...")
                    await refresh_materialized_view()


if __name__ == "__main__":
    asyncio.run(main())
