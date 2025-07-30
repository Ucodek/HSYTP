"""
API endpoints for instruments module.

This module provides REST API endpoints for managing financial instruments,
including creation, retrieval, updating, and searching for various tradable assets.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, Path, Query, status
from sqlalchemy.orm import Session

from app.api.common.filtering import apply_filters_from_params
from app.api.common.pagination import PagedResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.models import User
from app.modules.instruments.dependencies import (
    InstrumentBySymbolDep,
    InstrumentDep,
    InstrumentQueryParamsDep,
)
from app.modules.instruments.models import Exchange, Instrument, InstrumentType
from app.modules.instruments.schemas import (
    InstrumentCreate,
    InstrumentPriceUpdate,
    InstrumentResponse,
    InstrumentUpdate,
    LocalizedInstrumentResponse,
)
from app.modules.instruments.service import (
    create_instrument,
    deactivate_instrument,
    delete_instrument,
    get_instrument_countries,
    get_instrument_industries,
    get_instrument_sectors,
    update_instrument,
    update_price,
)
from app.utils.i18n import get_language
from app.utils.response import (
    create_success_response,
    created_response,
    no_content_response,
)

router = APIRouter(tags=["instruments"])

# --- Instrument Management ---


@router.post(
    "/",
    response_model=InstrumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new instrument",
)
async def create_new_instrument(
    instrument_data: InstrumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Create a new financial instrument.

    This endpoint allows creating a new financial instrument in the system.

    - **symbol**: Trading symbol (must be unique, automatically converted to uppercase)
    - **name**: Instrument name in multiple languages (at least English required)
    - **type**: Instrument type (stock, bond, ETF, etc.)
    - **exchange**: Exchange where traded (optional)
    - **currency**: ISO 4217 currency code (defaults to USD)
    - **description**: Detailed description (optional)
    - **sector**: Business sector (optional)
    - **industry**: Industry category (optional)
    - **country**: ISO 3166-1 alpha-2 country code (optional)
    - **isin**: International Securities Identification Number (optional)

    Requires admin privileges.
    """
    created = create_instrument(db, instrument_data)
    return created_response(created)


@router.put(
    "/{instrument_id}",
    response_model=LocalizedInstrumentResponse,
    summary="Update instrument details",
)
async def update_instrument_details(
    instrument_id: int = Path(..., description="Instrument ID", gt=0),
    update_data: InstrumentUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    accept_language: Optional[str] = Header(None, description="Preferred language"),
):
    """
    Update a financial instrument's details.

    This endpoint allows updating details of an existing instrument.
    The response is localized based on the Accept-Language header.

    - **name**: Updated name in multiple languages (optional)
    - **description**: Updated description (optional)
    - **type**: Updated instrument type (optional)
    - **exchange**: Updated exchange (optional)
    - **currency**: Updated currency code (optional)
    - **sector**: Updated business sector (optional)
    - **industry**: Updated industry category (optional)
    - **country**: Updated country code (optional)
    - **isin**: Updated ISIN (optional)
    - **is_active**: Updated active status (optional)

    Requires admin privileges.
    """
    language = get_language(accept_language)
    updated = update_instrument(db, instrument_id, update_data)

    return create_success_response(
        LocalizedInstrumentResponse.from_instrument(updated, language),
        message="Instrument updated successfully",
    )


@router.patch(
    "/{instrument_id}/price",
    response_model=LocalizedInstrumentResponse,
    summary="Update instrument price",
)
async def update_instrument_price(
    instrument_id: int = Path(..., description="Instrument ID", gt=0),
    price_data: InstrumentPriceUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    accept_language: Optional[str] = Header(None, description="Preferred language"),
):
    """
    Update a financial instrument's price information.

    This endpoint allows updating the price data of an existing instrument.
    The response is localized based on the Accept-Language header.

    - **current_price**: Current trading price (required)
    - **previous_close**: Previous day's closing price (optional)
    - **open_price**: Opening price (optional)
    - **day_high**: Day's high price (optional)
    - **day_low**: Day's low price (optional)
    - **w52_high**: 52-week high price (optional)
    - **w52_low**: 52-week low price (optional)
    - **volume**: Trading volume (optional)
    - **avg_volume**: Average trading volume (optional)
    - **market_cap**: Market capitalization (optional)
    - **beta**: Beta value (optional)
    - **pe_ratio**: Price-to-earnings ratio (optional)
    - **eps**: Earnings per share (optional)
    - **dividend_yield**: Dividend yield percentage (optional)

    Requires admin privileges.
    """
    language = get_language(accept_language)
    updated = update_price(db, instrument_id, price_data)

    return create_success_response(
        LocalizedInstrumentResponse.from_instrument(updated, language),
        message="Price information updated successfully",
    )


