import asyncio
from typing import List

from fastcore.db.engine import SessionLocal
from fastcore.errors.exceptions import NotFoundError
from fastcore.logging.manager import ensure_logger

from app.clients.market_data_client import MarketDataClient
from app.modules.instruments.models import InstrumentType
from app.modules.instruments.schemas import (
    InstrumentPriceHistoryCreate,
    InstrumentResponse,
)
from app.modules.instruments.service import (
    InstrumentPriceHistoryService,
    InstrumentService,
)

# Configure logger
logger = ensure_logger(None, __name__)

MAX_CONCURRENT = 10
CHUNK_SIZE = 500


def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


async def process_instrument(instrument: InstrumentResponse) -> None:
    """
    Fetch and upsert the latest price history for a single instrument.
    If the price record for the current timestamp does not exist, it is created.
    Handles NotFoundError for missing records and logs all actions and errors.
    Args:
        instrument (InstrumentResponse): The instrument to process.
    """
    async with SessionLocal() as session:
        service: InstrumentPriceHistoryService = InstrumentPriceHistoryService(session)

        try:
            data = await asyncio.to_thread(
                MarketDataClient.get_latest_market_data,
                symbol=instrument.symbol,
                period="7d",
            )

            if not data:
                logger.warning(f"No market data for {instrument.symbol}")
                return

            current_timestamp = data["market_timestamp"]

            existing_record = await service.get(instrument.id, current_timestamp)

            if existing_record:
                logger.info(
                    f"Price record already exists for {instrument.symbol} at {current_timestamp}, skipping"
                )
                return

        except NotFoundError:
            price_history = InstrumentPriceHistoryCreate.from_raw_data(
                instrument_id=instrument.id,
                data=data,
            )

            await service.create(price_history)
            logger.info(f"Updated price for {instrument.symbol}: {data['price']}")

        except Exception as e:
            logger.error(f"Error updating price for {instrument.symbol}: {str(e)}")


async def update_instrument_prices(filters=None) -> None:
    """
    Update the latest price history for all instruments matching the given filters.
    Processes instruments in parallel with a concurrency limit.
    Args:
        filters (dict, optional): Filtering criteria for instruments (e.g., type).
    """
    async with SessionLocal() as session:
        service: InstrumentService = InstrumentService(session)

        instruments: List[InstrumentResponse] = await service.list(filters)
        logger.info(f"Found {len(instruments)} instruments to update")

        semaphore = asyncio.Semaphore(MAX_CONCURRENT)

        async def sem_task(inst):
            async with semaphore:
                await process_instrument(inst)

        await asyncio.gather(*(sem_task(inst) for inst in instruments))


async def process_backfill(
    instrument: InstrumentResponse, period="5y", interval="1d"
) -> None:
    """
    Fetch and upsert historical price history for a single instrument.
    Uses chunking for bulk inserts. Logs all actions and errors.
    Args:
        instrument (InstrumentResponse): The instrument to process.
        period (str): The period for historical data (default: "5y").
        interval (str): The interval for historical data (default: "1d").
    """
    async with SessionLocal() as session:
        service: InstrumentPriceHistoryService = InstrumentPriceHistoryService(session)

        try:
            history = await asyncio.to_thread(
                MarketDataClient.get_historical_data,
                instrument.symbol,
                period,
                interval,
            )

            if not history:
                logger.warning(f"No historical data for {instrument.symbol}")
                return

            history_to_insert = [
                InstrumentPriceHistoryCreate.from_raw_data(
                    instrument_id=instrument.id, data=data
                )
                for data in history
            ]

            for chunk in chunked(history_to_insert, CHUNK_SIZE):
                await service.bulk_insert(chunk)
                logger.info(f"Inserted {len(chunk)} records for {instrument.symbol}")

        except Exception as e:
            logger.error(f"Error backfilling {instrument.symbol}: {str(e)}")


async def backfill_instrument_price_history(
    filters=None, period="5y", interval="1d"
) -> None:
    """
    Backfill historical price history for all instruments matching the given filters.
    Processes instruments in parallel with a concurrency limit and uses chunking for bulk inserts.
    Args:
        filters (dict, optional): Filtering criteria for instruments (e.g., type).
        period (str): The period for historical data (default: "5y").
        interval (str): The interval for historical data (default: "1d").
    """
    async with SessionLocal() as session:
        service: InstrumentService = InstrumentService(session)

        instruments: List[InstrumentResponse] = await service.list(filters)
        logger.info(f"Backfilling historical data for {len(instruments)} instruments")

        semaphore = asyncio.Semaphore(MAX_CONCURRENT)

        async def sem_task(inst):
            async with semaphore:
                await process_backfill(inst, period, interval)

        await asyncio.gather(*(sem_task(inst) for inst in instruments))


async def update_index_prices() -> None:
    """
    Update the latest price history for all index instruments.
    """
    await update_instrument_prices(filters={"type": InstrumentType.INDEX})


async def backfill_index_price_history() -> None:
    """
    Backfill historical price history for all index instruments.
    """
    await backfill_instrument_price_history(
        filters={"type": InstrumentType.INDEX},
    )


async def update_stock_prices() -> None:
    """
    Update the latest price history for all stock instruments.
    """
    await update_instrument_prices(filters={"type": InstrumentType.STOCK})


async def backfill_stock_price_history() -> None:
    """
    Backfill historical price history for all stock instruments.
    """
    await backfill_instrument_price_history(
        filters={"type": InstrumentType.STOCK},
    )
