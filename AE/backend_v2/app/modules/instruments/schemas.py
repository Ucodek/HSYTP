from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.modules.instruments.models import (
    COUNTRY_CODE_LENGTH,
    CURRENCY_CODE_LENGTH,
    DEFAULT_CURRENCY,
    ISIN_LENGTH,
    SYMBOL_MAX_LENGTH,
    Exchange,
    InstrumentType,
)
from app.modules.instruments.utils import get_translated_text, safe_numeric
from app.utils.i18n import TranslatedField


# Base schemas
class InstrumentBase(BaseModel):
    """Base schema with common instrument fields."""

    symbol: str = Field(
        ..., min_length=1, max_length=SYMBOL_MAX_LENGTH, description="Trading symbol"
    )
    name: TranslatedField = Field(
        ..., description="Instrument name in multiple languages"
    )
    type: InstrumentType = Field(..., description="Instrument type")
    exchange: Optional[Exchange] = Field(None, description="Exchange where traded")
    currency: str = Field(
        DEFAULT_CURRENCY,
        min_length=3,
        max_length=CURRENCY_CODE_LENGTH,
        description="ISO 4217 currency code",
    )
    description: Optional[TranslatedField] = Field(
        None, description="Instrument description in multiple languages"
    )
    sector: Optional[TranslatedField] = Field(
        None, description="Business sector in multiple languages"
    )
    industry: Optional[TranslatedField] = Field(
        None, description="Industry category in multiple languages"
    )
    country: Optional[str] = Field(
        None,
        min_length=2,
        max_length=COUNTRY_CODE_LENGTH,
        description="ISO 3166-1 alpha-2 country code",
    )


class InstrumentCreate(InstrumentBase):
    """Schema for creating a new instrument."""

    isin: Optional[str] = Field(
        None, min_length=ISIN_LENGTH, max_length=ISIN_LENGTH, description="ISIN code"
    )

    @field_validator("symbol")
    def symbol_uppercase(cls, v):
        """Convert symbol to uppercase."""
        return v.upper() if v else v

    @field_validator("isin")
    def validate_isin(cls, v):
        """Validate ISIN format if provided."""
        if v is None:
            return v
        if len(v) != ISIN_LENGTH:
            raise ValueError(f"ISIN must be {ISIN_LENGTH} characters")
        return v.upper()

    @field_validator("name")
    def validate_name(cls, v):
        """Ensure name has at least the default language (en)."""
        if isinstance(v, dict):
            # Convert dict to TranslatedField if it comes from JSON
            from app.utils.i18n import TranslatedField

            v = TranslatedField.from_dict(v)

        # Ensure English text is provided
        if not hasattr(v, "en") or not v.en:
            raise ValueError("Name must have at least an English version")

        return v


class InstrumentUpdate(BaseModel):
    """Schema for updating an instrument."""

    name: Optional[TranslatedField] = None
    description: Optional[TranslatedField] = None
    type: Optional[InstrumentType] = None
    exchange: Optional[Exchange] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=CURRENCY_CODE_LENGTH)
    sector: Optional[TranslatedField] = None
    industry: Optional[TranslatedField] = None
    country: Optional[str] = Field(None, min_length=2, max_length=COUNTRY_CODE_LENGTH)
    isin: Optional[str] = Field(None, min_length=ISIN_LENGTH, max_length=ISIN_LENGTH)
    is_active: Optional[bool] = None

    # Define validator separately for this class instead of reusing
    @field_validator("isin")
    def validate_isin(cls, v):
        """Validate ISIN format if provided."""
        if v is None:
            return v
        if len(v) != ISIN_LENGTH:
            raise ValueError(f"ISIN must be {ISIN_LENGTH} characters")
        return v.upper()


