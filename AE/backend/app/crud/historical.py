from datetime import datetime, timedelta, timezone
from typing import List, Any
import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.historical_cache import historical_cache
from app.crud.base import CRUDBase
from app.models.historical import HistoricalData
from app.schemas.historical import HistoricalDataCreate

logger = logging.getLogger(__name__)


class CRUDHistoricalData(
    CRUDBase[HistoricalData, HistoricalDataCreate, HistoricalDataCreate]
):
    """CRUD operations for historical data with TimescaleDB optimizations."""

    def __init__(self):
        super().__init__(HistoricalData)

    async def get_for_instrument(
        self,
        db: AsyncSession,
        *,
        instrument_id: int,
        period: str,
        interval: str,
        use_cache: bool = True,
    ) -> List[Any]:
        """Get historical data for an instrument with time bucketing and caching."""
        # Try to get from cache first if enabled
        if use_cache:
            cached_data = await historical_cache.get_cached_data(
                instrument_id, period, interval
            )
            if cached_data:
                logger.debug(
                    f"Cache hit for historical data {instrument_id}/{period}/{interval}"
                )
                return cached_data

        # Calculate time range
        end_date = datetime.now(timezone.utc)
        start_date = self._calculate_start_date(end_date, period)

        # Handle the original data case (no aggregation)
        if interval == "1m":
            query = (
                select(HistoricalData)
                .where(
                    HistoricalData.instrument_id == instrument_id,
                    HistoricalData.timestamp >= start_date,
                    HistoricalData.timestamp <= end_date,
                )
                .order_by(HistoricalData.timestamp)
            )

            try:
                result = await db.execute(query)
                data = result.scalars().all()

                # Cache the result if we have data
                if use_cache and data:
                    await historical_cache.cache_data(
                        instrument_id, period, interval, data
                    )

                return data
            except Exception as e:
                logger.error(f"Error retrieving 1m data: {e}")
                # Rethrow to handle at API level
                raise

        # Special case: Use the materialized view for daily data
        if interval == "1d" and period not in ["1d"]:  # For periods longer than 1 day
            try:
                # Check if the materialized view exists
                result = await db.execute(text("SELECT to_regclass('daily_prices')"))
                if result.scalar():
                    # Use the materialized view for daily data
                    stmt = text(
                        """
                        SELECT
                            day as timestamp,
                            open,
                            high,
                            low,
                            close,
                            volume,
                            adjusted_close
                        FROM daily_prices
                        WHERE
                            instrument_id = :instrument_id AND
                            day >= :start_date AND
                            day <= :end_date
                        ORDER BY day ASC
                    """
                    )

                    result = await db.execute(
                        stmt,
                        {
                            "instrument_id": instrument_id,
                            "start_date": start_date,
                            "end_date": end_date,
                        },
                    )

                    data = result.fetchall()

                    # Cache results if we have data
                    if use_cache and data:
                        await historical_cache.cache_data(
                            instrument_id, period, interval, data
                        )

                    return data

            except Exception as e:
                logger.warning(f"Error using materialized view: {e}")
                logger.info("Falling back to on-the-fly aggregation")
                # Fallback to on-the-fly aggregation
                # if the materialized view doesn't exist
                # or there was an error

        # For aggregated data, use TimescaleDB functions
        try:
            interval_str = self._get_interval_string(interval)

            # SQL query with TimescaleDB's time_bucket function
            stmt = text(
                """
                SELECT
                    time_bucket(:interval, timestamp) AS bucket,
                    first(open, timestamp) AS open,
                    max(high) AS high,
                    min(low) AS low,
                    last(close, timestamp) AS close,
                    sum(volume) AS volume,
                    last(adjusted_close, timestamp) AS adjusted_close
                FROM historical_data
                WHERE
                    instrument_id = :instrument_id AND
                    timestamp >= :start_date AND
                    timestamp <= :end_date
                GROUP BY bucket
                ORDER BY bucket ASC
            """
            )

            result = await db.execute(
                stmt,
                {
                    "interval": interval_str,
                    "instrument_id": instrument_id,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )

            data = result.fetchall()

            # Cache the result if we got data
            if use_cache and data:
                await historical_cache.cache_data(instrument_id, period, interval, data)

            return data

        except Exception as e:
            logger.error(f"Error aggregating historical data: {e}")
            # Rethrow to handle at API level
            raise

    async def get_with_gaps_filled(
        self,
        db: AsyncSession,
        *,
        instrument_id: int,
        period: str,
        interval: str,
        fill_method: str = "locf",  # last observation carried forward
    ) -> List[Any]:
        """Get historical data with gaps filled for missing intervals."""
        # Calculate time range
        end_date = datetime.now(timezone.utc)
        start_date = self._calculate_start_date(end_date, period)
        interval_str = self._get_interval_string(interval)

        # Determine fill method (LOCF = Last Observation Carried Forward)
        locf_expr = "LOCF" if fill_method == "locf" else "COALESCE"

        # SQL query with TimescaleDB's time_bucket_gapfill function
        stmt = text(
            f"""
            SELECT
                time_bucket_gapfill(:interval, timestamp) AS timestamp,
                {locf_expr}(first(open, timestamp)) AS open,
                {locf_expr}(max(high)) AS high,
                {locf_expr}(min(low)) AS low,
                {locf_expr}(last(close, timestamp)) AS close,
                COALESCE(sum(volume), 0) AS volume,
                {locf_expr}(last(adjusted_close, timestamp)) AS adjusted_close
            FROM historical_data
            WHERE
                instrument_id = :instrument_id AND
                timestamp >= :start_date AND
                timestamp <= :end_date
            GROUP BY timestamp
            ORDER BY timestamp ASC
        """
        )

        result = await db.execute(
            stmt,
            {
                "interval": interval_str,
                "instrument_id": instrument_id,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        return result.fetchall()

    def _get_interval_string(self, interval: str) -> str:
        """Convert interval string to TimescaleDB interval format."""
        interval_map = {
            "1m": "1 minute",
            "5m": "5 minutes",
            "15m": "15 minutes",
            "30m": "30 minutes",
            "1h": "1 hour",
            "1d": "1 day",
            "1w": "1 week",
        }
        return interval_map.get(interval, "1 day")

    def _calculate_start_date(self, end_date: datetime, period: str) -> datetime:
        """Calculate start date based on period."""
        period_map = {
            "1d": timedelta(days=1),
            "1w": timedelta(weeks=1),
            "1m": timedelta(days=30),
            "3m": timedelta(days=90),
            "6m": timedelta(days=180),
            "1y": timedelta(days=365),
            "5y": timedelta(days=365 * 5),
            "max": timedelta(days=365 * 20),
        }
        delta = period_map.get(period, timedelta(days=30))
        return end_date - delta


# Create singleton instance
historical_data = CRUDHistoricalData()
