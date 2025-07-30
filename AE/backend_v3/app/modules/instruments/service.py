"""
Service layer for the instruments module.

Handles business logic and transaction management for instruments and price history.
"""
from datetime import datetime
from typing import List, Optional

from fastcore.cache import cache
from fastcore.cache.manager import get_cache
from fastcore.errors.exceptions import ConflictError, NotFoundError, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import InstrumentPriceHistoryRepository, InstrumentRepository
from .schemas import (
    InstrumentCreate,
    InstrumentPriceHistoryCreate,
    InstrumentPriceHistoryResponse,
    InstrumentPriceHistoryUpdate,
    InstrumentResponse,
    InstrumentUpdate,
    InstrumentWithLatestPriceResponse,
)


class InstrumentService:
    """
    Service for managing financial instruments.

    Provides business logic for creating, retrieving, updating, deleting, and listing instruments.
    Handles transaction management and error handling.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the InstrumentService.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
        """
        self.session = session
        self.repo = InstrumentRepository(session)

    async def create(self, data: InstrumentCreate) -> InstrumentResponse:
        """
        Create a new instrument.

        Args:
            data (InstrumentCreate): The instrument creation data.
        Raises:
            ConflictError: If an instrument with the same symbol already exists.
            ValidationError: If creation fails due to invalid data or DB error.
        Returns:
            InstrumentResponse: The created instrument.
        """
        existing = await self.repo.get_by_symbol(data.symbol)
        if existing:
            raise ConflictError("Instrument with this symbol already exists.")
        try:
            instrument = await self.repo.create(data.model_dump())
            await self.session.commit()
            await self.session.refresh(instrument)

            # invalidate cache for the list of instruments
            cache_client = await get_cache()
            await cache_client.clear("instruments:list:")
            await cache_client.clear("instruments:count:")

            return InstrumentResponse.model_validate(instrument)
        except Exception as e:
            raise ValidationError(f"Failed to create instrument: {e}")

    @cache(ttl=300, prefix="instruments:by_id:")
    async def get(self, instrument_id: int) -> InstrumentResponse:
        """
        Retrieve an instrument by its ID.

        Args:
            instrument_id (int): The instrument's ID.
        Raises:
            NotFoundError: If the instrument does not exist.
        Returns:
            InstrumentResponse: The instrument data.
        """
        instrument = await self.repo.get_by_id(instrument_id)
        if not instrument:
            raise NotFoundError("Instrument not found")
        return InstrumentResponse.model_validate(instrument)

    @cache(ttl=300, prefix="instruments:by_symbol:")
    async def get_by_symbol(self, symbol: str) -> InstrumentResponse:
        """
        Retrieve an instrument by its symbol.

        Args:
            symbol (str): The instrument's symbol.
        Raises:
            NotFoundError: If the instrument does not exist.
        Returns:
            InstrumentResponse: The instrument data.
        """
        instrument = await self.repo.get_by_symbol(symbol)
        if not instrument:
            raise NotFoundError("Instrument not found")
        return InstrumentResponse.model_validate(instrument)

    @cache(ttl=120, prefix="instruments:list:")
    async def list(
        self, filters: Optional[dict] = None, offset: int = 0, limit: int = 100
    ) -> List[InstrumentResponse]:
        """
        List instruments with optional filters and pagination.

        Args:
            filters (dict, optional): Filtering criteria.
            offset (int): Pagination offset.
            limit (int): Pagination limit.
        Returns:
            List[InstrumentResponse]: List of instruments.
        """
        instruments = await self.repo.list(filters=filters, offset=offset, limit=limit)
        return [InstrumentResponse.model_validate(i) for i in instruments]

    @cache(ttl=120, prefix="instruments:count:")
    async def count(self, filters: Optional[dict] = None) -> int:
        """
        Return the total number of instruments, optionally filtered.

        Args:
            filters (dict, optional): Filtering criteria.
        Returns:
            int: Total number of matching instruments.
        """
        return await self.repo.count(filters=filters)

    async def update(
        self, instrument_id: int, data: InstrumentUpdate
    ) -> InstrumentResponse:
        """
        Update an existing instrument.

        Args:
            instrument_id (int): The instrument's ID.
            data (InstrumentUpdate): The update data.
        Raises:
            NotFoundError: If the instrument does not exist.
            ValidationError: If update fails due to invalid data or DB error.
        Returns:
            InstrumentResponse: The updated instrument.
        """
        instrument = await self.repo.get_by_id(instrument_id)
        if not instrument:
            raise NotFoundError("Instrument not found")
        try:
            updated = await self.repo.update(
                instrument_id, data.model_dump(exclude_unset=True)
            )
            await self.session.commit()
            await self.session.refresh(updated)

            # invalidate cache for the list of instruments
            cache_client = await get_cache()
            await cache_client.clear("instruments:list:")
            await cache_client.clear("instruments:by_id:")
            await cache_client.clear("instruments:by_symbol:")

            return InstrumentResponse.model_validate(updated)
        except Exception as e:
            raise ValidationError(f"Failed to update instrument: {e}")

    async def delete(self, instrument_id: int) -> None:
        """
        Delete an instrument by its ID.

        Args:
            instrument_id (int): The instrument's ID.
        """
        await self.repo.delete(instrument_id)
        await self.session.commit()

        # invalidate cache for the list of instruments
        cache_client = await get_cache()
        await cache_client.clear("instruments:list:")
        await cache_client.clear("instruments:by_id:")
        await cache_client.clear("instruments:by_symbol:")
        await cache_client.clear("instruments:count:")

    async def bulk_insert(
        self, records: List[InstrumentCreate]
    ) -> List[InstrumentResponse]:
        """
        Bulk insert multiple instruments efficiently.

        Args:
            records (list[InstrumentCreate]): List of instrument creation data.
        """
        dicts = [r.model_dump() for r in records]
        instruments = await self.repo.bulk_insert(dicts)
        await self.session.commit()

        # Invalidate cache for the list of instruments
        cache_client = await get_cache()
        await cache_client.clear("instruments:list:")
        await cache_client.clear("instruments:count:")

        # return instruments
        return [InstrumentResponse.model_validate(i) for i in instruments]

    async def bulk_upsert(
        self, records: List[InstrumentCreate]
    ) -> List[InstrumentResponse]:
        """
        Bulk upsert multiple instruments efficiently.

        Args:
            records (list[InstrumentCreate]): List of instrument creation data.
        """
        dicts = [r.model_dump() for r in records]
        instruments = await self.repo.bulk_upsert(dicts)
        await self.session.commit()

        # Invalidate cache for the list of instruments
        cache_client = await get_cache()
        await cache_client.clear("instruments:list:")
        await cache_client.clear("instruments:count:")

        return [InstrumentResponse.model_validate(i) for i in instruments]

    async def add_stock_to_index(self, index_id: int, stock_id: int) -> None:
        """
        Add a stock to an index.
        Args:
            index_id (int): The ID of the index instrument.
            stock_id (int): The ID of the stock instrument.
        """
        await self.repo.add_stock_to_index(index_id, stock_id)
        await self.session.commit()

        # Invalidate cache for the list of indices
        cache_client = await get_cache()
        await cache_client.clear("instruments:indices:")
        await cache_client.clear("instruments:constituents:")

    async def add_stocks_to_index(self, index_id: int, stock_ids: List[int]) -> None:
        """
        Bulk add multiple stocks to an index.
        Args:
            index_id (int): The ID of the index instrument.
            stock_ids (list[int]): List of stock instrument IDs to add as constituents.
        """
        await self.repo.add_stocks_to_index(index_id, stock_ids)
        await self.session.commit()

        # Invalidate cache for the list of indices
        cache_client = await get_cache()
        await cache_client.clear("instruments:indices:")
        await cache_client.clear("instruments:constituents:")

    async def remove_stock_from_index(self, index_id: int, stock_id: int) -> None:
        """
        Remove a stock from an index.
        Args:
            index_id (int): The ID of the index instrument.
            stock_id (int): The ID of the stock instrument.
        """
        await self.repo.remove_stock_from_index(index_id, stock_id)
        await self.session.commit()

        # Invalidate cache for the list of indices
        cache_client = await get_cache()
        await cache_client.clear("instruments:indices:")
        await cache_client.clear("instruments:constituents:")

    async def remove_stocks_from_index(
        self, index_id: int, stock_ids: List[int]
    ) -> None:
        """
        Bulk remove multiple stocks from an index.
        Args:
            index_id (int): The ID of the index instrument.
            stock_ids (list[int]): List of stock instrument IDs to remove as constituents.
        """
        await self.repo.remove_stocks_from_index(index_id, stock_ids)
        await self.session.commit()

        # Invalidate cache for the list of indices
        cache_client = await get_cache()
        await cache_client.clear("instruments:indices:")
        await cache_client.clear("instruments:constituents:")

    @cache(ttl=1800, prefix="instruments:constituents:")
    async def get_constituents(self, index_id: int) -> List[InstrumentResponse]:
        """
        Get all stock constituents for a given index.
        Args:
            index_id (int): The ID of the index instrument.
        Returns:
            list[InstrumentResponse]: List of stock InstrumentResponse objects.
        """
        stocks = await self.repo.get_constituents(index_id)
        return [InstrumentResponse.model_validate(s) for s in stocks]

    @cache(ttl=1800, prefix="instruments:indices:")
    async def get_indices_for_stock(self, stock_id: int) -> List[InstrumentResponse]:
        """
        Get all indices that a given stock belongs to.
        Args:
            stock_id (int): The ID of the stock instrument.
        Returns:
            list[InstrumentResponse]: List of index InstrumentResponse objects.
        """
        indices = await self.repo.get_indices_for_stock(stock_id)
        return [InstrumentResponse.model_validate(i) for i in indices]

    @cache(ttl=60, prefix="instruments:list_with_latest_price:")
    async def list_with_latest_price(
        self, filters: Optional[dict] = None, offset: int = 0, limit: int = 100
    ) -> List[InstrumentWithLatestPriceResponse]:
        """
        List instruments with their latest price and price info.

        Args:
            filters (dict, optional): Filtering criteria.
            offset (int): Pagination offset.
            limit (int): Pagination limit.
        Returns:
            List[InstrumentWithLatestPriceResponse]: List of instruments with latest price info.
        """
        rows = await self.repo.list_with_latest_price(
            filters=filters, limit=limit, offset=offset
        )
        result = []
        for (
            instrument,
            price,
            market_timestamp,
            change,
            change_percent,
            volume,
            day_high,
            day_low,
            w52_high,
            w52_low,
            previous_close,
        ) in rows:
            result.append(
                InstrumentWithLatestPriceResponse(
                    id=instrument.id,
                    symbol=instrument.symbol,
                    name=instrument.name,
                    type=instrument.type,
                    market=instrument.market,
                    currency=instrument.currency,
                    country=instrument.country,
                    sector=instrument.sector,
                    industry=instrument.industry,
                    is_active=instrument.is_active,
                    created_at=instrument.created_at,
                    updated_at=instrument.updated_at,
                    price=price,
                    market_timestamp=market_timestamp,
                    change=change,
                    change_percent=change_percent,
                    volume=volume,
                    day_high=day_high,
                    day_low=day_low,
                    w52_high=w52_high,
                    w52_low=w52_low,
                    previous_close=previous_close,
                )
            )

        return result


