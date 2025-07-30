import asyncio
import sys
from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text

from app.db.session import AsyncSessionLocal

# Fix for Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def visualize_historical_data(
    symbol: str,
    period: str = "1m",  # 1 month
    interval: str = "1d",  # 1 day
    fill_gaps: bool = False,  # Changed default to
    # False due to Apache license limitations
):
    """Visualize historical data for a given instrument."""
    print(f"Getting historical data for {symbol}...")

    async with AsyncSessionLocal() as db:
        # 1. Get instrument ID
        result = await db.execute(
            text("SELECT id FROM instruments WHERE symbol = :symbol"),
            {"symbol": symbol},
        )
        instrument = result.fetchone()
        if not instrument:
            print(f"Instrument {symbol} not found")
            return

        instrument_id = instrument[0]
        print(f"Found instrument ID: {instrument_id}")

        # 2. Calculate date range
        end_date = datetime.now(timezone.utc)
        if period == "1w":
            start_date = end_date - timedelta(days=7)
        elif period == "1m":
            start_date = end_date - timedelta(days=30)
        elif period == "3m":
            start_date = end_date - timedelta(days=90)
        elif period == "6m":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to 1 month

        # 3. Query data using time_bucket (without gap
        # filling for Apache license compatibility)
        interval_map = {
            "1d": "1 day",
            "1h": "1 hour",
            "30m": "30 minutes",
            "15m": "15 minutes",
            "5m": "5 minutes",
            "1m": "1 minute",
        }
        interval_str = interval_map.get(interval, "1 day")

        query_params = {
            "instrument_id": instrument_id,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval_str,
        }

        # Use a simpler query compatible with Apache license
        query = text(
            """
            SELECT
                time_bucket(:interval, timestamp) AS time,
                avg(close) as close,
                max(high) as high,
                min(low) as low,
                first(open, timestamp) as open,
                sum(volume) as volume
            FROM historical_data
            WHERE
                instrument_id = :instrument_id AND
                timestamp >= :start_date AND
                timestamp <= :end_date
            GROUP BY time
            ORDER BY time ASC
        """
        )

        result = await db.execute(query, query_params)
        rows = result.fetchall()

        if not rows:
            print(f"No data found for {symbol} in the specified period")
            return

        print(f"Found {len(rows)} data points")

        # 4. Convert to pandas DataFrame - FIX: Properly handle SQLAlchemy row objects
        data_dicts = []
        for row in rows:
            # Convert SQLAlchemy row to dict using _mapping or via column access
            if hasattr(row, "_mapping"):
                # For SQLAlchemy 1.4+ Row objects
                data_dicts.append(dict(row._mapping))
            else:
                # Fallback - access by column name manually
                data_dict = {}
                data_dict["time"] = row.time if hasattr(row, "time") else row[0]
                data_dict["close"] = row.close if hasattr(row, "close") else row[1]
                data_dict["high"] = row.high if hasattr(row, "high") else row[2]
                data_dict["low"] = row.low if hasattr(row, "low") else row[3]
                data_dict["open"] = row.open if hasattr(row, "open") else row[4]
                data_dict["volume"] = row.volume if hasattr(row, "volume") else row[5]
                data_dicts.append(data_dict)

        data = pd.DataFrame(data_dicts)

        if len(data) == 0:
            print("No data found to visualize")
            return

        data["time"] = pd.to_datetime(data["time"])
        data.set_index("time", inplace=True)

        # Optional: Manual gap filling with pandas if fill_gaps is True
        if fill_gaps and len(data) > 1:
            print("Filling gaps using pandas interpolation...")
            # Get the minimum time interval in the data
            min_interval = min(
                data.index[i] - data.index[i - 1] for i in range(1, len(data.index))
            )

            # Create a continuous time range with the detected interval
            full_range = pd.date_range(
                start=data.index.min(),
                end=data.index.max(),
                freq=pd.to_timedelta(min_interval),
            )

            # Reindex and fill forward
            data = data.reindex(full_range).ffill()
            print(f"After filling gaps: {len(data)} data points")

        # 5. Create plot
        plt.figure(figsize=(12, 8))

        # Price plot
        plt.subplot(2, 1, 1)
        plt.plot(data.index, data["close"], label="Close Price")
        plt.title(f"{symbol} - {period} ({interval} intervals)")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()

        # Volume plot
        plt.subplot(2, 1, 2)
        plt.bar(data.index, data["volume"], label="Volume", color="green", alpha=0.6)
        plt.ylabel("Volume")
        plt.grid(True)
        plt.legend()

        plt.tight_layout()

        # 6. Save and show plot
        filename = f"{symbol}_{period}_{interval}.png"
        plt.savefig(filename)
        print(f"Plot saved to {filename}")
        plt.show()


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print(
            "Usage: python -m scripts.visualize_historical_data SYMBOL [PERIOD] "
            "[INTERVAL]"
        )
        print("  SYMBOL: Instrument symbol (e.g., AAPL)")
        print("  PERIOD: Time period (1w, 1m, 3m, 6m, 1y) - default: 1m")
        print("  INTERVAL: Data interval (1m, 5m, 15m, 30m, 1h, 1d) - default: 1d")
        sys.exit(1)

    symbol = sys.argv[1]
    period = sys.argv[2] if len(sys.argv) > 2 else "1m"
    interval = sys.argv[3] if len(sys.argv) > 3 else "1d"

    # Added message about Apache license limitations
    print(
        "Note: Using Apache license-compatible query (no gap filling with "
        "TimescaleDB)."
    )
    print("Gaps in data will be visible in the visualization.")

    asyncio.run(visualize_historical_data(symbol, period, interval))
