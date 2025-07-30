import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.db.base import BaseModel
from app.modules.instruments.utils import get_translated_text, safe_numeric
from app.utils.i18n import translated_column

# Constants
CURRENCY_CODE_LENGTH = 3
COUNTRY_CODE_LENGTH = 2
SYMBOL_MAX_LENGTH = 20
ISIN_LENGTH = 12
DEFAULT_CURRENCY = "USD"


class InstrumentType(str, enum.Enum):
    """Types of financial instruments."""

    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    OPTION = "option"
    FUTURE = "future"
    FOREX = "forex"
    CRYPTO = "crypto"
    INDEX = "index"
    OTHER = "other"


class Exchange(str, enum.Enum):
    """Major stock exchanges."""

    NYSE = "nyse"
    NASDAQ = "nasdaq"
    LSE = "lse"  # London Stock Exchange
    TSE = "tse"  # Tokyo Stock Exchange
    HKEX = "hkex"  # Hong Kong Exchange
    NSE = "nse"  # National Stock Exchange (India)
    BSE = "bse"  # Bombay Stock Exchange
    EURONEXT = "euronext"
    XETRA = "xetra"
    OTHER = "other"


class Instrument(BaseModel):
    """Financial instrument model for various tradable assets."""

    __tablename__ = "instruments"

    # Basic information
    symbol = Column(String(SYMBOL_MAX_LENGTH), index=True, nullable=False, unique=True)
    # Using translated columns for multilingual text
    name = translated_column(nullable=False)
    description = translated_column(nullable=True)
    isin = Column(
        String(ISIN_LENGTH), index=True, nullable=True, unique=True
    )  # International Securities Identification Number
    type = Column(Enum(InstrumentType), nullable=False, index=True)

    # Market information
    exchange = Column(Enum(Exchange), nullable=True, index=True)
    currency = Column(
        String(CURRENCY_CODE_LENGTH), nullable=False, default=DEFAULT_CURRENCY
    )  # ISO 4217 currency code

    # Price information
    current_price = Column(Numeric(20, 6), nullable=True)
    previous_close = Column(Numeric(20, 6), nullable=True)
    open_price = Column(Numeric(20, 6), nullable=True)
    day_high = Column(Numeric(20, 6), nullable=True)
    day_low = Column(Numeric(20, 6), nullable=True)
    w52_high = Column(Numeric(20, 6), nullable=True, name="fifty_two_week_high")
    w52_low = Column(Numeric(20, 6), nullable=True, name="fifty_two_week_low")

    # Volume information
    volume = Column(Integer, nullable=True)
    avg_volume = Column(Integer, nullable=True)

    # Additional information
    market_cap = Column(Numeric(30, 2), nullable=True)
    beta = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)  # Price-to-Earnings ratio
    eps = Column(Float, nullable=True)  # Earnings Per Share
    dividend_yield = Column(Float, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_updated = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    # Additional data for specific types - using translated columns
    sector = translated_column(nullable=True)
    industry = translated_column(nullable=True)
    country = Column(
        String(COUNTRY_CODE_LENGTH), nullable=True
    )  # ISO 3166-1 alpha-2 country code

    # Relations
    prices = relationship(
        "InstrumentPrice", back_populates="instrument", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Instrument {self.symbol} ({self.type})>"

    @property
    def is_stock(self) -> bool:
        """Check if the instrument is a stock."""
        return self.type == InstrumentType.STOCK

    @property
    def price_change(self) -> Optional[float]:
        """Calculate price change from previous close."""
        if self.current_price is None or self.previous_close is None:
            return None
        return safe_numeric(self.current_price - self.previous_close)

    @property
    def price_change_percent(self) -> Optional[float]:
        """Calculate price change percentage from previous close."""
        if (
            self.current_price is None
            or self.previous_close is None
            or self.previous_close == 0
        ):
            return None
        return float(
            (self.current_price - self.previous_close) / self.previous_close * 100
        )

    def to_dict(self, language: str = "en") -> dict:
        """
        Convert instrument to dictionary with localized text.

        Args:
            language: Language code for translated fields

        Returns:
            Dictionary with instrument data
        """
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": get_translated_text(self.name, language) or "",
            "description": get_translated_text(self.description, language),
            "type": self.type,
            "exchange": self.exchange,
            "currency": self.currency,
            "current_price": safe_numeric(self.current_price),
            "price_change": self.price_change,
            "price_change_percent": self.price_change_percent,
            "volume": self.volume,
            "sector": get_translated_text(self.sector, language),
            "industry": get_translated_text(self.industry, language),
            "country": self.country,
            "is_active": self.is_active,
            "last_updated": self.last_updated.isoformat()
            if self.last_updated
            else None,
        }


class InstrumentPrice(BaseModel):
    """Historical price data for instruments."""

    __tablename__ = "instrument_prices"

    # Relationship to instrument
    instrument_id = Column(
        Integer,
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Price data
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Numeric(20, 6), nullable=True)
    high = Column(Numeric(20, 6), nullable=True)
    low = Column(Numeric(20, 6), nullable=True)
    close = Column(Numeric(20, 6), nullable=False)
    adjusted_close = Column(Numeric(20, 6), nullable=True)
    volume = Column(Integer, nullable=True)

    # Relationship
    instrument = relationship("Instrument", back_populates="prices")

    def __repr__(self):
        return (
            f"<InstrumentPrice {self.instrument_id} at {self.timestamp}: {self.close}>"
        )