class InstrumentPriceHistoryService:
    """
    Service for managing instrument price history (time series).

    Provides business logic for creating, retrieving, updating, deleting, listing, and bulk inserting price history records.
    Handles transaction management and error handling.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the InstrumentPriceHistoryService.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
        """
        self.session = session
        self.repo = InstrumentPriceHistoryRepository(session)

    async def create(
        self,
        data: InstrumentPriceHistoryCreate,
    ) -> InstrumentPriceHistoryResponse:
        """
        Create a new price history record.

        Args:
            data (InstrumentPriceHistoryCreate): The price history creation data.
        Raises:
            ValidationError: If creation fails due to invalid data or DB error.
        Returns:
            InstrumentPriceHistoryResponse: The created price history record.
        """
        try:
            record = await self.repo.create(data.model_dump())
            await self.session.commit()
            await self.session.refresh(record)

            # Invalidate cache for the latest price
            cache_client = await get_cache()
            await cache_client.clear(f"price_history:latest:{data.instrument_id}")
            await cache_client.clear(f"price_history:in_range:{data.instrument_id}")
            await cache_client.clear(f"price_history:list:")
            await cache_client.clear(f"price_history:count:")

            return InstrumentPriceHistoryResponse.model_validate(record)
        except Exception as e:
            raise ValidationError(f"Failed to create price history: {e}")

    async def get(
        self,
        instrument_id: int,
        market_timestamp: datetime,
    ) -> InstrumentPriceHistoryResponse:
        """
        Retrieve a price history record by its composite key (instrument_id, market_timestamp).

        Args:
            instrument_id (int): The instrument's ID.
            market_timestamp (datetime): The market timestamp.
        Raises:
            NotFoundError: If the record does not exist.
        Returns:
            InstrumentPriceHistoryResponse: The price history data.
        """
        record = await self.repo.get_by_id(instrument_id, market_timestamp)
        return InstrumentPriceHistoryResponse.model_validate(record)

    @cache(ttl=1800, prefix="price_history:list:")
    async def list(
        self,
        filters: Optional[dict] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[InstrumentPriceHistoryResponse]:
        """
        List price history records with optional filters and pagination.

        Args:
            filters (dict, optional): Filtering criteria.
            offset (int): Pagination offset.
            limit (int): Pagination limit.
        Returns:
            List[InstrumentPriceHistoryResponse]: List of price history records.
        """
        records = await self.repo.list(filters=filters, offset=offset, limit=limit)
        return [InstrumentPriceHistoryResponse.model_validate(r) for r in records]

    @cache(ttl=1800, prefix="price_history:count:")
    async def count(self, filters: Optional[dict] = None) -> int:
        """
        Return the total number of price history records, optionally filtered.

        Args:
            filters (dict, optional): Filtering criteria.
        Returns:
            int: Total number of matching price history records.
        """
        return await self.repo.count(filters=filters)

    @cache(ttl=60, prefix="price_history:latest:")
    async def get_latest_price(
        self,
        instrument_id: int,
    ) -> Optional[InstrumentPriceHistoryResponse]:
        """
        Retrieve the latest price history record for a given instrument.

        Args:
            instrument_id (int): The instrument's ID.
        Returns:
            Optional[InstrumentPriceHistoryResponse]: The latest price history record, or None if not found.
        """
        record = await self.repo.get_latest_price(instrument_id)

        if not record:
            return None

        return InstrumentPriceHistoryResponse.model_validate(record)

    @cache(ttl=1800, prefix="price_history:in_range:")
    async def get_prices_in_range(
        self,
        instrument_id: int,
        start: datetime = None,
        end: datetime = None,
    ) -> List[InstrumentPriceHistoryResponse]:
        """
        Retrieve price history records for an instrument within a date range.

        Args:
            instrument_id (int): The instrument's ID.
            start: Start datetime.
            end: End datetime.
        Returns:
            List[InstrumentPriceHistoryResponse]: List of price history records in the range.
        """
        records = await self.repo.get_prices_in_range(instrument_id, start, end)
        return [InstrumentPriceHistoryResponse.model_validate(r) for r in records]

    async def bulk_insert(self, records: List[InstrumentPriceHistoryCreate]) -> None:
        """
        Bulk insert multiple price history records efficiently.

        Args:
            records (list[InstrumentPriceHistoryCreate]): List of price history creation data.
        """
        dicts = [r.model_dump() for r in records]
        await self.repo.bulk_insert(dicts)
        await self.session.commit()

        # Invalidate cache for the latest price
        cache_client = await get_cache()
        await cache_client.clear("price_history:latest:")
        await cache_client.clear("price_history:in_range:")
        await cache_client.clear("price_history:list:")
        await cache_client.clear("price_history:count:")

    async def bulk_upsert(self, records: List[InstrumentPriceHistoryCreate]) -> None:
        """
        Bulk upsert multiple price history records efficiently.

        Args:
            records (list[InstrumentPriceHistoryCreate]): List of price history creation data.
        """
        dicts = [r.model_dump() for r in records]
        await self.repo.bulk_upsert(dicts)
        await self.session.commit()

        # Invalidate cache for the latest price
        cache_client = await get_cache()
        await cache_client.clear("price_history:latest:")
        await cache_client.clear("price_history:in_range:")
        await cache_client.clear("price_history:list:")
        await cache_client.clear("price_history:count:")

    async def update(
        self,
        instrument_id: int,
        market_timestamp: datetime,
        data: InstrumentPriceHistoryUpdate,
    ) -> InstrumentPriceHistoryResponse:
        """
        Update an existing price history record.

        Args:
            instrument_id (int): The instrument's ID.
            market_timestamp (datetime): The market timestamp.
            data (InstrumentPriceHistoryUpdate): The update data.
        Raises:
            NotFoundError: If the record does not exist.
            ValidationError: If update fails due to invalid data or DB error.
        Returns:
            InstrumentPriceHistoryResponse: The updated price history record.
        """
        try:
            updated = await self.repo.update(
                instrument_id,
                market_timestamp,
                data.model_dump(exclude_unset=True),
            )
            await self.session.commit()
            await self.session.refresh(updated)
            return InstrumentPriceHistoryResponse.model_validate(updated)
        except NotFoundError:
            raise
        except Exception as e:
            raise ValidationError(f"Failed to update price history: {e}")

    async def delete(
        self,
        instrument_id: int,
        market_timestamp: datetime,
    ) -> None:
        """
        Delete a price history record by its composite key.

        Args:
            instrument_id (int): The instrument's ID.
            market_timestamp (datetime): The market timestamp.
        """
        await self.repo.delete(instrument_id, market_timestamp)
        await self.session.commit()

        # Invalidate cache for the latest price
        cache_client = await get_cache()
        await cache_client.clear("price_history:latest:")
        await cache_client.clear("price_history:in_range:")
        await cache_client.clear("price_history:list:")
        await cache_client.clear("price_history:count:")
