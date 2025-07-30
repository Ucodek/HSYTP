#!/usr/bin/env python
"""
Seed initial data into the database.

This script populates the database with initial data like:
1. Admin and test users
2. Sample financial instruments
3. Basic reference data

Usage:
    python -m scripts.seed_data [--users] [--instruments] [--clear] [--verbose]

Options:
    --users         Seed user accounts (admin, test users)
    --instruments   Seed sample financial instruments
    --clear         Clear existing data before seeding
    --verbose       Show detailed output
    --all           Seed all data types (default if no options specified)
"""

import argparse
import logging
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.modules.auth.models import Token, User, UserRole
from app.modules.instruments.models import Exchange, Instrument, InstrumentType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("seed_data")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Seed database with initial data")
    parser.add_argument("--users", action="store_true", help="Seed user accounts")
    parser.add_argument(
        "--instruments", action="store_true", help="Seed sample financial instruments"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing data before seeding"
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--all", action="store_true", help="Seed all data types")
    return parser.parse_args()


def clear_data(db: Session, models=None):
    """Clear data from specified models."""
    if models is None:
        models = [Token, User, Instrument]

    try:
        for model in models:
            logger.info(f"Clearing {model.__name__} data...")
            db.query(model).delete()

        db.commit()
        logger.info("Data cleared successfully.")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error clearing data: {e}")
        return False


def seed_users(db: Session):
    """Seed admin and test users."""
    try:
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("Admin123!"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(admin_user)

        # Create regular test user
        test_user = User(
            email="user@example.com",
            username="testuser",
            hashed_password=get_password_hash("User123!"),
            full_name="Test User",
            role=UserRole.USER,
            is_active=True,
            is_verified=True,
        )
        db.add(test_user)

        db.commit()
        logger.info(f"Created admin user: admin@example.com (password: Admin123!)")
        logger.info(f"Created test user: user@example.com (password: User123!)")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error seeding users: {e}")
        return False


def seed_instruments(db: Session):
    """Seed sample financial instruments."""
    try:
        # Sample stock instruments
        instruments = [
            # US Stocks
            Instrument(
                symbol="AAPL",
                name="Apple Inc.",
                description="Technology company that designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.",
                isin="US0378331005",
                type=InstrumentType.STOCK,
                exchange=Exchange.NASDAQ,
                currency="USD",
                current_price=Decimal("150.00"),
                previous_close=Decimal("149.80"),
                open_price=Decimal("149.90"),
                day_high=Decimal("151.20"),
                day_low=Decimal("148.80"),
                volume=30000000,
                avg_volume=28000000,
                market_cap=Decimal("2500000000000"),
                beta=1.2,
                pe_ratio=25.5,
                eps=5.89,
                dividend_yield=0.6,
                sector="Technology",
                industry="Consumer Electronics",
                country="US",
                is_active=True,
                last_updated=datetime.utcnow(),
            ),
            Instrument(
                symbol="MSFT",
                name="Microsoft Corporation",
                description="Technology company that develops, licenses, and supports software products.",
                isin="US5949181045",
                type=InstrumentType.STOCK,
                exchange=Exchange.NASDAQ,
                currency="USD",
                current_price=Decimal("265.50"),
                previous_close=Decimal("264.90"),
                open_price=Decimal("265.10"),
                day_high=Decimal("267.00"),
                day_low=Decimal("264.20"),
                volume=25000000,
                avg_volume=22000000,
                market_cap=Decimal("2000000000000"),
                beta=0.95,
                pe_ratio=34.2,
                eps=7.76,
                dividend_yield=0.9,
                sector="Technology",
                industry="Software",
                country="US",
                is_active=True,
                last_updated=datetime.utcnow(),
            ),
            # ETFs
            Instrument(
                symbol="SPY",
                name="SPDR S&P 500 ETF Trust",
                description="Exchange-traded fund that tracks the S&P 500 index.",
                isin="US78462F1030",
                type=InstrumentType.ETF,
                exchange=Exchange.NYSE,
                currency="USD",
                current_price=Decimal("410.20"),
                previous_close=Decimal("409.80"),
                open_price=Decimal("409.90"),
                day_high=Decimal("411.50"),
                day_low=Decimal("409.20"),
                volume=70000000,
                avg_volume=65000000,
                market_cap=Decimal("380000000000"),
                beta=1.0,
                sector="Diversified",
                industry="Index Fund",
                country="US",
                is_active=True,
                last_updated=datetime.utcnow(),
            ),
            # Cryptocurrency
            Instrument(
                symbol="BTC-USD",
                name="Bitcoin USD",
                description="Bitcoin to USD exchange rate.",
                type=InstrumentType.CRYPTO,
                currency="USD",
                current_price=Decimal("35500.00"),
                previous_close=Decimal("35200.00"),
                open_price=Decimal("35250.00"),
                day_high=Decimal("36000.00"),
                day_low=Decimal("35000.00"),
                volume=500000,
                avg_volume=450000,
                is_active=True,
                last_updated=datetime.utcnow(),
            ),
            # Forex
            Instrument(
                symbol="EUR/USD",
                name="Euro / US Dollar",
                description="Euro to US Dollar exchange rate.",
                type=InstrumentType.FOREX,
                currency="USD",
                current_price=Decimal("1.0850"),
                previous_close=Decimal("1.0845"),
                open_price=Decimal("1.0840"),
                day_high=Decimal("1.0860"),
                day_low=Decimal("1.0830"),
                is_active=True,
                last_updated=datetime.utcnow(),
            ),
        ]

        for instrument in instruments:
            db.add(instrument)

        db.commit()
        logger.info(f"Seeded {len(instruments)} sample instruments")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error seeding instruments: {e}")
        return False


def main():
    """Main entry point for the script."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # If no specific data types are specified, seed all data
    if not (args.users or args.instruments):
        args.all = True

    logger.info("Starting database seeding...")

    # Create database session
    db = SessionLocal()

    try:
        # Clear existing data if requested
        if args.clear:
            if not clear_data(db):
                logger.error("Failed to clear existing data. Exiting.")
                return 1

        # Seed users if requested
        if args.users or args.all:
            if not seed_users(db):
                logger.error("Failed to seed users. Exiting.")
                return 1

        # Seed instruments if requested
        if args.instruments or args.all:
            if not seed_instruments(db):
                logger.error("Failed to seed instruments. Exiting.")
                return 1

        logger.info("Database seeding completed successfully.")
        return 0
    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
