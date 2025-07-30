from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field, model_validator


class InstrumentType(str, Enum):
    """Enum for instrument types."""

    STOCK = "stock"
    INDEX = "index"
    CRYPTO = "crypto"
    ETF = "etf"


class InstrumentBase(BaseModel):
    """Base schema for instruments."""

    symbol: str = Field(..., description="Instrument symbol", max_length=20)
    name: Dict[str, str] = Field(..., description="Multilingual name")
    type: InstrumentType = Field(..., description="Instrument type")
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
    sector: Optional[str] = Field(None, description="Sector", max_length=50)
    industry: Optional[str] = Field(None, description="Industry", max_length=50)


class InstrumentCreate(InstrumentBase):
    """Schema for creating an instrument."""

    @model_validator(mode="after")
    def validate_name(self) -> "InstrumentCreate":
        # This validation could be extracted to a reusable function
        # Ensure name has at least one language entry
        if not self.name or not any(self.name.values()):
            raise ValueError("Name must have at least one language entry")

        # Ensure English name exists (can be adapted to your default language)
        if "en-US" not in self.name or not self.name["en-US"]:
            raise ValueError("English (en-US) name must be provided")

        return self


class InstrumentUpdate(BaseModel):
    """Schema for updating an instrument."""

    name: Optional[Dict[str, str]] = None
    type: Optional[InstrumentType] = None
    # Repeated field definitions that could be inherited from base
    country: Optional[str] = Field(
        None,
        description="Country code (ISO 3166-1 alpha-3)",
        min_length=2,
        max_length=3,
    )
    currency: Optional[str] = Field(
        None, description="Currency code (ISO 4217)", min_length=3, max_length=3
    )
    description: Optional[Dict[str, str]] = None
    sector: Optional[str] = Field(None, description="Sector", max_length=50)
    industry: Optional[str] = Field(None, description="Industry", max_length=50)


class InstrumentInDBBase(InstrumentBase):
    """Schema for instrument as stored in database."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Instrument(InstrumentInDBBase):
    """Schema for instrument response."""

    pass
