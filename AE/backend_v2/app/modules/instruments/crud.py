"""
Database operations for the instruments module.

This module provides CRUD operations for instruments and price histories.
"""
import logging
from datetime import datetime, timezone
from functools import wraps
from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.instruments.models import Instrument, InstrumentPrice
from app.modules.instruments.schemas import (
    InstrumentCreate,
    InstrumentFilter,
    InstrumentPriceCreate,
    InstrumentPriceUpdate,
    InstrumentUpdate,
)
from app.modules.instruments.utils import get_translated_text

logger = logging.getLogger(__name__)


# --- Common Utilities ---


def db_transaction(func):
    """
    Decorator for database operations with error handling and transaction management.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with error handling
    """

    @wraps(func)
    def wrapper(db: Session, *args, **kwargs):
        try:
            result = func(db, *args, **kwargs)
            return result
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error in {func.__name__}: {str(e)}")
            # Extract constraint violation details
            error_detail = str(e).lower()
            if "unique constraint" in error_detail:
                if "symbol" in error_detail:
                    raise ValueError(f"Instrument with symbol already exists")
                elif "isin" in error_detail:
                    raise ValueError(f"Instrument with ISIN already exists")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise

    return wrapper


# --- Basic Instrument Operations ---


def get_instrument(db: Session, instrument_id: int) -> Optional[Instrument]:
    """Get instrument by ID."""
    return db.query(Instrument).filter(Instrument.id == instrument_id).first()


def get_instrument_by_symbol(db: Session, symbol: str) -> Optional[Instrument]:
    """Get instrument by symbol (case-insensitive)."""
    if not symbol:
        return None
    return (
        db.query(Instrument)
        .filter(func.upper(Instrument.symbol) == symbol.upper())
        .first()
    )


def get_instrument_by_isin(db: Session, isin: str) -> Optional[Instrument]:
    """Get instrument by ISIN (case-insensitive)."""
    if not isin:
        return None
    return (
        db.query(Instrument).filter(func.upper(Instrument.isin) == isin.upper()).first()
    )


@db_transaction
def create_instrument(db: Session, data: InstrumentCreate) -> Instrument:
    """Create a new instrument."""
    # Create instrument object with data from schema
    db_instrument = Instrument(
        symbol=data.symbol.upper(),
        name=data.name,
        type=data.type,
        exchange=data.exchange,
        currency=data.currency,
        description=data.description,
        sector=data.sector,
        industry=data.industry,
        country=data.country,
        isin=data.isin.upper() if data.isin else None,
        is_active=True,
        last_updated=datetime.now(timezone.utc),
    )

    db.add(db_instrument)
    db.commit()
    db.refresh(db_instrument)

    logger.info(f"Created instrument: {db_instrument.symbol}")
    return db_instrument


@db_transaction
def update_instrument(
    db: Session, instrument_id: int, data: InstrumentUpdate
) -> Optional[Instrument]:
    """Update an existing instrument."""
    # Get the instrument to update
    instrument = get_instrument(db, instrument_id)
    if not instrument:
        return None

    # Get update data excluding None values
    update_data = data.model_dump(exclude_unset=True)

    # Handle ISIN case conversion
    if "isin" in update_data and update_data["isin"] is not None:
        update_data["isin"] = update_data["isin"].upper()

    # Apply updates to model
    for field, value in update_data.items():
        setattr(instrument, field, value)

    # Update last_updated timestamp
    instrument.last_updated = datetime.now(timezone.utc)

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    logger.info(f"Updated instrument ID: {instrument_id}")
    return instrument


@db_transaction
def update_instrument_price(
    db: Session, instrument_id: int, data: InstrumentPriceUpdate
) -> Optional[Instrument]:
    """Update an instrument's price data."""
    # Get the instrument to update
    instrument = get_instrument(db, instrument_id)
    if not instrument:
        return None

    # Get update data excluding None values
    update_data = data.model_dump(exclude_unset=True)

    # Apply updates to model
    for field, value in update_data.items():
        setattr(instrument, field, value)

    # Update last_updated timestamp
    instrument.last_updated = datetime.now(timezone.utc)

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    logger.info(f"Updated price for instrument ID: {instrument_id}")
    return instrument


@db_transaction
def delete_instrument(db: Session, instrument_id: int) -> bool:
    """Delete an instrument by ID."""
    # Get the instrument to delete
    instrument = get_instrument(db, instrument_id)
    if not instrument:
        return False

    db.delete(instrument)
    db.commit()
    logger.info(f"Deleted instrument ID: {instrument_id}")
    return True


@db_transaction
def deactivate_instrument(db: Session, instrument_id: int) -> Optional[Instrument]:
    """Deactivate an instrument instead of deleting it."""
    # Get the instrument to deactivate
    instrument = get_instrument(db, instrument_id)
    if not instrument:
        return None

    # Set as inactive
    instrument.is_active = False
    instrument.last_updated = datetime.now(timezone.utc)

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    logger.info(f"Deactivated instrument ID: {instrument_id}")
    return instrument


# --- Search and Filtering ---


def apply_instrument_filters(query, filter_params: InstrumentFilter):
    """
    Apply filters to an instrument query.

    Args:
        query: SQLAlchemy query
        filter_params: Filter parameters

    Returns:
        Updated query with filters applied
    """
    # Apply basic filters
    if filter_params.type:
        query = query.filter(Instrument.type == filter_params.type)

    if filter_params.exchange:
        query = query.filter(Instrument.exchange == filter_params.exchange)

    if filter_params.country:
        query = query.filter(Instrument.country == filter_params.country)

    if filter_params.is_active is not None:
        query = query.filter(Instrument.is_active == filter_params.is_active)

    # Apply text search if provided
    if filter_params.query:
        search_term = f"%{filter_params.query}%"
        query = query.filter(
            or_(
                Instrument.symbol.ilike(search_term), Instrument.isin.ilike(search_term)
            )
        )

    return query


