from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    total: int
    limit: int
    offset: int


class ResponseMeta(BaseModel):
    """Metadata for API responses."""

    timestamp: int = Field(
        ..., description="Unix timestamp when the response was generated"
    )
    data_timestamp: Optional[int] = Field(
        None, description="Unix timestamp when the data was captured"
    )
    pagination: Optional[PaginationMeta] = None


class ResponseBase(BaseModel):
    """Base schema for all API responses."""

    success: bool = True
    meta: Optional[ResponseMeta] = None


class DataResponse(ResponseBase, Generic[T]):
    """Schema for responses that return a single data object."""

    data: T


class ListResponse(ResponseBase, Generic[T]):
    """Schema for responses that return a list of items."""

    data: List[T]


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    success: bool = False
    error: Dict[str, Any]
