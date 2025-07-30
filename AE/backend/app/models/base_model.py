from sqlalchemy import Column, DateTime, Integer, func

from app.db.base import Base


class BaseModel(Base):
    """Base model class for all database models with common fields."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
