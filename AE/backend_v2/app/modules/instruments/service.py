"""
Business logic for instrument module.

This module handles business rules, validations, and orchestrates
database operations for financial instruments.
"""
import logging
from typing import List, Optional, Tuple, TypeVar

from sqlalchemy.orm import Session

from app.errors.error_codes import ErrorCode
from app.errors.exceptions import NotFoundError, ValidationError
from app.modules.instruments.crud import create_instrument as crud_create_instrument
from app.modules.instruments.crud import (
    deactivate_instrument as crud_deactivate_instrument,
)
from app.modules.instruments.crud import delete_instrument as crud_delete_instrument
from app.modules.instruments.crud import get_countries as crud_get_countries
from app.modules.instruments.crud import (
    get_instrument,
    get_instrument_by_isin,
    get_instrument_by_symbol,
)
from app.modules.instruments.crud import (
    get_localized_industries as crud_get_localized_industries,
)
from app.modules.instruments.crud import (
    get_localized_sectors as crud_get_localized_sectors,
)
from app.modules.instruments.crud import update_instrument as crud_update_instrument
from app.modules.instruments.crud import (
    update_instrument_price as crud_update_instrument_price,
)
from app.modules.instruments.models import Exchange, Instrument, InstrumentType
from app.modules.instruments.schemas import (
    InstrumentCreate,
    InstrumentFilter,
    InstrumentList,
    InstrumentPriceUpdate,
    InstrumentResponse,
    InstrumentUpdate,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


def check_instrument_exists(
    instrument: Optional[Instrument], instrument_id: int
) -> Instrument:
    """
    Check if an instrument exists and raise an error if not.

    Args:
        instrument: Instrument object or None
        instrument_id: ID of the instrument

    Returns:
        Instrument if it exists

    Raises:
        NotFoundError: If the instrument is not found
    """
    if not instrument:
        raise NotFoundError(
            detail=f"Instrument with ID {instrument_id} not found",
            error_code=ErrorCode.RES_NOT_FOUND,
        )
    return instrument


# --- Instrument Creation and Updates ---


def create_instrument(db: Session, data: InstrumentCreate) -> Instrument:
    """
    Create a new financial instrument with validation.

    Args:
        db: Database session
        data: Instrument data to create

    Returns:
        Created instrument

    Raises:
        ValidationError: If an instrument with the same symbol or ISIN already exists
    """
    logger.info(f"Creating new instrument with symbol: {data.symbol}")

    # Validate symbol is unique
    if get_instrument_by_symbol(db, data.symbol):
        raise ValidationError(
            detail=f"Instrument with symbol '{data.symbol}' already exists",
            error_code=ErrorCode.VAL_DUPLICATE_ENTRY,
        )

    # Validate ISIN is unique (if provided)
    if data.isin and get_instrument_by_isin(db, data.isin):
        raise ValidationError(
            detail=f"Instrument with ISIN '{data.isin}' already exists",
            error_code=ErrorCode.VAL_DUPLICATE_ENTRY,
        )

    # Create instrument
    instrument = crud_create_instrument(db, data)
    logger.info(f"Created instrument ID: {instrument.id}")

    return instrument


def update_instrument(
    db: Session, instrument_id: int, data: InstrumentUpdate
) -> Instrument:
    """
    Update an instrument's details with validation.

    Args:
        db: Database session
        instrument_id: ID of instrument to update
        data: Updated data

    Returns:
        Updated instrument

    Raises:
        NotFoundError: If the instrument is not found
    """
    logger.info(f"Updating instrument ID: {instrument_id}")

    # Update instrument
    instrument = crud_update_instrument(db, instrument_id, data)

    # Check if instrument exists
    instrument = check_instrument_exists(instrument, instrument_id)

    logger.info(f"Updated instrument: {instrument.symbol}")
    return instrument


def update_price(
    db: Session, instrument_id: int, data: InstrumentPriceUpdate
) -> Instrument:
    """
    Update an instrument's price information.

    Args:
        db: Database session
        instrument_id: ID of instrument to update
        data: Updated price data

    Returns:
        Updated instrument

    Raises:
        NotFoundError: If the instrument is not found
    """
    logger.info(f"Updating price for instrument ID: {instrument_id}")

    # Update price
    instrument = crud_update_instrument_price(db, instrument_id, data)

    # Check if instrument exists
    instrument = check_instrument_exists(instrument, instrument_id)

    logger.info(f"Updated price for instrument: {instrument.symbol}")
    return instrument


# --- Instrument Retrieval ---


def get_instrument_by_id(db: Session, instrument_id: int) -> Instrument:
    """
    Get an instrument by ID.

    Args:
        db: Database session
        instrument_id: Instrument ID

    Returns:
        Instrument

    Raises:
        NotFoundError: If the instrument is not found
    """
    instrument = get_instrument(db, instrument_id)
    return check_instrument_exists(instrument, instrument_id)


def find_instrument_by_symbol(db: Session, symbol: str) -> Instrument:
    """
    Find an instrument by its symbol.

    Args:
        db: Database session
        symbol: Trading symbol

    Returns:
        Instrument

    Raises:
        NotFoundError: If the instrument is not found
    """
    instrument = get_instrument_by_symbol(db, symbol)
    if not instrument:
        raise NotFoundError(
            detail=f"Instrument with symbol '{symbol}' not found",
            error_code=ErrorCode.RES_NOT_FOUND,
        )
    return instrument


# --- Instrument Status Management ---


def delete_instrument(db: Session, instrument_id: int) -> None:
    """
    Delete an instrument from the database.

    Args:
        db: Database session
        instrument_id: Instrument ID

    Raises:
        NotFoundError: If the instrument is not found
    """
    logger.info(f"Deleting instrument ID: {instrument_id}")

    # Delete instrument
    success = crud_delete_instrument(db, instrument_id)

    # Check if instrument exists
    if not success:
        raise NotFoundError(
            detail=f"Instrument with ID {instrument_id} not found",
            error_code=ErrorCode.RES_NOT_FOUND,
        )

    logger.info(f"Deleted instrument ID: {instrument_id}")


def deactivate_instrument(db: Session, instrument_id: int) -> Instrument:
    """
    Deactivate an instrument instead of deleting it.

    Args:
        db: Database session
        instrument_id: Instrument ID

    Returns:
        Deactivated instrument

    Raises:
        NotFoundError: If the instrument is not found
    """
    logger.info(f"Deactivating instrument ID: {instrument_id}")

    # Deactivate instrument
    instrument = crud_deactivate_instrument(db, instrument_id)

    # Check if instrument exists
    instrument = check_instrument_exists(instrument, instrument_id)

    logger.info(f"Deactivated instrument: {instrument.symbol}")
    return instrument


# --- Instrument Search and Filtering ---

from app.api.common.filtering import apply_filters_from_params


def search_instruments(
    db: Session, filter_params: dict, page: int = 1, page_size: int = 20
) -> Tuple[List[Instrument], int]:
    """
    Search for instruments with filtering and pagination.

    Args:
        db: Database session
        filter_params: Filter parameters
        page: Page number (starting from 1)
        page_size: Number of items per page

    Returns:
        Tuple of (list of instruments, total count)
    """
    # Calculate offset from page number
    skip = (page - 1) * page_size

    # Create base query
    query = db.query(Instrument)

    # Convert dict params to InstrumentFilter if needed
    if isinstance(filter_params, dict):
        from app.modules.instruments.schemas import InstrumentFilter

        filter_params = InstrumentFilter(**filter_params)

    # Apply text search from query parameter if provided
    search_text = getattr(filter_params, "query", None)
    if search_text:
        # Define which fields to search in
        search_fields = ["symbol", "isin"]
        # Apply text search to query
        from app.api.common.filtering import apply_text_search

        query = apply_text_search(query, Instrument, search_text, search_fields)

        # Additional handling for translated fields like name, which need special handling
        # This part remains custom due to the TranslatedField complexity
        f"%{search_text}%"
        # The logic for searching in translated fields would go here
        # ...

    # Apply standard filters using our utility
    query = apply_filters_from_params(query, Instrument, filter_params)

    # Get total count for pagination
    total_count = query.count()

    # Apply pagination and return results
    instruments = query.order_by(Instrument.symbol).offset(skip).limit(page_size).all()

    return instruments, total_count


def get_instrument_list(
    db: Session,
    instrument_type: Optional[InstrumentType] = None,
    exchange: Optional[Exchange] = None,
    is_active: bool = True,
    page: int = 1,
    page_size: int = 20,
) -> InstrumentList:
    """
    Get a list of instruments with optional filtering and pagination.

    Args:
        db: Database session
        instrument_type: Filter by instrument type
        exchange: Filter by exchange
        is_active: Filter by active status
        page: Page number
        page_size: Items per page

    Returns:
        List of instruments with count
    """
    # Create filter parameters
    filter_params = InstrumentFilter(
        type=instrument_type, exchange=exchange, is_active=is_active
    )

    # Get paginated results
    instruments, count = search_instruments(db, filter_params, page, page_size)

    # Convert to response schema
    return InstrumentList(
        items=[
            InstrumentResponse.model_validate(instrument) for instrument in instruments
        ],
        count=count,
    )


# --- Metadata Functions ---


def get_instrument_sectors(db: Session, language: str = "en") -> List[str]:
    """
    Get all instrument sectors with localized text.

    Args:
        db: Database session
        language: Language code for localization

    Returns:
        List of localized sector names
    """
    return crud_get_localized_sectors(db, language)


def get_instrument_industries(
    db: Session, language: str = "en", sector: Optional[str] = None
) -> List[str]:
    """
    Get all instrument industries with localized text.

    Args:
        db: Database session
        language: Language code for localization
        sector: Optional sector to filter by

    Returns:
        List of localized industry names
    """
    return crud_get_localized_industries(db, language, sector)


def get_instrument_countries(db: Session) -> List[str]:
    """
    Get all country codes used by instruments.

    Args:
        db: Database session

    Returns:
        List of country codes
    """
    return crud_get_countries(db)
