import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select  # Add select and func imports
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.market import market_index, market_movers
from app.db.session import get_db
from app.models.market import MarketIndex  # Add MarketIndex model import
from app.models.users import User
from app.schemas.base import DataResponse, ListResponse
from app.schemas.market import (
    MarketIndex as MarketIndexSchema,
    MarketMoversResponse,
    MarketMoverType,
)
from app.utils.response import create_list_response, create_response

router = APIRouter()


@router.get("/movers", response_model=DataResponse[MarketMoversResponse])
async def get_market_movers(
    type: MarketMoverType = Query(..., description="Type of movers to retrieve"),
    limit: int = Query(5, ge=1, le=20, description="Number of results to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get market movers (gainers, losers, or most active).
    """
    if type == MarketMoverType.GAINERS:
        instruments = await market_movers.get_gainers(db, limit=limit)
    elif type == MarketMoverType.LOSERS:
        instruments = await market_movers.get_losers(db, limit=limit)
    elif type == MarketMoverType.ACTIVE:
        instruments = await market_movers.get_most_active(db, limit=limit)
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid market mover type: {type}"
        )

    # Prepare the response
    response_data = []
    for instrument in instruments:
        if instrument.price:
            response_data.append(
                {
                    "instrument": instrument,
                    "price_change": instrument.price.price_change,
                    "change_percent": instrument.price.change_percent,
                    "volume": instrument.price.volume,
                }
            )

    return create_response(
        data={
            "type": type,
            "data": response_data,
            "timestamp": datetime.now(timezone.utc),
        },
        data_timestamp=int(time.time()),
    )


@router.get("/indices", response_model=ListResponse[MarketIndexSchema])
async def get_market_indices(
    country: Optional[str] = Query(
        None, description="Filter by country code (e.g., USA, TUR)"
    ),
    skip: int = Query(0, ge=0, description="Number of items to skip for pagination"),
    limit: int = Query(
        10, ge=1, le=100, description="Number of items to return for pagination"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a list of market indices with optional filtering by country.
    """
    if country:
        indices = await market_index.get_by_country(
            db, country=country, skip=skip, limit=limit
        )
    else:
        indices = await market_index.get_multi(db, skip=skip, limit=limit)

    # Get total count for pagination
    count_query = await db.execute(
        select(func.count(MarketIndex.id)).where(
            MarketIndex.country == country if country else True
        )
    )
    total = count_query.scalar() or 0

    # Return standardized list response with pagination
    return create_list_response(
        data=indices,
        total=total,
        limit=limit,
        offset=skip,
        # Use current time as data_timestamp since this is latest data
        data_timestamp=int(time.time()),
    )


@router.get("/indices/{symbol}", response_model=DataResponse[MarketIndexSchema])
async def get_market_index(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed information about a specific market index.
    """
    index = await market_index.get_by_symbol_with_price(db, symbol=symbol)
    if not index:
        raise HTTPException(status_code=404, detail=f"Market index {symbol} not found")

    return create_response(data=index, data_timestamp=int(time.time()))
