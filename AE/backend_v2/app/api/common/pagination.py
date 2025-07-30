"""
Pagination utilities for API endpoints.

This module provides standardized pagination for API endpoints, including:
- Query parameter handling with FastAPI dependencies
- SQLAlchemy query pagination
- Consistent response formatting
"""
from math import ceil
from typing import Any, Callable, Dict, Generic, List, Type, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Query as SQLAlchemyQuery

T = TypeVar("T")
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class PaginationParams:
    """
    Pagination parameters for list endpoints.

    This class handles pagination parameters from requests and
    provides convenient methods for applying pagination to queries.

    Example:
        ```python
        @router.get("/items")
        async def list_items(
            pagination: PaginationParams = Depends(),
            db: Session = Depends(get_db)
        ):
            query = db.query(Item)
            total = query.count()
            items = pagination.paginate_query(query).all()
            return PagedResponse.create(items, total, pagination)
        ```
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    ):
        """
        Initialize pagination parameters.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
        """
        self.page = page
        self.page_size = page_size

    @property
    def skip(self) -> int:
        """Calculate number of items to skip."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get number of items to return."""
        return self.page_size

    def paginate_query(self, query: SQLAlchemyQuery) -> SQLAlchemyQuery:
        """
        Apply pagination to a SQLAlchemy query.

        Args:
            query: SQLAlchemy query object

        Returns:
            Paginated query
        """
        return query.offset(self.skip).limit(self.limit)

    def get_pagination_info(self, total_items: int) -> Dict[str, int]:
        """
        Get pagination metadata.

        Args:
            total_items: Total number of items

        Returns:
            Dictionary with pagination metadata
        """
        total_pages = ceil(total_items / self.page_size) if total_items > 0 else 1

        return {
            "page": self.page,
            "page_size": self.page_size,
            "total": total_items,
            "pages": total_pages,
            "has_next": self.page < total_pages,
            "has_prev": self.page > 1,
        }

    def paginate_and_count_query(
        self, query: SQLAlchemyQuery, model: Type[ModelType], count_col: Any = None
    ) -> tuple[SQLAlchemyQuery, int]:
        """
        Apply pagination to a query and get count in one operation.

        This method optimizes database operations by splitting the query
        to get paginated results and count separately.

        Args:
            query: SQLAlchemy query to paginate
            model: Model class being queried
            count_col: Column to use for count (defaults to model.id)

        Returns:
            Tuple of (paginated query, total count)
        """
        # Use the provided count column or default to model.id
        if count_col is None:
            count_col = model.id

        # Get total count
        count_query = query.with_entities(func.count(count_col))
        total = count_query.scalar() or 0

        # Apply pagination to original query
        paginated_query = self.paginate_query(query)

        return paginated_query, total


class PaginationMeta(BaseModel):
    """
    Pagination metadata for API responses.

    This class contains metadata about a paginated response,
    including page numbers, total count, and navigation flags.
    """

    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 2,
                "page_size": 50,
                "total": 156,
                "pages": 4,
                "has_next": True,
                "has_prev": True,
            }
        }
    )


class PagedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response with items and metadata.

    This generic class provides a consistent response format for all
    paginated endpoints, supporting any item type.

    Example:
        ```python
        @router.get("/users", response_model=PagedResponse[UserResponse])
        async def list_users(pagination: PaginationParams = Depends()):
            users, total = get_users_with_count(pagination.skip, pagination.limit)
            return PagedResponse.create(users, total, pagination)
        ```
    """

    items: List[T] = Field(..., description="List of items for the current page")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": ["...list of items..."],
                "page": 2,
                "page_size": 50,
                "total": 156,
                "pages": 4,
                "has_next": True,
                "has_prev": True,
            }
        }
    )

    @classmethod
    def create(
        cls, items: List[T], total: int, pagination: PaginationParams
    ) -> "PagedResponse[T]":
        """
        Create a paged response from items and pagination parameters.

        Args:
            items: List of items for the current page
            total: Total number of items across all pages
            pagination: Pagination parameters

        Returns:
            Paged response
        """
        pages = ceil(total / pagination.page_size) if total > 0 else 1
        has_next = pagination.page < pages
        has_prev = pagination.page > 1

        return cls(
            items=items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev,
        )

    @classmethod
    def empty(cls, pagination: PaginationParams) -> "PagedResponse[T]":
        """
        Create an empty paged response.

        Args:
            pagination: Pagination parameters

        Returns:
            Empty paged response
        """
        return cls(
            items=[],
            page=pagination.page,
            page_size=pagination.page_size,
            total=0,
            pages=1,
            has_next=False,
            has_prev=False,
        )


# Dependency function for using pagination in routes
def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    """
    FastAPI dependency for pagination parameters.

    Example:
        ```python
        @router.get("/items")
        async def list_items(pagination: PaginationParams = Depends(get_pagination_params)):
            # Use pagination parameters
        ```

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        PaginationParams instance
    """
    return PaginationParams(page=page, page_size=page_size)


# Type alias for easier use in FastAPI dependencies
Pagination = Callable[[], PaginationParams]
