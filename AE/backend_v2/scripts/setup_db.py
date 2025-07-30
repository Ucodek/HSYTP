#!/usr/bin/env python
"""
Database setup and initialization script.

This script performs the following operations:
1. Creates database tables if they don't exist
2. Initializes and configures Alembic for migrations
3. Creates an initial migration
4. Applies migrations to the database

Usage:
    python -m scripts.setup_db [--recreate] [--migrate] [--verbose]

Options:
    --recreate      Drop all tables before creating them
    --migrate       Create and apply migrations after table creation
    --verbose       Show detailed output
"""

import argparse
import importlib.util
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Check if sqlalchemy_utils is available
sqlalchemy_utils_available = importlib.util.find_spec("sqlalchemy_utils") is not None

if sqlalchemy_utils_available:
    from sqlalchemy_utils import create_database, database_exists
else:
    # Define fallback functions if sqlalchemy_utils is not available
    def database_exists(url):
        """Simple check if database exists by attempting to connect."""
        from sqlalchemy import create_engine

        try:
            engine = create_engine(url)
            conn = engine.connect()
            conn.close()
            return True
        except Exception:
            return False

    def create_database(url):
        """Create database (only supported for SQLite)."""
        if url.startswith("sqlite:///"):
            # For SQLite, just ensure the directory exists
            db_path = url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            return True
        else:
            logging.error("Cannot create database: sqlalchemy_utils not installed")
            logging.error("Please install it with: pip install sqlalchemy-utils")
            return False


from app.core.config.base import settings
from app.db.base import Base
from app.db.session import engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("setup_db")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Setup database tables and migrations")
    parser.add_argument(
        "--recreate", action="store_true", help="Drop and recreate all tables"
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Create and apply migrations after table creation",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--sqlite",
        action="store_true",
        help="Use SQLite instead of PostgreSQL (for development/testing)",
    )
    return parser.parse_args()


def ensure_database_exists(use_sqlite=False):
    """Ensure that the database exists, creating it if it doesn't."""
    try:
        # Override database URL if using SQLite
        if use_sqlite:
            os.environ["USE_SQLITE"] = "true"
            logger.info("Using SQLite database for setup")

        # Get database URL (after potential SQLite override)
        db_url = settings.DATABASE_URL

        # Special handling for SQLite
        if db_url.startswith("sqlite:///"):
            logger.info("Using SQLite database")
            db_path = db_url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            return True

        if not database_exists(db_url):
            logger.info(f"Database does not exist. Creating database...")
            if create_database(db_url):
                logger.info(f"Database created successfully.")
            else:
                logger.error("Failed to create database.")
                return False
        else:
            logger.info(f"Database already exists.")

        return True
    except Exception as e:
        logger.error(f"Error ensuring database exists: {e}")
        return False


def create_tables(recreate=False):
    """Create all database tables."""
    try:
        if recreate:
            logger.info("Dropping all tables...")
            Base.metadata.drop_all(bind=engine)
            logger.info("All tables dropped successfully.")

        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error creating tables: {e}")
        return False


def ensure_alembic_initialized():
    """Ensure Alembic is initialized for migrations."""
    alembic_ini_path = Path.cwd() / "alembic.ini"

    if not alembic_ini_path.exists():
        alembic_example = Path.cwd() / "alembic.ini.example"
        if alembic_example.exists():
            logger.info("Copying alembic.ini from example file...")
            with open(alembic_example, "r") as example_file:
                content = example_file.read()

            with open(alembic_ini_path, "w") as ini_file:
                ini_file.write(content)

            logger.info("alembic.ini created successfully.")
        else:
            logger.error(
                "alembic.ini.example not found. Please create alembic.ini manually."
            )
            return False

    return True


def run_alembic_command(command, message=None):
    """Run an Alembic command."""
    try:
        if message:
            result = subprocess.run(
                ["alembic", command, "-m", message],
                capture_output=True,
                text=True,
                check=True,
            )
        else:
            result = subprocess.run(
                ["alembic", command], capture_output=True, text=True, check=True
            )

        logger.info(f"Alembic command '{command}' executed successfully.")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Alembic command '{command}': {e}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        return False, None


def create_initial_migration():
    """Create initial Alembic migration."""
    logger.info("Creating initial migration...")
    success, output = run_alembic_command("revision", "Initial migration")
    if success:
        logger.info("Initial migration created successfully.")
    return success


def apply_migrations():
    """Apply all pending migrations."""
    logger.info("Applying database migrations...")
    success, output = run_alembic_command("upgrade", "head")
    if success:
        logger.info("Database migrations applied successfully.")
    return success


def main():
    """Main entry point for the script."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting database setup...")

    # Ensure database exists
    if not ensure_database_exists(use_sqlite=args.sqlite):
        logger.error("Failed to ensure database exists. Exiting.")
        return 1

    # Create tables
    if not create_tables(recreate=args.recreate):
        logger.error("Failed to create tables. Exiting.")
        return 1

    # Handle migrations if requested
    if args.migrate:
        # Ensure Alembic is initialized
        if not ensure_alembic_initialized():
            logger.error("Failed to initialize Alembic. Exiting.")
            return 1

        # Create initial migration
        if not create_initial_migration():
            logger.error("Failed to create initial migration. Exiting.")
            return 1

        # Apply migrations
        if not apply_migrations():
            logger.error("Failed to apply migrations. Exiting.")
            return 1

    logger.info("Database setup completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
