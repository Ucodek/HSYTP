from fastcore.db.engine import SessionLocal
from fastcore.errors.exceptions import NotFoundError
from fastcore.logging.manager import ensure_logger

from app.clients.market_data_client import MarketDataClient
from app.modules.instruments.schemas import InstrumentCreate
from app.modules.instruments.service import InstrumentService

# Configure logger
logger = ensure_logger(None, __name__)

INDEX_SYMBOLS = [
    "^GSPC",  # S&P 500
    "^IXIC",  # NASDAQ Composite
    "XU100.IS",  # BIST 100
    "^DJI",  # Dow Jones Industrial Average
]


async def create_market_indices():
    """Create or update major market indices."""
    async with SessionLocal() as session:
        service: InstrumentService = InstrumentService(session)

        for symbol in INDEX_SYMBOLS:
            try:
                # Try to get existing index
                await service.get_by_symbol(symbol)
                logger.info(f"Index '{index_data.symbol}' already exists.")
            except NotFoundError:
                # Create if not exists
                latest_data = MarketDataClient.get_latest_market_data(symbol)

                if not latest_data:
                    logger.warning(f"No market data for {symbol}")
                    continue

                index_data = InstrumentCreate(**latest_data)

                await service.create(index_data)
                logger.info(f"Created index '{index_data.symbol}'.")
