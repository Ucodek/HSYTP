from sqlalchemy import Column, DateTime, Integer, MetaData, func
from sqlalchemy.orm import declarative_base

# Add back the naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

# Base class for all SQLAlchemy models
Base = declarative_base(metadata=metadata)


class BaseModel(Base):
    """Base model for all SQLAlchemy models."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


# Remove the circular imports - these will be handled in a different file
# from app.modules.auth.models import User, Token, UserRole, TokenType
# from app.modules.instruments.models import Instrument, InstrumentType, Exchange
