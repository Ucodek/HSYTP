# This file exists to break circular imports between models
# and is used by Alembic to discover all models for migrations
from app.db.base import Base

# Import all models that should be included in migrations
# These imports are used by Alembic to detect models when generating migrations
from app.modules.auth.models import Token, TokenType, User, UserRole
from app.modules.instruments.models import Exchange, Instrument, InstrumentType

# Export all models for convenience
__all__ = [
    "Base",
    "User",
    "Token",
    "UserRole",
    "TokenType",
    "Instrument",
    "InstrumentType",
    "Exchange",
]
