import asyncio
import logging

from sqlalchemy import text

from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def refresh_continuous_aggregates() -> None:
    """Refresh materialized views for aggregated data."""
    logger.info("Refreshing materialized views")

    try:
        async with AsyncSessionLocal() as db:
            # Simple materialized view refresh
            await db.execute(text("REFRESH MATERIALIZED VIEW daily_prices"))
            await db.commit()
            logger.info("Successfully refreshed materialized views")
    except Exception as e:
        logger.error(f"Error refreshing materialized views: {e}")
        raise


async def execute_maintenance() -> None:
    """Execute TimescaleDB maintenance tasks."""
    logger.info("Running TimescaleDB maintenance")

    try:
        async with AsyncSessionLocal() as db:
            # Run compression job
            await db.execute(
                text(
                    "SELECT compress_chunks('historical_data', older_than => INTERVAL '7 days')"
                )
            )

            # Run retention policy job
            await db.execute(
                text(
                    "SELECT drop_chunks('historical_data', older_than => INTERVAL '1 year')"
                )
            )

            # Log maintenance stats with broken up query
            result = await db.execute(
                text(
                    """
                    SELECT
                        pg_size_pretty(before_compression_total_bytes) as before_size,
                        pg_size_pretty(after_compression_total_bytes) as after_size,
                        round(
                            100 * (before_compression_total_bytes -
                            after_compression_total_bytes) /
                            NULLIF(before_compression_total_bytes, 0)
                        ) as percent_savings
                    FROM timescaledb_information.compressed_chunk_stats
                    WHERE hypertable_name = 'historical_data'
                    """
                )
            )

            stats = result.fetchone()
            if stats:
                logger.info(
                    f"Compression savings: {stats[2]}% (Before: {stats[0]}, "
                    f"After: {stats[1]})"
                )

        logger.info("TimescaleDB maintenance completed")
    except Exception as e:
        logger.error(f"Error during TimescaleDB maintenance: {e}")


if __name__ == "__main__":
    # This allows the script to be run directly for manual maintenance
    asyncio.run(execute_maintenance())
