import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def check_database_connection(db: AsyncSession) -> bool:
    """
    Check if database connection is working.

    Args:
        db: SQLAlchemy AsyncSession

    Returns:
        True if connection is working, False otherwise
    """
    try:
        # Execute a simple query
        result = await db.execute(text("SELECT 1"))
        value = result.scalar()

        # Check if we got expected result
        if value == 1:
            logging.info("Database connection successful")
            return True

        logging.error(f"Database connection check returned unexpected value: {value}")
        return False

    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        return False


async def get_database_stats(db: AsyncSession) -> dict:
    """
    Get basic statistics about the database.

    Args:
        db: SQLAlchemy AsyncSession

    Returns:
        Dictionary with database statistics
    """
    try:
        # Get database version
        version_result = await db.execute(text("SHOW server_version"))
        version = version_result.scalar()

        # Get number of connections
        conn_result = await db.execute(text("SELECT count(*) FROM pg_stat_activity"))
        connections = conn_result.scalar()

        return {"version": version, "connections": connections, "status": "connected"}
    except Exception as e:
        logging.error(f"Error getting database stats: {str(e)}")
        return {"status": "error", "message": str(e)}
