"""Common dependencies for API endpoints."""
from typing import Annotated, Any, Callable, Dict, Optional, Type

from fastapi import Depends, Header, Query, Request
from sqlalchemy.orm import Session

from app.api.common.filtering import FilterParams
from app.api.common.pagination import PaginationParams, get_pagination_params
from app.api.common.query_params import QueryParams
from app.api.common.sorting import SortingParams, get_sorting_params
from app.db.session import get_db
from app.modules.auth.dependencies import (
    get_current_active_user,
    get_current_admin_user,
    get_current_user,
    optional_current_user,
)
from app.modules.auth.models import User
from app.utils.i18n import get_language

# Re-export auth dependencies for convenience
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
OptionalUser = Annotated[Optional[User], Depends(optional_current_user)]
DbSession = Annotated[Session, Depends(get_db)]

# Add language dependency annotation for consistent language handling
Language = Annotated[str, Depends(get_language)]

# Pagination, Sorting, and Filtering dependencies
PaginationDep = Annotated[PaginationParams, Depends(get_pagination_params)]
SortingDep = Annotated[SortingParams, Depends(get_sorting_params)]


# Common query parameters for filtering and sorting
async def common_query_parameters(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of items to return"
    ),
    sort: Optional[str] = Query(None, description="Field to sort by"),
    order: str = Query("asc", description="Sort order (asc or desc)"),
    q: Optional[str] = Query(None, description="Search query"),
    language: str = Depends(get_language),
) -> Dict[str, Any]:
    """
    Common query parameters for list endpoints.

    Args:
        skip: Number of items to skip (for pagination)
        limit: Maximum number of items to return
        sort: Field to sort by
        order: Sort order (asc or desc)
        q: Search query
        language: Language preference from Accept-Language header

    Returns:
        Dictionary with query parameters
    """
    return {
        "skip": skip,
        "limit": limit,
        "sort": sort,
        "order": order.lower(),
        "q": q,
        "language": language,
    }


CommonQueryParams = Annotated[Dict[str, Any], Depends(common_query_parameters)]


# Request ID extraction
def get_request_id(
    request: Request, x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
) -> Optional[str]:
    """
    Get the request ID from the X-Request-ID header or from request state.

    Args:
        request: FastAPI request
        x_request_id: X-Request-ID header

    Returns:
        Request ID
    """
    if x_request_id:
        return x_request_id

    return getattr(request.state, "request_id", None)


RequestId = Annotated[Optional[str], Depends(get_request_id)]


# Create a factory function for QueryParams dependency
def create_query_params_dependency(filter_class: Type[FilterParams[Any]]) -> Callable:
    """
    Create a dependency that combines filtering, sorting, and pagination.

    Args:
        filter_class: FilterParams class to use

    Returns:
        Dependency function that returns a QueryParams instance
    """
    return QueryParams.create_dependency(filter_class)
