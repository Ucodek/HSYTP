"""Unified query parameter handling for API endpoints."""
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar

from fastapi import Depends
from sqlalchemy.orm import Query as SQLAlchemyQuery

from app.api.common.filtering import FilterParams, apply_filters_from_params
from app.api.common.pagination import PaginationParams, get_pagination_params
from app.api.common.sorting import SortingParams, get_sorting_params

T = TypeVar("T")
ModelType = TypeVar("ModelType")


class QueryParams(Generic[T]):
    """
    Combined query parameters for filtering, pagination, and sorting.

    This provides a unified interface for handling common query operations.
    """

    def __init__(
        self,
        filters: T,
        pagination: PaginationParams,
        sorting: Optional[SortingParams] = None,
    ):
        self.filters = filters
        self.pagination = pagination
        self.sorting = sorting

    def apply_to_query(
        self,
        query: SQLAlchemyQuery,
        model: Type[ModelType],
        sort_allowed_fields: Optional[List[str]] = None,
        sort_field_map: Optional[Dict[str, str]] = None,
    ) -> tuple[SQLAlchemyQuery, int]:
        """
        Apply all query parameters to a SQLAlchemy query.

        Args:
            query: SQLAlchemy query object
            model: SQLAlchemy model class
            sort_allowed_fields: List of fields allowed for sorting
            sort_field_map: Mapping from API field names to model field names

        Returns:
            Tuple of (paginated query, total count)
        """
        # Apply filters
        filtered_query = apply_filters_from_params(query, model, self.filters)

        # Get total count
        total = filtered_query.count()

        # Apply sorting if provided
        if self.sorting:
            filtered_query = self.sorting.apply_to_query(
                filtered_query,
                model,
                allowed_fields=sort_allowed_fields,
                field_map=sort_field_map,
            )

        # Apply pagination and return
        paginated_query = self.pagination.paginate_query(filtered_query)

        return paginated_query, total

    def apply_all_params(
        self,
        query: SQLAlchemyQuery,
        model: Type[ModelType],
        sort_allowed_fields: Optional[List[str]] = None,
        sort_field_map: Optional[Dict[str, str]] = None,
        default_sort_field: Optional[str] = None,
    ) -> List[Any]:
        """
        Apply all query parameters and return the results.

        This is a convenience method that:
        1. Applies filters
        2. Applies sorting
        3. Gets the total count
        4. Applies pagination
        5. Executes the query

        Args:
            query: SQLAlchemy query
            model: Model class
            sort_allowed_fields: List of allowed sort fields
            sort_field_map: Map of API field names to model field names
            default_sort_field: Default field to sort by if none provided

        Returns:
            Tuple of (list of results, total count)
        """
        # Apply filters first
        filtered_query = apply_filters_from_params(query, model, self.filters)

        # Get total count
        total = filtered_query.count()

        # Apply sorting with default if provided
        if self.sorting:
            filtered_query = self.sorting.apply_to_query(
                filtered_query,
                model,
                allowed_fields=sort_allowed_fields,
                field_map=sort_field_map,
                default_field=default_sort_field,
            )
        elif default_sort_field and hasattr(model, default_sort_field):
            # Apply default sorting if no sort parameter but default is provided
            filtered_query = filtered_query.order_by(getattr(model, default_sort_field))

        # Apply pagination
        paginated_query = self.pagination.paginate_query(filtered_query)

        # Execute query and return results with count
        results = paginated_query.all()
        return results, total

    @classmethod
    def create_dependency(
        cls, filter_class: Type[FilterParams[Any]], include_sorting: bool = True
    ) -> Callable:
        """
        Create a dependency that combines filters, pagination, and optional sorting.

        Args:
            filter_class: FilterParams class to use
            include_sorting: Whether to include sorting parameters

        Returns:
            Dependency function that returns a QueryParams instance
        """
        if include_sorting:

            def dependency(
                filters: Any = Depends(filter_class),
                pagination: PaginationParams = Depends(get_pagination_params),
                sorting: SortingParams = Depends(get_sorting_params),
            ) -> "QueryParams[Any]":
                return cls(filters, pagination, sorting)

        else:

            def dependency(
                filters: Any = Depends(filter_class),
                pagination: PaginationParams = Depends(get_pagination_params),
            ) -> "QueryParams[Any]":
                return cls(filters, pagination)

        return dependency
