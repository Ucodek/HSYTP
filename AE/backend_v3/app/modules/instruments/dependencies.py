"""
Dependency injection setup for the instruments module.

Provides dependencies for InstrumentService and InstrumentPriceHistoryService.
"""

from fastapi import Depends
from fastcore.db.manager import get_db

from .service import InstrumentPriceHistoryService, InstrumentService


def get_instrument_service(session=Depends(get_db)):
    """
    Dependency provider for InstrumentService.

    Args:
        session: Database session provided by get_db.
    Returns:
        InstrumentService: Service instance for instrument operations.
    """
    return InstrumentService(session)


def get_price_history_service(session=Depends(get_db)):
    """
    Dependency provider for InstrumentPriceHistoryService.

    Args:
        session: Database session provided by get_db.
    Returns:
        InstrumentPriceHistoryService: Service instance for price history operations.
    """
    return InstrumentPriceHistoryService(session)
