"""Filtering utilities for API endpoints."""
from datetime import date, datetime
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar

from fastapi import Depends
from pydantic import BaseModel, create_model
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, and_, or_
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Query as SQLAlchemyQuery

T = TypeVar("T")
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)

# Type alias for filter functions
FilterFunction = Callable[[Any, Any], Any]


class FilterOperator(str, Enum):
    """Filter operators for comparison."""

    EQ = "eq"  # Equal
    NE = "ne"  # Not equal
    GT = "gt"  # Greater than
    GE = "ge"  # Greater than or equal
    LT = "lt"  # Less than
    LE = "le"  # Less than or equal
    LIKE = "like"  # LIKE (contains)
    ILIKE = "ilike"  # ILIKE (case-insensitive contains)
    IN = "in"  # IN (list of values)
    NOT_IN = "not_in"  # NOT IN (list of values)
    IS_NULL = "is_null"  # IS NULL
    IS_NOT_NULL = "is_not_null"  # IS NOT NULL


# Global operator mapping to avoid duplication
OPERATOR_MAPPING: Dict[FilterOperator, FilterFunction] = {
    FilterOperator.EQ: lambda col, val: col == val,
    FilterOperator.NE: lambda col, val: col != val,
    FilterOperator.GT: lambda col, val: col > val,
    FilterOperator.GE: lambda col, val: col >= val,
    FilterOperator.LT: lambda col, val: col < val,
    FilterOperator.LE: lambda col, val: col <= val,
    FilterOperator.LIKE: lambda col, val: col.like(f"%{val}%"),
    FilterOperator.ILIKE: lambda col, val: col.ilike(f"%{val}%"),
    FilterOperator.IN: lambda col, val: col.in_(val),
    FilterOperator.NOT_IN: lambda col, val: ~col.in_(val),
    FilterOperator.IS_NULL: lambda col, _: col.is_(None),
    FilterOperator.IS_NOT_NULL: lambda col, _: col.isnot(None),
}


class Filter(BaseModel):
    """
    Filter definition for applying to SQLAlchemy queries.

    Represents a single filter condition.
    """

    field: str
    operator: FilterOperator = FilterOperator.EQ
    value: Any = None

    def apply(
        self, query: SQLAlchemyQuery, model: Type[DeclarativeMeta]
    ) -> SQLAlchemyQuery:
        """
        Apply this filter to a SQLAlchemy query.

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model class

        Returns:
            Filtered query
        """
        if not hasattr(model, self.field):
            return query

        column = getattr(model, self.field)
        condition = get_filter_condition(column, self.operator, self.value)

        if condition is not None:
            return query.filter(condition)

        return query


class FilterParams(BaseModel, Generic[T]):
    """
    Base class for creating filter parameter models.

    This class can be extended to create specific filter parameter models
    for different entity types.

    Example:
        ```python
        class UserFilterParams(FilterParams):
            name: Optional[str] = None
            email: Optional[str] = None
            is_active: Optional[bool] = None

        @router.get("/users", response_model=PagedResponse[UserResponse])
        async def list_users(
            filters: UserFilterParams = Depends(),
            pagination: PaginationParams = Depends()
        ):
            # Use filters in your query
        ```
    """

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }

    def to_filter_list(self) -> List[Filter]:
        """
        Convert filter params to a list of Filter objects.

        Returns:
            List of Filter objects for each non-None parameter
        """
        filters = []
        for field_name, field_value in self.model_dump(exclude_none=True).items():
            if field_value is not None:
                filters.append(Filter(field=field_name, value=field_value))
        return filters


def apply_text_search(
    query: SQLAlchemyQuery,
    model: Type[DeclarativeMeta],
    search_text: str,
    search_fields: List[str],
) -> SQLAlchemyQuery:
    """
    Apply text search to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query
        model: SQLAlchemy model class
        search_text: Text to search for
        search_fields: Fields to search in

    Returns:
        Filtered query with text search applied
    """
    if not search_text or not search_fields:
        return query

    search_conditions = []

    for field_name in search_fields:
        if hasattr(model, field_name):
            column = getattr(model, field_name)
            # Only search in string columns
            if isinstance(column.type, String):
                search_conditions.append(column.ilike(f"%{search_text}%"))

    if search_conditions:
        return query.filter(or_(*search_conditions))

    return query


def apply_filters(
    query: SQLAlchemyQuery,
    model: Type[DeclarativeMeta],
    filters: List[Filter],
    combine_with_and: bool = True,
) -> SQLAlchemyQuery:
    """
    Apply multiple filters to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query
        model: SQLAlchemy model class
        filters: List of filters to apply
        combine_with_and: Whether to combine filters with AND (True) or OR (False)

    Returns:
        Filtered query
    """
    if not filters:
        return query

    # Apply all filters
    conditions = []

    for filter_obj in filters:
        if hasattr(model, filter_obj.field):
            column = getattr(model, filter_obj.field)
            condition = get_filter_condition(
                column, filter_obj.operator, filter_obj.value
            )
            if condition is not None:
                conditions.append(condition)

    if conditions:
        if combine_with_and:
            return query.filter(and_(*conditions))
        else:
            return query.filter(or_(*conditions))

    return query


