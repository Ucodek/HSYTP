"""
Instruments module for managing financial instruments.

This module provides:
- Instrument creation and management
- Instrument price data
- Historical price data
- Instrument metadata (sectors, industries, countries)
"""

# API router
from app.modules.instruments.api import router as instruments_router

# Dependencies
from app.modules.instruments.dependencies import (
    InstrumentBySymbolDep,
    InstrumentDep,
    InstrumentFilterParams,
    InstrumentParams,
    InstrumentParamsDep,
    InstrumentQueryParams,
    InstrumentQueryParamsDep,
    SearchParamsDep,
    get_instrument_by_id_dep,
    get_instrument_by_symbol_dep,
    get_instrument_query_params,
    get_search_params,
)

# Models
from app.modules.instruments.models import (
    COUNTRY_CODE_LENGTH,
    CURRENCY_CODE_LENGTH,
    DEFAULT_CURRENCY,
    ISIN_LENGTH,
    SYMBOL_MAX_LENGTH,
    Exchange,
    Instrument,
    InstrumentPrice,
    InstrumentType,
)

# Schemas
from app.modules.instruments.schemas import (
    InstrumentBase,
    InstrumentCreate,
    InstrumentFilter,
    InstrumentList,
    InstrumentPriceCreate,
    InstrumentPriceResponse,
    InstrumentPriceUpdate,
    InstrumentResponse,
    InstrumentSearchParams,
    InstrumentUpdate,
    LocalizedInstrumentResponse,
    PriceData,
)

# Utilities
from app.modules.instruments.utils import get_translated_text, safe_numeric

__all__ = [
    # Models
    "Instrument",
    "InstrumentPrice",
    "InstrumentType",
    "Exchange",
    "CURRENCY_CODE_LENGTH",
    "COUNTRY_CODE_LENGTH",
    "SYMBOL_MAX_LENGTH",
    "ISIN_LENGTH",
    "DEFAULT_CURRENCY",
    # Schemas
    "InstrumentBase",
    "InstrumentCreate",
    "InstrumentUpdate",
    "InstrumentResponse",
    "LocalizedInstrumentResponse",
    "InstrumentPriceUpdate",
    "InstrumentPriceCreate",
    "InstrumentPriceResponse",
    "InstrumentFilter",
    "InstrumentSearchParams",
    "InstrumentList",
    "PriceData",
    # Utilities
    "safe_numeric",
    "get_translated_text",
    # Dependencies
    "get_instrument_by_id_dep",
    "get_instrument_by_symbol_dep",
    "get_search_params",
    "InstrumentDep",
    "InstrumentBySymbolDep",
    "SearchParamsDep",
    "InstrumentFilterParams",
    "InstrumentParams",
    "InstrumentParamsDep",
    "InstrumentQueryParams",
    "InstrumentQueryParamsDep",
    "get_instrument_query_params",
    # Router
    "instruments_router",
]
