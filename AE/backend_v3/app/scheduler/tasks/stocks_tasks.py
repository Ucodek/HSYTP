import asyncio
from typing import List

from fastcore.db.engine import SessionLocal
from fastcore.logging.manager import ensure_logger

from app.clients.market_data_client import MarketDataClient
from app.modules.instruments.models import InstrumentType
from app.modules.instruments.schemas import InstrumentCreate, InstrumentResponse
from app.modules.instruments.service import InstrumentService

# Configure logger
logger = ensure_logger(None, __name__)

CHUNK_SIZE = 500  #


def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


async def create_market_stocks():
    """
    Create or update all stocks for all unique exchanges found in indices using MarketDataClient.
    Fetches all stock instrument info for each exchange, and creates or updates them in the database.
    """
    async with SessionLocal() as session:
        service: InstrumentService = InstrumentService(session)

        indices: List[InstrumentResponse] = await service.list(
            filters={"type": InstrumentType.INDEX}
        )
        logger.info(f"Found {len(indices)} indices to find stocks for")

        for index in indices:
            try:
                market = index.market.value.upper()
                symbol = index.symbol.split(".")[0].replace("^", "")

                market_symbol = f"{market};{symbol}"

                data = await asyncio.to_thread(
                    MarketDataClient.get_stocks_by_index,
                    index_symbol=market_symbol,
                )

                if not data:
                    logger.warning(f"No market data for {index.symbol}")
                    continue

                # Process the data and create or update stocks in the database
                stocks_data = [InstrumentCreate(**stock) for stock in data]
                # await service.bulk_insert(stocks_data)
                # upserted_stocks = await service.bulk_upsert(stocks_data)

                upserted_stocks = []
                for chunk in chunked(stocks_data, CHUNK_SIZE):
                    upserted_stocks.extend(await service.bulk_upsert(chunk))

                # After successful insertion, add the stocks to related indices
                stock_ids = [stock.id for stock in upserted_stocks]
                # await service.add_stocks_to_index(index.id, stock_ids)
                for chunk in chunked(stock_ids, CHUNK_SIZE):
                    await service.add_stocks_to_index(index.id, chunk)

                logger.info(
                    f"Inserted {len(upserted_stocks)} stocks for index {index.symbol}"
                )
            except Exception as e:
                logger.error(
                    f"Error fetching stocks for index {index.symbol}: {str(e)}"
                )
