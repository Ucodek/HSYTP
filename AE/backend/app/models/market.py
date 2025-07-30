from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class MarketIndex(BaseModel):
    """Model for market indices like S&P 500, NASDAQ, etc."""

    __tablename__ = "market_indices"

    symbol = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(JSONB, nullable=False)  # Multilingual support
    country = Column(String(3), nullable=True, index=True)
    currency = Column(String(3), nullable=True)
    description = Column(JSONB, nullable=True)  # Multilingual support
    constituents = Column(JSONB, nullable=True)  # Array of instrument IDs

    # Add relationship to MarketIndexPrice
    price = relationship("MarketIndexPrice", uselist=False, back_populates="index")


class MarketIndexPrice(BaseModel):
    """Model for storing the latest prices for market indices."""

    __tablename__ = "market_index_prices"

    index_id = Column(
        Integer, ForeignKey("market_indices.id", ondelete="CASCADE"), nullable=False
    )
    last_price = Column(Numeric(18, 4), nullable=False)
    price_change = Column(Numeric(18, 4), nullable=True)
    change_percent = Column(Numeric(8, 4), nullable=True)
    volume = Column(Numeric(18, 0), nullable=True)
    previous_close = Column(Numeric(18, 4), nullable=True)
    period_high = Column(Numeric(18, 4), nullable=True)
    period_low = Column(Numeric(18, 4), nullable=True)
    w52_high = Column(Numeric(18, 4), nullable=True)
    w52_low = Column(Numeric(18, 4), nullable=True)
    data_timestamp = Column(Text, nullable=False)

    # Update relationship to include back_populates
    index = relationship("MarketIndex", back_populates="price")