# Price-related schemas
class InstrumentPriceUpdate(BaseModel):
    """Schema for updating instrument price data."""

    current_price: float = Field(..., gt=0)
    previous_close: Optional[float] = Field(None, ge=0)
    open_price: Optional[float] = Field(None, ge=0)
    day_high: Optional[float] = Field(None, ge=0)
    day_low: Optional[float] = Field(None, ge=0)
    w52_high: Optional[float] = Field(None, ge=0)
    w52_low: Optional[float] = Field(None, ge=0)
    volume: Optional[int] = Field(None, ge=0)
    avg_volume: Optional[int] = Field(None, ge=0)
    market_cap: Optional[float] = Field(None, ge=0)
    beta: Optional[float] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = Field(None, ge=0)


class PriceData(BaseModel):
    """Schema for price data in responses."""

    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
    open_price: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    w52_high: Optional[float] = None
    w52_low: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    market_cap: Optional[float] = None
    beta: Optional[float] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    last_updated: Optional[datetime] = None

    @classmethod
    def from_instrument(cls, instrument: "Instrument") -> Optional["PriceData"]:
        """Create PriceData from an instrument instance."""
        if not hasattr(instrument, "current_price"):
            return None

        return cls(
            current_price=safe_numeric(instrument.current_price),
            previous_close=safe_numeric(instrument.previous_close),
            price_change=instrument.price_change,
            price_change_percent=instrument.price_change_percent,
            open_price=safe_numeric(instrument.open_price),
            day_high=safe_numeric(instrument.day_high),
            day_low=safe_numeric(instrument.day_low),
            w52_high=safe_numeric(instrument.w52_high),
            w52_low=safe_numeric(instrument.w52_low),
            volume=instrument.volume,
            avg_volume=instrument.avg_volume,
            market_cap=safe_numeric(instrument.market_cap),
            beta=instrument.beta,
            pe_ratio=instrument.pe_ratio,
            eps=instrument.eps,
            dividend_yield=instrument.dividend_yield,
            last_updated=instrument.last_updated,
        )


# Response schemas
class InstrumentResponse(InstrumentBase):
    """Schema for instrument response."""

    id: int
    isin: Optional[str] = None
    price: Optional[PriceData] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()


class LocalizedInstrumentResponse(BaseModel):
    """Schema for localized instrument response."""

    id: int
    symbol: str
    name: str
    type: InstrumentType
    exchange: Optional[Exchange] = None
    currency: str
    description: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    isin: Optional[str] = None
    price: Optional[PriceData] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_instrument(
        cls, instrument: "Instrument", language: str = "en"
    ) -> "LocalizedInstrumentResponse":
        """Create a response with localized text for the specified language."""
        data = {
            "id": instrument.id,
            "symbol": instrument.symbol,
            "name": get_translated_text(instrument.name, language)
            or "",  # Name is required
            "type": instrument.type,
            "exchange": instrument.exchange,
            "currency": instrument.currency,
            "description": get_translated_text(instrument.description, language),
            "sector": get_translated_text(instrument.sector, language),
            "industry": get_translated_text(instrument.industry, language),
            "country": instrument.country,
            "isin": instrument.isin,
            "price": PriceData.from_instrument(instrument),
            "is_active": instrument.is_active,
            "created_at": instrument.created_at,
            "updated_at": instrument.updated_at,
        }
        return cls(**data)


# Historical price schemas
class InstrumentPriceCreate(BaseModel):
    """Schema for creating historical price data."""

    instrument_id: int
    timestamp: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float = Field(..., gt=0)
    adjusted_close: Optional[float] = None
    volume: Optional[int] = Field(None, ge=0)


class InstrumentPriceResponse(BaseModel):
    """Schema for historical price data response."""

    instrument_id: int
    timestamp: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float
    adjusted_close: Optional[float] = None
    volume: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# Filtering and pagination schemas
class InstrumentFilter(BaseModel):
    """Schema for filtering instruments."""

    query: Optional[str] = None
    type: Optional[InstrumentType] = None
    exchange: Optional[Exchange] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = True


# Simply alias InstrumentFilter as InstrumentSearchParams to avoid duplication
InstrumentSearchParams = InstrumentFilter


class InstrumentList(BaseModel):
    """Schema for simple instrument list without pagination."""

    items: List[InstrumentResponse]
    count: int
