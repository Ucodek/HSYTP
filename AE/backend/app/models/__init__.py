# Import all models here to ensure they are registered with SQLAlchemy
from app.models.base_model import BaseModel
from app.models.historical import HistoricalData
from app.models.instruments import Instrument, InstrumentPrice
from app.models.market import MarketIndex, MarketIndexPrice
from app.models.users import RefreshToken, User

# For Alembic's use - all models must be listed here
__all__ = [
    "BaseModel",
    "Instrument",
    "InstrumentPrice",
    "User",
    "RefreshToken",
    "MarketIndex",
    "MarketIndexPrice",
    "HistoricalData",
]
