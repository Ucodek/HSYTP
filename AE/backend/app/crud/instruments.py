from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.instruments import Instrument
from app.schemas.instruments import InstrumentCreate, InstrumentUpdate


class CRUDInstrument(CRUDBase[Instrument, InstrumentCreate, InstrumentUpdate]):
    async def get_by_symbol(
        self, db: AsyncSession, symbol: str
    ) -> Optional[Instrument]:
        """Get an instrument by its symbol."""
        query = select(self.model).where(self.model.symbol == symbol)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_symbols(
        self, db: AsyncSession, symbols: List[str]
    ) -> List[Instrument]:
        """Get multiple instruments by their symbols."""
        query = select(self.model).where(self.model.symbol.in_(symbols))
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, type: str, skip: int = 0, limit: int = 100
    ) -> List[Instrument]:
        """Get instruments by type (stock, index, crypto, etf)."""
        query = (
            select(self.model).where(self.model.type == type).offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_country(
        self, db: AsyncSession, country: str, skip: int = 0, limit: int = 100
    ) -> List[Instrument]:
        """Get instruments by country code."""
        query = (
            select(self.model)
            .where(self.model.country == country)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


# Create a singleton instance
instrument = CRUDInstrument(Instrument)
