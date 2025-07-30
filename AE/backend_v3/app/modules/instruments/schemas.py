from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import InstrumentType, MarketType


# --- Instrument Schemas ---
class InstrumentBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    type: InstrumentType
    market: MarketType
    currency: str = Field(..., min_length=3, max_length=3)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class InstrumentCreate(InstrumentBase):
    pass


class InstrumentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[InstrumentType] = None
    market: Optional[MarketType] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    model_config = ConfigDict(extra="ignore")


class InstrumentResponse(InstrumentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class InstrumentWithLatestPriceResponse(InstrumentResponse):
    price: Optional[Decimal] = None
    market_timestamp: Optional[datetime] = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    day_high: Optional[Decimal] = None
    day_low: Optional[Decimal] = None
    w52_high: Optional[Decimal] = None
    w52_low: Optional[Decimal] = None
    previous_close: Optional[Decimal] = None
    model_config = ConfigDict(from_attributes=True)


# --- Price History Schemas ---
class InstrumentPriceHistoryBase(BaseModel):
    price: Decimal = Field(..., max_digits=18, decimal_places=6)
    change: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    change_percent: Optional[Decimal] = Field(None, max_digits=10, decimal_places=4)
    volume: Optional[Decimal] = Field(None, max_digits=20, decimal_places=0)
    day_high: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    day_low: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    previous_close: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    w52_high: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    w52_low: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    market_timestamp: datetime = Field(
        ...,
        description="Datetime with timezone when price was recorded in the market",
        examples=["2024-05-07T14:30:00Z", "2024-05-07T14:30:00+03:00"],
    )

    @staticmethod
    def quantize_data(data: dict) -> dict:
        def q(val, places):
            if val is None:
                return None
            return Decimal(str(val)).quantize(Decimal(places), rounding=ROUND_HALF_UP)

        return {
            **data,
            "price": q(data.get("price"), "0.000001"),
            "change": q(data.get("change"), "0.000001"),
            "change_percent": q(data.get("change_percent"), "0.0001"),
            "day_high": q(data.get("day_high"), "0.000001"),
            "day_low": q(data.get("day_low"), "0.000001"),
            "w52_high": q(data.get("w52_high"), "0.000001"),
            "w52_low": q(data.get("w52_low"), "0.000001"),
            "previous_close": q(data.get("previous_close"), "0.000001"),
        }

    @classmethod
    def from_raw_data(cls, instrument_id: int, data: dict):
        quantized = cls.quantize_data(data)
        return cls(instrument_id=instrument_id, **quantized)


class InstrumentPriceHistoryCreate(InstrumentPriceHistoryBase):
    instrument_id: int


class InstrumentPriceHistoryUpdate(BaseModel):
    price: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    change: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    change_percent: Optional[Decimal] = Field(None, max_digits=10, decimal_places=4)
    volume: Optional[Decimal] = Field(None, max_digits=20, decimal_places=0)
    day_high: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    day_low: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    previous_close: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    w52_high: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    w52_low: Optional[Decimal] = Field(None, max_digits=18, decimal_places=6)
    market_timestamp: Optional[datetime] = None
    model_config = ConfigDict(extra="ignore")


class InstrumentPriceHistoryResponse(InstrumentPriceHistoryBase):
    instrument_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
