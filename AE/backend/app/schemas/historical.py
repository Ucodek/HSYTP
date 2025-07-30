from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field  # Added Field import


class HistoricalDataPoint(BaseModel):
    """Schema for a single historical data point."""

    timestamp: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float
    volume: Optional[int] = None
    adjusted_close: Optional[float] = None


class HistoricalDataCreate(HistoricalDataPoint):
    """Schema for creating historical data."""

    instrument_id: int


class HistoricalDataResponse(BaseModel):
    """Schema for historical data response."""

    instrument_id: int
    symbol: str
    data: list[HistoricalDataPoint]

    model_config = {"from_attributes": True}


class PeriodEnum(str, Enum):
    """Valid time periods."""

    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"
    SIX_MONTHS = "6m"
    ONE_YEAR = "1y"
    FIVE_YEARS = "5y"
    MAX = "max"


class IntervalEnum(str, Enum):
    """Valid time intervals."""

    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"


class HistoricalQueryParams(BaseModel):
    """Parameters for historical data queries."""

    period: PeriodEnum = Field(PeriodEnum.ONE_MONTH)
    interval: IntervalEnum = Field(IntervalEnum.ONE_DAY)

    # Validator no longer needed as Enum handles validation
