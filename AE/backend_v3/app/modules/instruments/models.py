"""
Database models for financial instruments.

Defines ORM models for instruments.
"""

import enum

from fastcore.db.base import BaseModel, metadata
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.orm import relationship


class InstrumentType(str, enum.Enum):
    """Types of financial instruments."""

    STOCK = "stock"
    ETF = "etf"
    CRYPTO = "crypto"
    INDEX = "index"
    FOREX = "forex"
    OTHER = "other"


class MarketType(str, enum.Enum):
    """Market classification."""

    NASDAQ = "nasdaq"
    NYSE = "nyse"
    BIST = "bist"
    CRYPTO = "crypto"
    FOREX = "forex"
    OTHER = "other"


index_constituents = Table(
    "index_constituents",
    metadata,
    Column(
        "index_id",
        Integer,
        ForeignKey("instruments.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "stock_id",
        Integer,
        ForeignKey("instruments.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Instrument(BaseModel):
    """
    SQLAlchemy ORM model for financial instruments.

    Attributes:
        symbol (str): Unique identifier/ticker symbol for the instrument.
        name (str): Display name of the instrument.
        type (InstrumentType): Type of financial instrument.
        market (MarketType): Market where the instrument is traded.
        currency (str): ISO currency code for the instrument.
        country (str): ISO country code (optional).
        sector (str): Business sector (optional).
        industry (str): Industry classification (optional).
        is_active (bool): Whether the instrument is active and tradable.
    """

    __tablename__ = "instruments"

    symbol = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(InstrumentType), nullable=False, index=True)
    country = Column(String(2), nullable=True, index=True)
    currency = Column(String(3), nullable=False, default="USD")
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    market = Column(Enum(MarketType), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    # price_history = relationship("InstrumentPriceHistory", backref="instrument")

    price_history = relationship(
        "InstrumentPriceHistory",
        back_populates="instrument",
        cascade="all, delete-orphan",
    )

    constituents = relationship(
        "Instrument",
        secondary="index_constituents",
        primaryjoin="Instrument.id==index_constituents.c.index_id",
        secondaryjoin="Instrument.id==index_constituents.c.stock_id",
        backref="indices",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """Return a string representation of the instrument."""
        return f"<Instrument {self.symbol} ({self.type})>"


class InstrumentPriceHistory(BaseModel):
    """
    Price history for financial instruments (time series).

    Each row represents price data at a specific timestamp.
    """

    __tablename__ = "instrument_price_history"

    id = None  # for time series, we don't need an id

    instrument_id = Column(
        Integer,
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        primary_key=True,
    )
    price = Column(Numeric(18, 6), nullable=False)
    change = Column(Numeric(18, 6), nullable=True)
    change_percent = Column(Numeric(10, 4), nullable=True)
    volume = Column(Numeric(20, 0), nullable=True)
    day_high = Column(Numeric(18, 6), nullable=True)
    day_low = Column(Numeric(18, 6), nullable=True)
    w52_high = Column(Numeric(18, 6), nullable=True)
    w52_low = Column(Numeric(18, 6), nullable=True)
    previous_close = Column(Numeric(18, 6), nullable=True)

    market_timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Datetime with timezone when price was recorded in the market",
        primary_key=True,
    )

    # Relationships
    instrument = relationship("Instrument", back_populates="price_history")

    # efficient index for time range queries
    __table_args__ = (
        Index("idx_price_history_ts_instrument", "market_timestamp", "instrument_id"),
        {"comment": "Time-series price data for instruments"},
    )

    def __repr__(self) -> str:
        return f"<PriceHistory instrument_id={self.instrument_id} price={self.price} time={self.market_timestamp}>"
