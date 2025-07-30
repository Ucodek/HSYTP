from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.instruments import Instrument


class MarketMoverType(str, Enum):
    """Types of market movers."""

    GAINERS = "gainers"
    LOSERS = "losers"
    ACTIVE = "active"


class MarketIndexBase(BaseModel):
    """Base schema for market indices."""

    symbol: str = Field(..., description="Index symbol", max_length=20)
    name: Dict[str, str] = Field(..., description="Multilingual name")
    country: Optional[str] = Field(
        None,
        description="Country code (ISO 3166-1 alpha-3)",
        min_length=2,
        max_length=3,
    )
    currency: Optional[str] = Field(
        None, description="Currency code (ISO 4217)", min_length=3, max_length=3
    )
    description: Optional[Dict[str, str]] = Field(
        None, description="Multilingual description"
    )


class MarketIndexCreate(MarketIndexBase):
    """Schema for creating a market index."""

    constituents: Optional[List[int]] = None


class MarketIndexUpdate(BaseModel):
    """Schema for updating a market index."""

    name: Optional[Dict[str, str]] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    description: Optional[Dict[str, str]] = None
    constituents: Optional[List[int]] = None


class MarketIndexPrice(BaseModel):
    """Schema for market index price."""

    last_price: float
    price_change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    previous_close: Optional[float] = None
    period_high: Optional[float] = None
    period_low: Optional[float] = None
    w52_high: Optional[float] = None
    w52_low: Optional[float] = None
    data_timestamp: str


class MarketIndex(MarketIndexBase):
    """Schema for market index response."""

    id: int
    created_at: datetime
    updated_at: datetime
    price: Optional[MarketIndexPrice] = None

    model_config = {"from_attributes": True}


class MarketMover(BaseModel):
    """Schema for market movers response item."""

    instrument: Instrument
    price_change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None


class MarketMoversResponse(BaseModel):
    """Schema for market movers response."""

    type: MarketMoverType
    data: List[MarketMover]
    timestamp: datetime