def search_instruments(
    db: Session, filters: InstrumentFilter, skip: int = 0, limit: int = 100
) -> List[Instrument]:
    """
    Search for instruments with filtering and pagination.

    Args:
        db: Database session
        filters: Filter parameters
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of matching instruments
    """
    query = db.query(Instrument)
    query = apply_instrument_filters(query, filters)

    return query.order_by(Instrument.symbol).offset(skip).limit(limit).all()


def count_instruments(db: Session, filters: InstrumentFilter) -> int:
    """
    Count instruments matching filter criteria.

    Args:
        db: Database session
        filters: Filter parameters

    Returns:
        Count of matching instruments
    """
    # Use count query optimization
    query = db.query(func.count(Instrument.id))
    query = apply_instrument_filters(query, filters)

    return query.scalar() or 0


# --- Price History Operations ---


def get_price_history(
    db: Session,
    instrument_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
) -> List[InstrumentPrice]:
    """
    Get historical price data for an instrument.

    Args:
        db: Database session
        instrument_id: Instrument ID
        start_date: Start date for filtering
        end_date: End date for filtering
        limit: Maximum number of records to return

    Returns:
        List of price history records
    """
    query = db.query(InstrumentPrice).filter(
        InstrumentPrice.instrument_id == instrument_id
    )

    # Apply date filters if provided
    if start_date:
        query = query.filter(InstrumentPrice.timestamp >= start_date)

    if end_date:
        query = query.filter(InstrumentPrice.timestamp <= end_date)

    # Sort by date descending and limit results
    return query.order_by(InstrumentPrice.timestamp.desc()).limit(limit).all()


@db_transaction
def create_price_history(db: Session, data: InstrumentPriceCreate) -> InstrumentPrice:
    """
    Create a historical price record.

    Args:
        db: Database session
        data: Price data

    Returns:
        Created price record
    """
    # Create price record from schema data
    db_price = InstrumentPrice(
        instrument_id=data.instrument_id,
        timestamp=data.timestamp,
        open=data.open,
        high=data.high,
        low=data.low,
        close=data.close,
        adjusted_close=data.adjusted_close,
        volume=data.volume,
    )

    db.add(db_price)
    db.commit()
    db.refresh(db_price)

    logger.info(f"Created price history for instrument ID: {data.instrument_id}")
    return db_price


@db_transaction
def bulk_create_price_history(
    db: Session, price_data_list: List[InstrumentPriceCreate]
) -> int:
    """
    Bulk create historical price records.

    Args:
        db: Database session
        price_data_list: List of price data objects

    Returns:
        Number of records created
    """
    # Create price record objects from schema data
    db_prices = [
        InstrumentPrice(
            instrument_id=price_data.instrument_id,
            timestamp=price_data.timestamp,
            open=price_data.open,
            high=price_data.high,
            low=price_data.low,
            close=price_data.close,
            adjusted_close=price_data.adjusted_close,
            volume=price_data.volume,
        )
        for price_data in price_data_list
    ]

    # Use bulk save for efficiency
    db.bulk_save_objects(db_prices)
    db.commit()

    record_count = len(db_prices)
    logger.info(f"Bulk created {record_count} price history records")
    return record_count


# --- Metadata Operations ---


def get_countries(db: Session) -> List[str]:
    """
    Get all unique country codes from instruments.

    Args:
        db: Database session

    Returns:
        List of country codes
    """
    # Query distinct non-null country codes
    result = (
        db.query(Instrument.country)
        .filter(Instrument.country.isnot(None))
        .distinct()
        .all()
    )

    # Extract values from result tuples
    return [r[0] for r in result if r[0]]


def get_localized_sectors(db: Session, language: str = "en") -> List[str]:
    """
    Get all unique sectors with localized text.

    Args:
        db: Database session
        language: Language code for localization

    Returns:
        List of localized sector names
    """
    # Get instruments with distinct sectors
    sector_instruments = (
        db.query(Instrument)
        .filter(Instrument.sector.isnot(None))
        .group_by(Instrument.sector)
        .all()
    )

    # Extract and deduplicate translated sector names
    sectors = []
    seen = set()

    for instrument in sector_instruments:
        sector_text = get_translated_text(instrument.sector, language)
        if sector_text and sector_text not in seen:
            sectors.append(sector_text)
            seen.add(sector_text)

    return sectors


def get_localized_industries(
    db: Session, language: str = "en", sector: Optional[str] = None
) -> List[str]:
    """
    Get all unique industries with localized text.

    Args:
        db: Database session
        language: Language code for localization
        sector: Optional sector to filter by

    Returns:
        List of localized industry names
    """
    # Get instruments with distinct industries
    query = db.query(Instrument).filter(Instrument.industry.isnot(None))

    # We'll filter by sector if needed
    instruments = query.group_by(Instrument.industry).all()

    # Extract and deduplicate translated industry names
    industries = []
    seen = set()

    for instrument in instruments:
        # If sector filter is applied, check if this instrument's sector matches
        if sector:
            instr_sector = get_translated_text(instrument.sector, language)
            if instr_sector != sector:
                continue

        industry_text = get_translated_text(instrument.industry, language)
        if industry_text and industry_text not in seen:
            industries.append(industry_text)
            seen.add(industry_text)

    return industries
