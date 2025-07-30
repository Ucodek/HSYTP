import logging
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Configure connection pool settings
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=not settings.DATABASE_URL
    or not settings.DATABASE_URL.startswith("postgresql"),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Simple event listener to ensure TimescaleDB extension exists
@event.listens_for(engine.sync_engine, "connect")
def ensure_timescaledb_extension(dbapi_connection, connection_record):
    """Enable TimescaleDB extension when database connects.

    This only ensures the extension exists but doesn't set up tables.
    For full setup including hypertables, use scripts/setup_timescaledb.py
    """
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")
        cursor.close()
        dbapi_connection.commit()
    except Exception as e:
        logging.warning(f"TimescaleDB extension setup note: {e}")


async def get_db():
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
