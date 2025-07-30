"""Sorting utilities for API endpoints."""
from typing import Annotated, Any, Callable, Dict, List, Optional, Type

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Query as SQLAlchemyQuery


class SortingParams:
    """
    Sorting parameters for list endpoints.

    Provides convenient methods for applying sorting to SQL queries.
    """

    def __init__(
        self,
        sort: Optional[str] = Query(None, description="Field to sort by"),
        order: str = Query("asc", description="Sort order (asc or desc)"),
    ):
        """
        Initialize sorting parameters.

        Args:
            sort: Field to sort by
            order: Sort order (asc or desc)
        """
        self.sort = sort
        self.order = order.lower()

        if self.order not in ["asc", "desc"]:
            self.order = "asc"

    def apply_to_query(
        self,
        query: SQLAlchemyQuery,
        model: Type[DeclarativeMeta],
        allowed_fields: Optional[List[str]] = None,
        default_field: Optional[str] = None,
        field_map: Optional[Dict[str, str]] = None,
    ) -> SQLAlchemyQuery:
        """
        Apply sorting to a SQLAlchemy query.

        Args:
            query: SQLAlchemy query object
            model: SQLAlchemy model class
            allowed_fields: List of fields that can be used for sorting
            default_field: Default field to sort by if sort is not specified
            field_map: Mapping from API field names to model field names

        Returns:
            Sorted query

        Raises:
            HTTPException: If sort field is not allowed
        """
        # If sort is not specified, use default if provided
        sort_field = self.sort or default_field

        if not sort_field:
            return query

        # Map field name if necessary
        original_sort_field = sort_field
        if field_map and sort_field in field_map:
            sort_field = field_map[sort_field]

        # Validate sort field if allowed_fields is provided
        if allowed_fields and original_sort_field not in allowed_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort field: {original_sort_field}. Allowed fields: {', '.join(allowed_fields)}",
            )

        # Check if the field exists in the model
        if not hasattr(model, sort_field):
            if allowed_fields:
                # If allowed_fields were provided, this should not happen
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sort field '{sort_field}' does not exist in model",
                )
            # If no allowed_fields were provided, just return unsorted query
            return query

        # Apply sorting
        column = getattr(model, sort_field)
        sort_func = desc if self.order == "desc" else asc

        return query.order_by(sort_func(column))

    def get_sort_expression(
        self,
        model: Type[DeclarativeMeta],
        allowed_fields: Optional[List[str]] = None,
        default_field: Optional[str] = None,
        field_map: Optional[Dict[str, str]] = None,
    ) -> Optional[Any]:
        """
        Get the SQLAlchemy sort expression without applying it to a query.

        This is useful when you need the sort expression for more complex queries.

        Args:
            model: SQLAlchemy model
            allowed_fields: List of allowed fields
            default_field: Default field to sort by
            field_map: Field name mapping

        Returns:
            SQLAlchemy sort expression or None
        """
        # Get sort field, using default if none provided
        sort_field = self.sort or default_field
        if not sort_field:
            return None

        # Apply field mapping
        original_sort_field = sort_field
        if field_map and sort_field in field_map:
            sort_field = field_map[sort_field]

        # Validate allowed fields
        if allowed_fields and original_sort_field not in allowed_fields:
            return None

        # Check if field exists
        if not hasattr(model, sort_field):
            return None

        # Get sort direction
        sort_func = desc if self.order == "desc" else asc

        # Return sort expression
        return sort_func(getattr(model, sort_field))

    def apply_with_custom_sort(
        self,
        query: SQLAlchemyQuery,
        model: Type[DeclarativeMeta],
        custom_sort_fields: Dict[str, Callable[[SQLAlchemyQuery], SQLAlchemyQuery]],
        default_field: Optional[str] = None,
    ) -> SQLAlchemyQuery:
        """
        Apply sorting with support for custom sort implementations.

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model
            custom_sort_fields: Dict mapping field names to sort functions
            default_field: Default field to sort by

        Returns:
            Sorted query
        """
        sort_field = self.sort or default_field
        if not sort_field:
            return query

        # Check if this is a custom sort field
        if sort_field in custom_sort_fields:
            # Apply the custom sort function
            sort_func = custom_sort_fields[sort_field]
            direction = self.order
            return sort_func(query, direction)

        # Fall back to normal sorting
        return self.apply_to_query(query, model, allowed_fields=[sort_field])


def apply_sorting(
    query: SQLAlchemyQuery,
    model: Type[DeclarativeMeta],
    sort: Optional[str] = None,
    order: str = "asc",
    allowed_fields: Optional[List[str]] = None,
    field_map: Optional[Dict[str, str]] = None,
) -> SQLAlchemyQuery:
    """
    Apply sorting to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query
        model: SQLAlchemy model class
        sort: Field to sort by
        order: Sort order (asc or desc)
        allowed_fields: List of fields that can be used for sorting
        field_map: Mapping from API field names to model field names

    Returns:
        Sorted query
    """
    if not sort:
        return query

    # Validate sort field if allowed_fields is provided
    if allowed_fields and sort not in allowed_fields:
        return query

    # Map field name if necessary
    if field_map and sort in field_map:
        sort = field_map[sort]

    # Check if the field exists in the model
    if not hasattr(model, sort):
        return query

    # Apply sorting
    column = getattr(model, sort)
    direction = desc if order.lower() == "desc" else asc

    return query.order_by(direction(column))


def get_sorting_params(
    sort: Optional[str] = Query(None, description="Field to sort by"),
    order: str = Query("asc", description="Sort order (asc or desc)"),
) -> SortingParams:
    """
    FastAPI dependency for sorting parameters.

    Args:
        sort: Field to sort by
        order: Sort order (asc or desc)

    Returns:
        SortingParams instance
    """
    return SortingParams(sort=sort, order=order)


# Type alias for easier use in FastAPI dependencies
SortingDep = Annotated[SortingParams, Depends(get_sorting_params)]