def apply_filters_from_params(
    query: SQLAlchemyQuery,
    model: Type[DeclarativeMeta],
    filter_params: FilterParams,
    combine_with_and: bool = True,
) -> SQLAlchemyQuery:
    """
    Apply filters from FilterParams to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query
        model: SQLAlchemy model class
        filter_params: Filter parameters
        combine_with_and: Whether to combine filters with AND (True) or OR (False)

    Returns:
        Filtered query
    """
    filters = filter_params.to_filter_list()
    return apply_filters(query, model, filters, combine_with_and)


def get_filter_dependency(filter_class: Type[FilterParams]) -> Callable:
    """
    Create a FastAPI dependency for filter parameters.

    Args:
        filter_class: FilterParams subclass to use

    Returns:
        Dependency function that returns an instance of the filter class
    """

    def dependency() -> filter_class:
        return filter_class()

    return dependency


def get_type_mapping() -> Dict[Type, Type]:
    """
    Get mapping from SQLAlchemy column types to Python types.

    Returns:
        Dictionary mapping SQLAlchemy types to Python types
    """
    return {
        String: str,
        Boolean: bool,
        Integer: int,
        Float: float,
        # Fix: Use Python's date/datetime types instead of SQLAlchemy ones
        Date: date,
        DateTime: datetime,
    }


def create_filter_model(
    model_class: Type[DeclarativeMeta],
    name: str = None,
    include_fields: List[str] = None,
    exclude_fields: List[str] = None,
) -> Type[FilterParams]:
    """
    Create a FilterParams model from a SQLAlchemy model.

    Automatically generates filter parameters based on column types:
    - String columns: Optional[str]
    - Boolean columns: Optional[bool]
    - Numeric columns: Optional[float/int]
    - Date/time columns: Optional[date/datetime]
    - Enum columns: Optional[same enum type]

    Args:
        model_class: SQLAlchemy model class
        name: Name for the new model (default: model_class.__name__ + "FilterParams")
        include_fields: List of fields to include (if None, include all)
        exclude_fields: List of fields to exclude

    Returns:
        FilterParams subclass for the model
    """
    # Generate name if not provided
    if not name:
        name = f"{model_class.__name__}FilterParams"

    # Get all columns of the model
    field_definitions = {}
    exclude_fields = exclude_fields or []
    primary_key_columns = [
        column.key for column in model_class.__table__.columns if column.primary_key
    ]

    # Get type mapping
    type_mapping = get_type_mapping()

    for column_name, column in model_class.__table__.columns.items():
        # Skip excluded fields and primary keys
        if column_name in exclude_fields or column_name in primary_key_columns:
            continue

        # Include only specific fields if provided
        if include_fields and column_name not in include_fields:
            continue

        # Find the corresponding Python type
        python_type = None
        for sa_type, py_type in type_mapping.items():
            if isinstance(column.type, sa_type):
                python_type = py_type
                break

        # Handle Enum columns
        if hasattr(column.type, "enum_class"):
            python_type = column.type.enum_class

        # Add field if type was found
        if python_type:
            field_definitions[column_name] = (Optional[python_type], None)

    # Create a custom base class with the config we need
    class CustomFilterParams(FilterParams):
        model_config = {
            "arbitrary_types_allowed": True,
            "populate_by_name": True,
            "extra": "ignore",
        }

    # Create the model dynamically with our custom base class
    filter_model = create_model(name, __base__=CustomFilterParams, **field_definitions)

    return filter_model


class FilteredParams(Generic[T]):
    """
    Combined filter and pagination parameters.

    This class can be used to create a dependency that combines
    filter and pagination parameters.

    Example:
        ```python
        # Create filter params
        class UserFilterParams(FilterParams):
            name: Optional[str] = None
            email: Optional[str] = None

        # Create combined params
        UserParams = FilteredParams[UserFilterParams]

        @router.get("/users", response_model=PagedResponse[UserResponse])
        async def list_users(params: UserParams = Depends()):
            # Access params.filters and params.pagination
            users, total = get_users_with_filters(
                db,
                params.filters,
                params.pagination.page,
                params.pagination.page_size
            )
            return PagedResponse.create(users, total, params.pagination)
        ```
    """

    def __init__(self, filters: T, pagination: "PaginationParams"):
        self.filters = filters
        self.pagination = pagination

    @classmethod
    def create_dependency(cls, filter_class: Type[FilterParams[Any]]) -> Callable:
        """
        Create a FastAPI dependency that combines filter and pagination parameters.

        Args:
            filter_class: FilterParams class to use

        Returns:
            Dependency function that returns a FilteredParams instance
        """
        from app.api.common.pagination import PaginationParams, get_pagination_params

        def dependency(
            filters: Any = Depends(filter_class),
            pagination: PaginationParams = Depends(get_pagination_params),
        ) -> "FilteredParams[Any]":
            return cls(filters, pagination)

        return dependency


# Create a utility function to get condition from operator and value
def get_filter_condition(column: Any, operator: FilterOperator, value: Any) -> Any:
    """
    Get a SQLAlchemy filter condition based on operator and value.

    This centralized function handles all filter condition creation,
    ensuring consistent behavior across the filtering system.

    Args:
        column: SQLAlchemy column to filter on
        operator: Filter operator to apply
        value: Value to filter by

    Returns:
        SQLAlchemy filter condition
    """
    filter_func = OPERATOR_MAPPING.get(operator)
    if filter_func:
        return filter_func(column, value)
    return None
