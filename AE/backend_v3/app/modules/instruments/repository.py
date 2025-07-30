"""
Repository layer for the instruments module.

Provides database access methods for instrument and price history operations.
"""

from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Optional, Sequence, TypeVar

from fastcore.db import BaseRepository
from fastcore.errors.exceptions import DBError, NotFoundError
from fastcore.logging.manager import ensure_logger
from sqlalchemy import and_, delete, desc, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import aliased

from .models import Instrument, InstrumentPriceHistory, index_constituents

# Configure logger
logger = ensure_logger(None, __name__)

R = TypeVar("R")


def db_error_handler(func: Callable[..., R]) -> Callable[..., R]:
    """
    Decorator to handle database errors in repository methods.
    Logs the error and raises a DBError with the error message.
    Args:
        func (Callable[..., R]): The function to be decorated.
    Returns:
        Callable[..., R]: The decorated function.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> R:
        try:
            return await func(*args, **kwargs)
        except NotFoundError as e:
            # Do not log as error, just re-raise
            raise
        except Exception as e:
            method_name = func.__name__
            logger.error(f"Error in {method_name}: {e}")
            raise DBError(message=str(e))

    return wrapper


class InstrumentRepository(BaseRepository[Instrument]):
    """
    Repository for instrument-related database operations.
    """

    def __init__(self, session):
        super().__init__(Instrument, session)

    @db_error_handler
    async def get_by_symbol(self, symbol: str) -> Optional[Instrument]:
        """
        Get Instrument by symbol.
        Args:
            symbol (str): The symbol of the instrument.
        Returns:
            Optional[Instrument]: The Instrument object if found, else None.
        """
        stmt = select(self.model).where(self.model.symbol == symbol)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    @db_error_handler
    async def bulk_insert(self, records: list[dict]) -> list[Instrument]:
        """
        Efficiently insert multiple Instrument records in bulk using SQLAlchemy core insert.
        Args:
            records (list[dict]): List of dicts representing Instrument records.
        Returns:
            None
        """
        # stmt = insert(self.model)
        stmt = pg_insert(self.model).on_conflict_do_nothing(index_elements=["symbol"])
        await self.session.execute(stmt, records)

        # Fetch and return the inserted records by symbol
        symbols = [r["symbol"] for r in records]
        stmt = select(self.model).where(self.model.symbol.in_(symbols))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @db_error_handler
    async def bulk_upsert(self, records: list[dict]) -> list[Instrument]:
        """
        Efficiently insert or update multiple Instrument records in bulk using PostgreSQL upsert (ON CONFLICT DO UPDATE).
        Args:
            records (list[dict]): List of dicts representing Instrument records.
        Returns:
            None
        """
        stmt = pg_insert(self.model)
        stmt = stmt.on_conflict_do_update(
            index_elements=["symbol"],
            set_={
                "name": stmt.excluded.name,
                "type": stmt.excluded.type,
                "country": stmt.excluded.country,
                "currency": stmt.excluded.currency,
                "sector": stmt.excluded.sector,
                "industry": stmt.excluded.industry,
                "market": stmt.excluded.market,
                "is_active": stmt.excluded.is_active,
                "updated_at": datetime.now(timezone.utc),
            },
        )
        await self.session.execute(stmt, records)

        # Fetch and return the upserted records by symbol
        symbols = [r["symbol"] for r in records]
        stmt = select(self.model).where(self.model.symbol.in_(symbols))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @db_error_handler
    async def add_stocks_to_index(self, index_id: int, stock_ids: list[int]) -> None:
        """
        Bulk add multiple stocks to an index by inserting into the index_constituents table.
        Args:
            index_id (int): The ID of the index instrument.
            stock_ids (list[int]): List of stock instrument IDs to add as constituents.
        Returns:
            None
        """
        if not stock_ids:
            return

        stmt = (
            pg_insert(index_constituents)
            .values(
                [{"index_id": index_id, "stock_id": stock_id} for stock_id in stock_ids]
            )
            .on_conflict_do_nothing()
        )

        await self.session.execute(stmt)

    @db_error_handler
    async def remove_stocks_from_index(
        self, index_id: int, stock_ids: list[int]
    ) -> None:
        """
        Bulk remove multiple stocks from an index in the index_constituents table.
        Args:
            index_id (int): The ID of the index instrument.
            stock_ids (list[int]): List of stock instrument IDs to remove as constituents.
        Returns:
            None
        """
        if not stock_ids:
            return

        stmt = delete(index_constituents).where(
            index_constituents.c.index_id == index_id,
            index_constituents.c.stock_id.in_(stock_ids),
        )

        await self.session.execute(stmt)

    @db_error_handler
    async def add_stock_to_index(self, index_id: int, stock_id: int) -> None:
        """
        Add a stock to an index by inserting into the index_constituents table.
        Args:
            index_id (int): The ID of the index instrument.
            stock_id (int): The ID of the stock instrument.
        Returns:
            None
        """
        stmt = (
            pg_insert(index_constituents)
            .values(index_id=index_id, stock_id=stock_id)
            .on_conflict_do_nothing()
        )
        await self.session.execute(stmt)

    @db_error_handler
    async def remove_stock_from_index(self, index_id: int, stock_id: int) -> None:
        """
        Remove a stock from an index in the index_constituents table.
        Args:
            index_id (int): The ID of the index instrument.
            stock_id (int): The ID of the stock instrument.
        Returns:
            None
        """
        stmt = delete(index_constituents).where(
            index_constituents.c.index_id == index_id,
            index_constituents.c.stock_id == stock_id,
        )

        await self.session.execute(stmt)

    @db_error_handler
    async def get_constituents(self, index_id: int) -> list[Instrument]:
        """
        Get all stock constituents for a given index.
        Args:
            index_id (int): The ID of the index instrument.
        Returns:
            list[Instrument]: List of stock Instrument objects.
        """
        stmt = (
            select(Instrument)
            .join(index_constituents, Instrument.id == index_constituents.c.stock_id)
            .where(index_constituents.c.index_id == index_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @db_error_handler
    async def get_indices_for_stock(self, stock_id: int) -> list[Instrument]:
        """
        Get all indices that a given stock belongs to.
        Args:
            stock_id (int): The ID of the stock instrument.
        Returns:
            list[Instrument]: List of index Instrument objects.
        """
        stmt = (
            select(Instrument)
            .join(index_constituents, Instrument.id == index_constituents.c.index_id)
            .where(index_constituents.c.stock_id == stock_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @db_error_handler
    async def list_with_latest_price(
        self, filters: dict = None, limit: int = 100, offset: int = 0
    ) -> list[tuple]:
        """
        List instruments with their latest price.
        Args:
            filters (dict): Filters to apply on the instrument query.
            limit (int): Number of records to fetch.
            offset (int): Offset for pagination.
        Returns:
            list[tuple]: List of tuples containing Instrument and its latest price.
        """
        # Subquery to get latest price per instrument
        subq = (
            select(
                InstrumentPriceHistory.instrument_id,
                func.max(InstrumentPriceHistory.market_timestamp).label("latest_ts"),
            )
            .group_by(InstrumentPriceHistory.instrument_id)
            .subquery()
        )

        # Join instruments with their latest price
        price_alias = aliased(InstrumentPriceHistory)
        stmt = (
            select(
                Instrument,
                price_alias.price,
                price_alias.market_timestamp,
                # Add any other fields you want to select
                price_alias.change,
                price_alias.change_percent,
                price_alias.volume,
                price_alias.day_high,
                price_alias.day_low,
                price_alias.w52_high,
                price_alias.w52_low,
                price_alias.previous_close,
            )
            .outerjoin(subq, Instrument.id == subq.c.instrument_id)
            .outerjoin(
                price_alias,
                (price_alias.instrument_id == Instrument.id)
                & (price_alias.market_timestamp == subq.c.latest_ts),
            )
        )

        # Apply filters if any (as in your list method)
        if filters:
            for k, v in filters.items():
                if hasattr(Instrument, k):
                    stmt = stmt.where(getattr(Instrument, k) == v)

        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        # Each row: (Instrument, price_alias)
        return result.all()


class InstrumentPriceHistoryRepository(BaseRepository[InstrumentPriceHistory]):
    """
    Repository for instrument price history (time series) operations.
    """

    def __init__(self, session):
        super().__init__(InstrumentPriceHistory, session)

    # ===========================================================================================================

    # InstrumentPriceHistory has a composite primary key (instrument_id, market_timestamp)
    # so we need to override the get_by_id, update, and delete methods

    @db_error_handler
    async def get_by_id(
        self,
        instrument_id: int,
        market_timestamp: datetime,
    ) -> Optional[InstrumentPriceHistory]:
        """
        Get InstrumentPriceHistory by instrument_id and market_timestamp.
        Args:
            instrument_id (int): The ID of the instrument.
            market_timestamp (datetime): The market timestamp.
        Returns:
            Optional[InstrumentPriceHistory]: The InstrumentPriceHistory object if found, else None.
        Raises:
            NotFoundError: If the record with the specified keys doesn't exist.
        """
        stmt = select(self.model).where(
            self.model.instrument_id == instrument_id,
            self.model.market_timestamp == market_timestamp,
        )
        result = await self.session.execute(stmt)
        record = result.scalars().first()

        if record is None:
            raise NotFoundError(
                resource_type=self.model.__name__,
                resource_id=f"instrument_id={instrument_id}, timestamp={market_timestamp}",
            )

        return record

    @db_error_handler
    async def update(
        self,
        instrument_id: int,
        market_timestamp: datetime,
        data: dict,
    ) -> InstrumentPriceHistory:
        """
        Update an InstrumentPriceHistory record by composite key (instrument_id, market_timestamp).
        Args:
            instrument_id (int): The ID of the instrument.
            market_timestamp (datetime): The market timestamp.
            data (dict): Dict containing fields to update.
        Returns:
            InstrumentPriceHistory: The updated InstrumentPriceHistory object.
        Raises:
            NotFoundError: If the record with the specified keys doesn't exist.
        """
        record = await self.get_by_id(instrument_id, market_timestamp)

        for key, value in data.items():
            setattr(record, key, value)

        await self.session.flush()
        return record

    @db_error_handler
    async def delete(
        self,
        instrument_id: int,
        market_timestamp: datetime,
    ) -> None:
        """
        Delete an InstrumentPriceHistory record by composite key (instrument_id, market_timestamp).
        Args:
            instrument_id (int): The ID of the instrument.
            market_timestamp (datetime): The market timestamp.
        Returns:
            None
        """
        record = await self.get_by_id(instrument_id, market_timestamp)

        await self.session.delete(record)
        await self.session.flush()

    # ===========================================================================================================

    @db_error_handler
    async def get_latest_price(
        self, instrument_id: int
    ) -> Optional[InstrumentPriceHistory]:
        """
        Get the latest price for a given instrument.
        Args:
            instrument_id (int): The ID of the instrument.
        Returns:
            Optional[InstrumentPriceHistory]: The latest InstrumentPriceHistory object if found, else None.
        """
        stmt = (
            select(self.model)
            .where(self.model.instrument_id == instrument_id)
            .order_by(desc(self.model.market_timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    @db_error_handler
    async def get_prices_in_range(
        self, instrument_id: int, start: datetime, end: datetime
    ) -> Sequence[InstrumentPriceHistory]:
        """
        Get price history records for a given instrument within a date range.
        Args:
            instrument_id (int): The ID of the instrument.
            start (datetime): Start date for the range.
            end (datetime): End date for the range.
        Returns:
            Sequence[InstrumentPriceHistory]: List of InstrumentPriceHistory objects within the date range.
        """
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.instrument_id == instrument_id,
                    self.model.market_timestamp >= start,
                    self.model.market_timestamp <= end,
                )
            )
            .order_by(self.model.market_timestamp)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @db_error_handler
    async def bulk_insert(self, records: list[dict]) -> None:
        """
        Efficiently insert multiple InstrumentPriceHistory records in bulk using SQLAlchemy core insert.
        Args:
            records (list[dict]): List of dicts representing InstrumentPriceHistory records.
        Returns:
            None
        """
        # stmt = insert(self.model)
        stmt = pg_insert(self.model).on_conflict_do_nothing(
            index_elements=["instrument_id", "market_timestamp"]
        )

        await self.session.execute(stmt, records)

    @db_error_handler
    async def bulk_upsert(self, records: list[dict]) -> None:
        """
        Efficiently insert or update multiple InstrumentPriceHistory records in bulk using PostgreSQL upsert (ON CONFLICT DO UPDATE).
        Args:
            records (list[dict]): List of dicts representing InstrumentPriceHistory records.
        Returns:
            None
        """
        stmt = pg_insert(self.model)
        stmt = stmt.on_conflict_do_update(
            index_elements=["instrument_id", "market_timestamp"],
            set_={
                "price": stmt.excluded.price,
                "change": stmt.excluded.change,
                "change_percent": stmt.excluded.change_percent,
                "volume": stmt.excluded.volume,
                "day_high": stmt.excluded.day_high,
                "day_low": stmt.excluded.day_low,
                "previous_close": stmt.excluded.previous_close,
                "w52_high": stmt.excluded.w52_high,
                "w52_low": stmt.excluded.w52_low,
                "updated_at": datetime.now(timezone.utc),
            },
        )
        await self.session.execute(stmt, records)
