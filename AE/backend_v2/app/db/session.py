import logging
from contextlib import contextmanager

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from app.core.config.base import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with specific configurations for better performance
engine = create_engine(
    str(settings.DATABASE_URL),  # Changed from DATABASE_URI to DATABASE_URL
    pool_pre_ping=True,  # Test connections before using them
    pool_size=5,  # Number of connections to keep open
    max_overflow=10,  # Max number of connections to open when pool is full
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=settings.ENVIRONMENT == "development",  # Set to True to log all SQL statements
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Convert database URL to async compatible format
def get_async_database_url(url):
    """Convert a database URL to an async-compatible version."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    elif url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    return url


# Create async engine with appropriate driver
try:
    async_database_url = get_async_database_url(str(settings.DATABASE_URL))
    async_engine = create_async_engine(
        async_database_url,
        echo=settings.ENVIRONMENT == "development",
        pool_pre_ping=True,
    )

    AsyncSessionLocal = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
except Exception as e:
    # Log the error but don't crash - synchronous operations can still work
    logger.warning(f"Could not initialize async database engine: {e}")
    async_engine = None
    AsyncSessionLocal = None


def get_db() -> Session:
    """
    FastAPI dependency for getting database session.
    Yields a SQLAlchemy session for the request,
    and automatically closes it after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for getting a database session.
    For use outside of FastAPI request handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    Only used for development and testing.
    """
    # Import Base from base_class to ensure all models are registered
    from app.db.base_class import Base

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


async def ensure_database_exists() -> bool:
    """
    Ensure the database exists, creating it if it doesn't.

    Returns:
        bool: True if database exists or was created, False if there was an error
    """
    db_name = settings.POSTGRES_DB
    user = settings.POSTGRES_USER
    password = settings.POSTGRES_PASSWORD
    host = settings.POSTGRES_SERVER
    port = settings.POSTGRES_PORT

    try:
        # Connect to the default 'postgres' database to check if our database exists
        conn = psycopg2.connect(
            dbname="postgres", user=user, password=password, host=host, port=port
        )
        conn.autocommit = True  # Needed for creating database
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone() is not None

        if not exists:
            logger.info(f"Database '{db_name}' does not exist. Creating...")
            # Create the database
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Error ensuring database exists: {e}")
        return False
