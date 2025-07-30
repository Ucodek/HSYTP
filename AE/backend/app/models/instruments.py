from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class Instrument(BaseModel):
    """Model for financial instruments like stocks, indices, cryptos, etc."""

    __tablename__ = "instruments"

    symbol = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(JSONB, nullable=False)  # Multilingual support
    type = Column(String(10), nullable=False, index=True)  # stock, index, crypto, etf
    country = Column(String(3), nullable=True, index=True)
    currency = Column(String(3), nullable=True)
    description = Column(JSONB, nullable=True)  # Multilingual support
    sector = Column(String(50), nullable=True)
    industry = Column(String(50), nullable=True)

    # Relationship with price
    price = relationship("InstrumentPrice", uselist=False, back_populates="instrument")


class InstrumentPrice(BaseModel):
    """Model for storing the latest prices for instruments."""

    __tablename__ = "instrument_prices"

    # Change primary key structure - use id as primary key
    id = Column(Integer, primary_key=True)  # Add explicit id column as primary key
    instrument_id = Column(
        Integer,
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Each instrument has only one price record
        index=True,  # Add index for faster lookups
    )
    price = Column(Numeric(18, 4), nullable=False)
    price_change = Column(Numeric(18, 4), nullable=True)
    change_percent = Column(Numeric(8, 4), nullable=True)
    volume = Column(Numeric(18, 0), nullable=True)
    data_timestamp = Column(Text, nullable=False)

    # Relationship with instrument
    instrument = relationship("Instrument", back_populates="price")
