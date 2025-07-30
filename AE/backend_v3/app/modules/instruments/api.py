from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from fastcore.errors.exceptions import BadRequestError
from fastcore.schemas.response import DataResponse, ListMetadata, ListResponse

from .dependencies import get_instrument_service, get_price_history_service
from .schemas import (
    InstrumentCreate,
    InstrumentPriceHistoryCreate,
    InstrumentPriceHistoryResponse,
    InstrumentPriceHistoryUpdate,
    InstrumentResponse,
    InstrumentUpdate,
    InstrumentWithLatestPriceResponse,
)
from .service import InstrumentPriceHistoryService, InstrumentService

router = APIRouter(tags=["instruments"])


# --- Instrument Endpoints ---
@router.post("/", response_model=DataResponse[InstrumentResponse])
async def create_instrument(
    data: InstrumentCreate = Body(...),
    service: InstrumentService = Depends(get_instrument_service),
) -> DataResponse[InstrumentResponse]:
    """Create a new instrument."""
    instrument = await service.create(data)
    return DataResponse(data=instrument, message="Instrument created successfully")


@router.get(
    "/with-latest-price", response_model=ListResponse[InstrumentWithLatestPriceResponse]
)
async def list_instruments_with_latest_price(
    service: InstrumentService = Depends(get_instrument_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    symbol: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    market: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
) -> ListResponse[InstrumentWithLatestPriceResponse]:
    """
    List instruments with their latest price and price info.
    """
    filters = {
        k: v
        for k, v in {
            "symbol": symbol,
            "name": name,
            "type": type,
            "market": market,
            "currency": currency,
            "country": country,
            "sector": sector,
            "industry": industry,
            "is_active": is_active,
        }.items()
        if v is not None
    }
    offset = (page - 1) * page_size
    limit = page_size

    instruments = await service.list_with_latest_price(
        filters=filters, offset=offset, limit=limit
    )
    total = await service.count(filters=filters)

    metadata = ListMetadata(
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
        has_previous=page > 1,
    )

    return ListResponse(data=instruments, metadata=metadata)


@router.get("/{instrument_id}", response_model=DataResponse[InstrumentResponse])
async def get_instrument(
    instrument_id: int = Path(...),
    service: InstrumentService = Depends(get_instrument_service),
) -> DataResponse[InstrumentResponse]:
    """Get instrument by ID."""
    instrument = await service.get(instrument_id)
    return DataResponse(data=instrument, message="Instrument retrieved successfully")


@router.get("/by-symbol/{symbol}", response_model=DataResponse[InstrumentResponse])
async def get_instrument_by_symbol(
    symbol: str = Path(...),
    service: InstrumentService = Depends(get_instrument_service),
) -> DataResponse[InstrumentResponse]:
    """Get instrument by symbol."""
    instrument = await service.get_by_symbol(symbol)
    return DataResponse(data=instrument, message="Instrument retrieved successfully")


@router.get("/", response_model=ListResponse[InstrumentResponse])
async def list_instruments(
    service: InstrumentService = Depends(get_instrument_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    symbol: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    market: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
) -> ListResponse[InstrumentResponse]:
    """List instruments with optional filters and pagination."""
    filters = {
        k: v
        for k, v in {
            "symbol": symbol,
            "name": name,
            "type": type,
            "market": market,
            "currency": currency,
            "country": country,
            "sector": sector,
            "industry": industry,
            "is_active": is_active,
        }.items()
        if v is not None
    }

    offset = (page - 1) * page_size
    limit = page_size

    instruments = await service.list(filters=filters, offset=offset, limit=limit)
    total = await service.count(filters=filters)

    metadata = ListMetadata(
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
        has_previous=page > 1,
    )

    return ListResponse(data=instruments, metadata=metadata)


@router.patch("/{instrument_id}", response_model=DataResponse[InstrumentResponse])
async def update_instrument(
    instrument_id: int = Path(...),
    data: InstrumentUpdate = Body(...),
    service: InstrumentService = Depends(get_instrument_service),
) -> DataResponse[InstrumentResponse]:
    """Update an instrument."""
    instrument = await service.update(instrument_id, data)
    return DataResponse(data=instrument, message="Instrument updated successfully")


@router.delete(
    "/{instrument_id}",
    response_model=DataResponse[None],
)
async def delete_instrument(
    instrument_id: int = Path(...),
    service: InstrumentService = Depends(get_instrument_service),
) -> DataResponse[None]:
    """Delete an instrument."""
    await service.delete(instrument_id)
    return DataResponse(data=None, message="Instrument deleted successfully")


# --- Price History Endpoints ---
@router.post(
    "/{instrument_id}/history",
    response_model=DataResponse[InstrumentPriceHistoryResponse],
)
async def create_price_history(
    instrument_id: int = Path(...),
    data: InstrumentPriceHistoryCreate = Body(...),
    service: InstrumentPriceHistoryService = Depends(get_price_history_service),
) -> DataResponse[InstrumentPriceHistoryResponse]:
    """Create a new price history record for an instrument."""
    if data.instrument_id != instrument_id:
        raise BadRequestError(message="instrument_id in path and body must match")

    record = await service.create(data)
    return DataResponse(data=record, message="Price history created successfully")


@router.post(
    "/history/bulk",
    response_model=DataResponse[None],
)
async def bulk_insert_price_history(
    records: List[InstrumentPriceHistoryCreate] = Body(...),
    service: InstrumentPriceHistoryService = Depends(get_price_history_service),
) -> DataResponse[None]:
    """Bulk insert price history records."""
    await service.bulk_insert(records)
    return DataResponse(data=None, message="Bulk insert successful")


@router.get(
    "/{instrument_id}/history/latest",
    response_model=DataResponse[Optional[InstrumentPriceHistoryResponse]],
)
async def get_latest_price_history(
    instrument_id: int = Path(...),
    service: InstrumentPriceHistoryService = Depends(get_price_history_service),
) -> DataResponse[Optional[InstrumentPriceHistoryResponse]]:
    """Get the latest price history record for an instrument."""
    record = await service.get_latest_price(instrument_id)
    return DataResponse(
        data=record, message="Latest price history retrieved successfully"
    )


@router.get(
    "/{instrument_id}/history",
    response_model=ListResponse[InstrumentPriceHistoryResponse],
)
async def list_price_history(
    service: InstrumentPriceHistoryService = Depends(get_price_history_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    instrument_id: int = Path(...),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
) -> ListResponse[InstrumentPriceHistoryResponse]:
    """List price history records for an instrument, optionally within a date range."""

    if start and end:
        records = await service.get_prices_in_range(instrument_id, start, end)
        total = len(records)

        metadata = ListMetadata(total=total)
    else:
        filters = {"instrument_id": instrument_id}

        offset = (page - 1) * page_size
        limit = page_size

        records = await service.list(filters=filters, offset=offset, limit=limit)
        total = await service.count(filters=filters)

        metadata = ListMetadata(
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total,
            has_previous=page > 1,
        )

    return ListResponse(data=records, metadata=metadata)


@router.get(
    "/{instrument_id}/history/{market_timestamp}",
    response_model=DataResponse[InstrumentPriceHistoryResponse],
)
async def get_price_history(
    instrument_id: int = Path(...),
    market_timestamp: str = Path(
        ..., description="ISO-8601 formatted timestamp (e.g., 2024-05-07T14:30:00Z)"
    ),
    service: InstrumentPriceHistoryService = Depends(get_price_history_service),
) -> DataResponse[InstrumentPriceHistoryResponse]:
    """Get a specific price history record by instrument_id and market_timestamp."""
    try:
        # Parse the ISO string into a datetime object
        timestamp = datetime.fromisoformat(market_timestamp.replace("Z", "+00:00"))
        record = await service.get(instrument_id, timestamp)
        return DataResponse(
            data=record, message="Price history record retrieved successfully"
        )
    except ValueError as e:
        raise BadRequestError(
            message=f"Invalid timestamp format. Please use ISO-8601 format (e.g., 2024-05-07T14:30:00Z). Error: {str(e)}"
        )


@router.patch(
    "/{instrument_id}/history/{market_timestamp}",
    response_model=DataResponse[InstrumentPriceHistoryResponse],
)
async def update_price_history(
    instrument_id: int = Path(...),
    market_timestamp: str = Path(
        ..., description="ISO-8601 formatted timestamp (e.g., 2024-05-07T14:30:00Z)"
    ),
    data: InstrumentPriceHistoryUpdate = Body(...),
    service: InstrumentPriceHistoryService = Depends(get_price_history_service),
) -> DataResponse[InstrumentPriceHistoryResponse]:
    """Update a price history record by instrument_id and market_timestamp."""
    try:
        # Parse the ISO string into a datetime object
        timestamp = datetime.fromisoformat(market_timestamp.replace("Z", "+00:00"))
        record = await service.update(instrument_id, timestamp, data)
        return DataResponse(data=record, message="Price history updated successfully")
    except ValueError as e:
        raise BadRequestError(
            message=f"Invalid timestamp format. Please use ISO-8601 format (e.g., 2024-05-07T14:30:00Z). Error: {str(e)}"
        )


@router.delete(
    "/{instrument_id}/history/{market_timestamp}",
    response_model=DataResponse[None],
)
async def delete_price_history(
    instrument_id: int = Path(...),
    market_timestamp: str = Path(
        ..., description="ISO-8601 formatted timestamp (e.g., 2024-05-07T14:30:00Z)"
    ),
    service: InstrumentPriceHistoryService = Depends(get_price_history_service),
) -> DataResponse[None]:
    """Delete a price history record by instrument_id and market_timestamp."""
    try:
        # Parse the ISO string into a datetime object
        timestamp = datetime.fromisoformat(market_timestamp.replace("Z", "+00:00"))
        await service.delete(instrument_id, timestamp)
        return DataResponse(
            data=None, message="Price history record deleted successfully"
        )
    except ValueError as e:
        raise BadRequestError(
            message=f"Invalid timestamp format. Please use ISO-8601 format (e.g., 2024-05-07T14:30:00Z). Error: {str(e)}"
        )