@router.delete(
    "/{instrument_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete instrument",
)
async def delete_instrument_endpoint(
    instrument_id: int = Path(..., description="Instrument ID", gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Delete a financial instrument permanently.

    This endpoint permanently removes an instrument from the database.
    Consider using the deactivate endpoint instead to maintain historical data.

    Requires admin privileges.
    """
    delete_instrument(db, instrument_id)
    return no_content_response()


@router.post(
    "/{instrument_id}/deactivate",
    response_model=LocalizedInstrumentResponse,
    summary="Deactivate instrument",
)
async def deactivate_instrument_endpoint(
    instrument_id: int = Path(..., description="Instrument ID", gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    accept_language: Optional[str] = Header(None, description="Preferred language"),
):
    """
    Deactivate a financial instrument instead of deleting it.

    This endpoint marks an instrument as inactive while preserving all data.
    Deactivated instruments won't appear in default search results.
    The response is localized based on the Accept-Language header.

    Requires admin privileges.
    """
    language = get_language(accept_language)
    deactivated = deactivate_instrument(db, instrument_id)

    return create_success_response(
        LocalizedInstrumentResponse.from_instrument(deactivated, language),
        message="Instrument deactivated successfully",
    )


# --- Instrument Retrieval ---


@router.get(
    "/{instrument_id}",
    response_model=LocalizedInstrumentResponse,
    summary="Get instrument by ID",
)
async def get_instrument_by_id_endpoint(
    instrument: InstrumentDep,
    accept_language: Optional[str] = Header(None, description="Preferred language"),
):
    """
    Get detailed information about an instrument by its ID.

    This endpoint retrieves comprehensive information about a single instrument.
    The response is localized based on the Accept-Language header.

    - **instrument_id**: The numeric ID of the instrument to retrieve
    - **accept_language**: Optional language code for localized fields
    """
    language = get_language(accept_language)
    return create_success_response(
        LocalizedInstrumentResponse.from_instrument(instrument, language)
    )


@router.get(
    "/symbol/{symbol}",
    response_model=LocalizedInstrumentResponse,
    summary="Get instrument by symbol",
)
async def get_instrument_by_symbol_endpoint(
    instrument: InstrumentBySymbolDep,
    accept_language: Optional[str] = Header(None, description="Preferred language"),
):
    """
    Get detailed information about an instrument by its trading symbol.

    This endpoint retrieves comprehensive information about a single instrument using its trading symbol.
    The response is localized based on the Accept-Language header.

    - **symbol**: Trading symbol of the instrument (case-insensitive)
    - **accept_language**: Optional language code for localized fields
    """
    language = get_language(accept_language)
    return create_success_response(
        LocalizedInstrumentResponse.from_instrument(instrument, language)
    )


@router.get(
    "/",
    response_model=PagedResponse[LocalizedInstrumentResponse],
    summary="List instruments",
)
async def list_instruments(
    params: InstrumentQueryParamsDep,
    accept_language: Optional[str] = Header(None, description="Preferred language"),
    db: Session = Depends(get_db),
):
    """
    List financial instruments with filtering, sorting, and pagination.

    This endpoint provides a paginated list of financial instruments with
    optional filtering and sorting. Results are localized based on the Accept-Language header.

    - **filter parameters**: Various filter options (type, exchange, country, etc.)
    - **sort**: Field to sort by (symbol, type, exchange, etc.)
    - **order**: Sort order (asc or desc)
    - **page**: Page number for pagination (starts at 1)
    - **page_size**: Number of items per page (between 1 and 100)
    - **accept_language**: Language code for localized fields
    """
    # Get language preference
    language = get_language(accept_language)

    # Use the configuration from the config file instead of hardcoding
    from app.modules.instruments.config import INSTRUMENT_SORT_FIELDS

    # Use apply_all_params to simplify implementation
    query = db.query(Instrument)
    instruments, total = params.apply_all_params(
        query, Instrument, **INSTRUMENT_SORT_FIELDS
    )

    # Create localized response items
    localized_items = [
        LocalizedInstrumentResponse.from_instrument(item, language)
        for item in instruments
    ]

    # Create standardized paged response and explicitly convert to dictionary
    paged_response = PagedResponse.create(localized_items, total, params.pagination)

    # Fix: Explicitly convert the Pydantic model to a dictionary for JSON serialization
    return create_success_response(paged_response.model_dump())


@router.get(
    "/search",
    response_model=PagedResponse[LocalizedInstrumentResponse],
    summary="Search instruments",
)
async def search_instruments_endpoint(
    params: InstrumentQueryParamsDep,
    query: Optional[str] = Query(None, description="Text search query"),
    accept_language: Optional[str] = Header(None, description="Preferred language"),
    db: Session = Depends(get_db),
):
    """
    Search for instruments with advanced filtering, sorting, and pagination.

    This endpoint provides powerful search capabilities across all instruments.
    Results are localized based on the Accept-Language header.

    - **query**: Text search query to match against symbols, names, etc. (optional)
    - **filter parameters**: Various filter options
    - **sort**: Field to sort by (symbol, type, exchange, etc.)
    - **order**: Sort order (asc or desc)
    - **page**: Page number for pagination (starts at 1)
    - **page_size**: Number of items per page (between 1 and 100)
    - **accept_language**: Language code for localized fields
    """
    # Get language from header
    language = get_language(accept_language)

    # Get configuration from the config file
    from app.modules.instruments.config import INSTRUMENT_SORT_FIELDS

    # Combine text query with filter parameters
    filter_data = params.filters.model_dump()
    filter_data["query"] = query

    # Create a custom filter params object with the search query
    from app.modules.instruments.schemas import InstrumentFilter

    custom_filters = InstrumentFilter(**filter_data)

    # Create base query
    base_query = db.query(Instrument)

    # Apply text search separately if needed
    if query:
        from app.api.common.filtering import apply_text_search

        base_query = apply_text_search(
            base_query, Instrument, query, ["symbol", "isin"]
        )

    # Apply filters
    filtered_query = apply_filters_from_params(base_query, Instrument, custom_filters)

    # Get total count
    total = filtered_query.count()

    # Apply sorting if provided
    if params.sorting:
        filtered_query = params.sorting.apply_to_query(
            filtered_query,
            Instrument,
            allowed_fields=INSTRUMENT_SORT_FIELDS["allowed_fields"],
            field_map=INSTRUMENT_SORT_FIELDS["field_map"],
            default_field=INSTRUMENT_SORT_FIELDS["default_field"],
        )

    # Apply pagination
    paginated_query = params.pagination.paginate_query(filtered_query)
    instruments = paginated_query.all()

    # Create localized response items
    localized_items = [
        LocalizedInstrumentResponse.from_instrument(item, language)
        for item in instruments
    ]

    # Create standardized paged response
    paged_response = PagedResponse.create(localized_items, total, params.pagination)

    # Fix: Explicitly convert the Pydantic model to a dictionary for JSON serialization
    return create_success_response(paged_response.model_dump())


# --- Metadata Endpoints ---


@router.get("/metadata/types", response_model=List[str], summary="Get instrument types")
async def get_instrument_types():
    """
    Get all valid instrument types.

    Returns a list of all possible instrument type values that can be used in filtering
    and when creating new instruments.
    """
    return create_success_response([type_value.value for type_value in InstrumentType])


@router.get("/metadata/exchanges", response_model=List[str], summary="Get exchanges")
async def get_exchanges():
    """
    Get all valid exchanges.

    Returns a list of all possible exchange values that can be used in filtering
    and when creating new instruments.
    """
    return create_success_response([exchange.value for exchange in Exchange])


@router.get("/metadata/sectors", response_model=List[str], summary="Get sectors")
async def get_sectors(
    db: Session = Depends(get_db),
    accept_language: Optional[str] = Header(None, description="Preferred language"),
):
    """
    Get all unique sectors from instruments.

    Returns a list of all business sectors used by instruments in the system.
    Results are localized based on the Accept-Language header.

    - **accept_language**: Language code for localized sector names
    """
    language = get_language(accept_language)
    sectors = get_instrument_sectors(db, language)
    return create_success_response(sectors)


@router.get("/metadata/industries", response_model=List[str], summary="Get industries")
async def get_industries(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db),
    accept_language: Optional[str] = Header(None, description="Preferred language"),
):
    """
    Get all unique industries, optionally filtered by sector.

    Returns a list of all industry categories used by instruments in the system.
    Can be filtered by sector to show only industries within a specific sector.
    Results are localized based on the Accept-Language header.

    - **sector**: Optional sector name to filter industries by
    - **accept_language**: Language code for localized industry names
    """
    language = get_language(accept_language)
    industries = get_instrument_industries(db, language, sector)
    return create_success_response(industries)


@router.get("/metadata/countries", response_model=List[str], summary="Get countries")
async def get_countries(db: Session = Depends(get_db)):
    """
    Get all unique country codes used by instruments.

    Returns a list of all country codes (ISO 3166-1 alpha-2) used by instruments
    in the system.
    """
    countries = get_instrument_countries(db)
    return create_success_response(countries)
