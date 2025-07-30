import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.v1.endpoints import historical
from app.crud.instruments import instrument
from app.models.instruments import Instrument
from app.schemas.base import DataResponse, ListResponse
from app.schemas.instruments import (
    Instrument as InstrumentSchema,
    InstrumentCreate,
    InstrumentUpdate,
)
from app.utils.response import create_list_response, create_response

router = APIRouter()


@router.get("", response_model=ListResponse[InstrumentSchema])
async def get_instruments(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    country: Optional[str] = None,
):
    """
    Retrieve instruments with optional filtering.
    """
    # Get filtered instruments
    if type:
        instruments = await instrument.get_by_type(
            db, type=type, skip=skip, limit=limit
        )
        # Get total count for type filter
        count_query = await db.execute(
            select(func.count(Instrument.id)).where(Instrument.type == type)
        )
        total = count_query.scalar() or 0
    elif country:
        instruments = await instrument.get_by_country(
            db, country=country, skip=skip, limit=limit
        )
        # Get total count for country filter
        count_query = await db.execute(
            select(func.count(Instrument.id)).where(Instrument.country == country)
        )
        total = count_query.scalar() or 0
    else:
        instruments = await instrument.get_multi(db, skip=skip, limit=limit)
        # Get total count without filters
        count_query = await db.execute(select(func.count(Instrument.id)))
        total = count_query.scalar() or 0

    # Return standardized list response with pagination
    return create_list_response(
        data=instruments,
        total=total,
        limit=limit,
        offset=skip,
        data_timestamp=int(time.time()),  # Current time as data timestamp
    )


@router.get("/{symbol}", response_model=DataResponse[InstrumentSchema])
async def get_instrument_by_symbol(
    symbol: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a specific instrument by symbol.
    """
    db_instrument = await instrument.get_by_symbol(db, symbol=symbol)
    if db_instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")

    # Use create_response instead of direct dictionary
    return create_response(data=db_instrument, data_timestamp=int(time.time()))


@router.post("", response_model=DataResponse[InstrumentSchema], status_code=201)
async def create_instrument(
    *,
    db: AsyncSession = Depends(get_db),
    instrument_in: InstrumentCreate,
):
    """
    Create a new instrument.
    """
    # Check if instrument already exists
    db_instrument = await instrument.get_by_symbol(db, symbol=instrument_in.symbol)
    if db_instrument:
        raise HTTPException(
            status_code=400,
            detail=f"Instrument with symbol {instrument_in.symbol} already exists",
        )
    result = await instrument.create(db=db, obj_in=instrument_in)

    # Use create_response instead of direct dictionary
    return create_response(data=result, data_timestamp=int(time.time()))


@router.put("/{symbol}", response_model=DataResponse[InstrumentSchema])
async def update_instrument(
    *,
    db: AsyncSession = Depends(get_db),
    symbol: str,
    instrument_in: InstrumentUpdate,
):
    """
    Update an existing instrument.

    Note: Make sure your JSON is valid with no trailing commas.

    Example:
    ```json
    {
      "name": {
        "en-US": "Amazing Name"
      }
    }
    ```
    """
    db_instrument = await instrument.get_by_symbol(db, symbol=symbol)
    if not db_instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    result = await instrument.update(db=db, db_obj=db_instrument, obj_in=instrument_in)

    # Use create_response instead of direct dictionary
    return create_response(data=result, data_timestamp=int(time.time()))


@router.delete("/{symbol}", response_model=DataResponse[InstrumentSchema])
async def delete_instrument(
    *,
    db: AsyncSession = Depends(get_db),
    symbol: str,
):
    """
    Delete an instrument.
    """
    db_instrument = await instrument.get_by_symbol(db, symbol=symbol)
    if not db_instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    result = await instrument.remove(db=db, id=db_instrument.id)

    # Use create_response instead of direct dictionary
    return create_response(data=result, data_timestamp=int(time.time()))


router.include_router(historical.router, prefix="")
