"""
FastAPI dependencies for the instruments module.

This module provides reusable dependencies for instrument-related endpoints,
including functions to retrieve instruments by ID or symbol and to parse
search parameters from query parameters.
"""
from typing import Annotated, Optional

from fastapi import Depends, Path, Query
from sqlalchemy.orm import Session

from app.api.common.filtering import FilteredParams, create_filter_model
from app.api.common.query_params import QueryParams
from app.db.session import get_db
from app.errors.error_codes import ErrorCode
from app.errors.exceptions import NotFoundError
from app.modules.instruments.models import Exchange, Instrument, InstrumentType
from app.modules.instruments.schemas import InstrumentSearchParams
from app.modules.instruments.service import (
    find_instrument_by_symbol,
    get_instrument_by_id,
)

# --- Common Dependencies ---


async def get_instrument_by_id_dep(
    instrument_id: int = Path(..., gt=0, description="Instrument ID"),
    db: Session = Depends(get_db),
) -> Instrument:
    """
    Dependency to get an instrument by ID.

    Args:
        instrument_id: ID of the instrument to retrieve (must be positive)
        db: Database session

    Returns:
        Instrument object

    Raises:
        NotFoundError: If instrument is not found
    """
    instrument = get_instrument_by_id(db, instrument_id)
    if not instrument:
        raise NotFoundError(
            detail=f"Instrument with ID {instrument_id} not found",
            error_code=ErrorCode.RES_NOT_FOUND,
        )
    return instrument


async def get_instrument_by_symbol_dep(
    symbol: str = Path(..., min_length=1, description="Instrument trading symbol"),
    db: Session = Depends(get_db),
) -> Instrument:
    """
    Dependency to get an instrument by its trading symbol.

    Args:
        symbol: Trading symbol of the instrument
        db: Database session

    Returns:
        Instrument object

    Raises:
        NotFoundError: If instrument is not found
    """
    instrument = find_instrument_by_symbol(db, symbol)
    if not instrument:
        raise NotFoundError(
            detail=f"Instrument with symbol '{symbol}' not found",
            error_code=ErrorCode.RES_NOT_FOUND,
        )
    return instrument


# --- Search Parameters Dependency ---

# Create a type-safe filter model based on the Instrument model
# Exclude fields that need special handling (translated fields)
InstrumentFilterParams = create_filter_model(
    Instrument,
    exclude_fields=["name", "description", "sector", "industry"],
)


async def get_search_params(
    query: Optional[str] = Query(
        None, description="Search query for symbol, name, ISIN"
    ),
    type: Optional[InstrumentType] = Query(
        None, description="Filter by instrument type"
    ),
    exchange: Optional[Exchange] = Query(None, description="Filter by exchange"),
    sector: Optional[str] = Query(None, description="Filter by business sector"),
    country: Optional[str] = Query(
        None, description="Filter by country code (ISO 3166-1 alpha-2)"
    ),
    is_active: Optional[bool] = Query(True, description="Show only active instruments"),
) -> InstrumentSearchParams:
    """
    Dependency to create search parameters from query parameters.

    This dependency extracts search and filter parameters from query parameters
    and creates an InstrumentSearchParams object to be used in search operations.

    Args:
        query: Text search query
        type: Filter by instrument type
        exchange: Filter by exchange
        sector: Filter by sector
        country: Filter by country code
        is_active: Show only active instruments (default: True)

    Returns:
        Consolidated search parameters object
    """
    return InstrumentSearchParams(
        query=query,
        type=type,
        exchange=exchange,
        sector=sector,
        country=country,
        is_active=is_active,
    )


# Create combined filtering and pagination parameters
InstrumentParams = FilteredParams[InstrumentFilterParams]


def get_instrument_params():
    """Get combined filtering and pagination parameters for instruments."""
    return FilteredParams.create_dependency(InstrumentFilterParams)


# Create combined query parameters (filtering + pagination + sorting)
InstrumentQueryParams = QueryParams[InstrumentFilterParams]


def get_instrument_query_params():
    """Get combined filtering, pagination, and sorting parameters for instruments."""
    return QueryParams.create_dependency(InstrumentFilterParams)


# --- Type Aliases ---

# These provide convenient type annotations for FastAPI dependency injection
InstrumentDep = Annotated[Instrument, Depends(get_instrument_by_id_dep)]
InstrumentBySymbolDep = Annotated[Instrument, Depends(get_instrument_by_symbol_dep)]
SearchParamsDep = Annotated[InstrumentSearchParams, Depends(get_search_params)]
InstrumentParamsDep = Annotated[InstrumentParams, Depends(get_instrument_params())]
InstrumentQueryParamsDep = Annotated[
    InstrumentQueryParams, Depends(get_instrument_query_params())
]
DbSession = Annotated[Session, Depends(get_db)]
