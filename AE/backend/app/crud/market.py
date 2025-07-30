from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.instruments import Instrument, InstrumentPrice
from app.models.market import MarketIndex
from app.schemas.market import MarketIndexCreate, MarketIndexUpdate


class CRUDMarketIndex(CRUDBase[MarketIndex, MarketIndexCreate, MarketIndexUpdate]):
    """CRUD operations for market indices."""

    def _add_price_join(self, query):
        """Add standard price join to a query."""
        return query.options(joinedload(self.model.price))

    async def get_by_symbol(
        self, db: AsyncSession, *, symbol: str
    ) -> Optional[MarketIndex]:
        """Get a market index by symbol."""
        query = select(self.model).where(self.model.symbol == symbol)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_with_price(
        self, db: AsyncSession, *, market_index_id: int
    ) -> Optional[MarketIndex]:
        """Get a market index with its latest price."""
        query = self._add_price_join(
            select(self.model).where(self.model.id == market_index_id)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_symbol_with_price(
        self, db: AsyncSession, *, symbol: str
    ) -> Optional[MarketIndex]:
        """Get a market index by symbol with its latest price."""
        query = (
            select(self.model)
            .options(joinedload(self.model.price))
            .where(self.model.symbol == symbol)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[MarketIndex]:
        """Get multiple market indices with their prices."""
        # Override base method to include price relationship
        query = (
            select(self.model)
            .options(joinedload(self.model.price))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_country(
        self, db: AsyncSession, *, country: str, skip: int = 0, limit: int = 100
    ) -> List[MarketIndex]:
        """Get market indices by country with their prices."""
        query = (
            select(self.model)
            .options(joinedload(self.model.price))
            .where(self.model.country == country)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class CRUDMarketMovers:
    """Helper functions for market movers."""

    async def get_gainers(
        self, db: AsyncSession, *, limit: int = 5
    ) -> List[Instrument]:
        """Get top gainers - instruments with highest positive change percentage."""
        query = (
            select(Instrument)
            .join(InstrumentPrice, InstrumentPrice.instrument_id == Instrument.id)
            .where(InstrumentPrice.change_percent > 0)
            .order_by(desc(InstrumentPrice.change_percent))
            .options(joinedload(Instrument.price))
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_losers(self, db: AsyncSession, *, limit: int = 5) -> List[Instrument]:
        """Get top losers - instruments with lowest negative change percentage."""
        query = (
            select(Instrument)
            .join(InstrumentPrice, InstrumentPrice.instrument_id == Instrument.id)
            .where(InstrumentPrice.change_percent < 0)
            .order_by(InstrumentPrice.change_percent)
            .options(joinedload(Instrument.price))
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_most_active(
        self, db: AsyncSession, *, limit: int = 5
    ) -> List[Instrument]:
        """Get most active instruments by trading volume."""
        query = (
            select(Instrument)
            .join(InstrumentPrice, InstrumentPrice.instrument_id == Instrument.id)
            .where(InstrumentPrice.volume > 0)
            .order_by(desc(InstrumentPrice.volume))
            .options(joinedload(Instrument.price))
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


# Create singleton instances
market_index = CRUDMarketIndex(MarketIndex)
market_movers = CRUDMarketMovers()
