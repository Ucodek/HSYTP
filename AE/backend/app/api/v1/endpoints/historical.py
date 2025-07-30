import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.historical import historical_data
from app.crud.instruments import instrument as instrument_crud
from app.db.session import get_db
from app.models.users import User
from app.schemas.base import DataResponse
from app.schemas.historical import (
    HistoricalDataResponse,
    HistoricalQueryParams,
)
from app.utils.response import create_error_response, create_response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{symbol}/historical", response_model=DataResponse[HistoricalDataResponse])
async def get_historical_data(
    symbol: str,
    params: HistoricalQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    use_cache: bool = Query(
        True, description="Whether to use cached data if available"
    ),
):
    """Get historical price data for a specific instrument."""
    try:
        # Get the instrument by symbol
        instrument = await instrument_crud.get_by_symbol(db, symbol=symbol)
        if not instrument:
            logger.warning(f"Instrument not found: {symbol}")
            raise HTTPException(
                status_code=404, detail=f"Instrument {symbol} not found"
            )

        # Get historical data with retry capability
        try:
            data = await historical_data.get_for_instrument(
                db,
                instrument_id=instrument.id,
                period=params.period,
                interval=params.interval,
                use_cache=use_cache,
            )
        except Exception as e:
            logger.error(f"Failed to retrieve historical data: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Error retrieving historical data: {str(e)}"
            )

        # Check if we got any data
        if not data:
            logger.info(
                f"No historical data found for {symbol} with period={params.period}, "
                f"interval={params.interval}"
            )
            return create_response(
                data={
                    "instrument_id": instrument.id,
                    "symbol": instrument.symbol,
                    "data": [],
                },
                data_timestamp=None,
            )

        # Format the data for response
        formatted_data = []
        for point in data:
            # Handle the case where point might be a Row from a raw SQL query
            if hasattr(point, "bucket"):  # From time_bucket query
                formatted_data.append(
                    {
                        "timestamp": point.bucket,
                        "open": point.open,
                        "high": point.high,
                        "low": point.low,
                        "close": point.close,
                        "volume": point.volume,
                        "adjusted_close": point.adjusted_close,
                    }
                )
            elif hasattr(point, "_mapping"):  # SQLAlchemy 1.4+ result
                row_data = dict(point._mapping)
                formatted_data.append(
                    {
                        "timestamp": row_data.get("timestamp")
                        or row_data.get("bucket")
                        or row_data.get("day"),
                        "open": row_data.get("open"),
                        "high": row_data.get("high"),
                        "low": row_data.get("low"),
                        "close": row_data.get("close"),
                        "volume": row_data.get("volume"),
                        "adjusted_close": row_data.get("adjusted_close"),
                    }
                )
            elif isinstance(point, dict):  # Already a dict (e.g. from cache)
                formatted_data.append(point)
            else:  # Regular ORM object
                formatted_data.append(point)

        # Get the timestamp of the newest data point for data_timestamp
        data_timestamp = None
        if formatted_data:
            try:
                newest_point = max(
                    formatted_data,
                    key=lambda x: x["timestamp"]
                    if isinstance(x, dict)
                    else x.timestamp,
                )
                timestamp = (
                    newest_point["timestamp"]
                    if isinstance(newest_point, dict)
                    else newest_point.timestamp
                )
                data_timestamp = int(timestamp.timestamp())
            except (AttributeError, TypeError, KeyError) as e:
                logger.warning(f"Could not determine data timestamp: {e}")

        # Return standardized response
        return create_response(
            data={
                "instrument_id": instrument.id,
                "symbol": instrument.symbol,
                "data": formatted_data,
            },
            data_timestamp=data_timestamp,
        )
    except HTTPException:
        # Re-raise HTTP exceptions for proper handling
        raise
    except Exception as e:
        logger.exception(f"Unhandled error in get_historical_data: {e}")
        return create_error_response(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred while processing your request",
            status_code=500,
        )
