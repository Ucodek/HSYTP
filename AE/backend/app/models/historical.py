from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, Index
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel


class HistoricalData(BaseModel):
    """Model for historical price data optimized for TimescaleDB."""

    __tablename__ = "historical_data"

    # Disable id column from BaseModel - this is critical!
    id = None

    # Primary key fields for TimescaleDB hypertable
    instrument_id = Column(Integer, ForeignKey("instruments.id"), primary_key=True)
    timestamp = Column(DateTime(timezone=True), primary_key=True)

    # Data fields
    open = Column(Numeric(18, 4))
    high = Column(Numeric(18, 4))
    low = Column(Numeric(18, 4))
    close = Column(Numeric(18, 4), nullable=False)
    volume = Column(Numeric(18, 0))
    adjusted_close = Column(Numeric(18, 4))

    # Relationship
    instrument = relationship("Instrument", backref="historical_data")

    # Efficient index for time range queries
    __table_args__ = (
        Index("idx_historical_ts_instrument", "timestamp", "instrument_id"),
        {"comment": "Time-series price data for TimescaleDB"},
    )

    # Note: The conversion to a hypertable will be handled in the migration
