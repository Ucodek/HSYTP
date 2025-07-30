from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedParams(BaseModel):
    """Parameters for pagination."""

    page: int = 1
    limit: int = 20
    total: int = 0


class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""

    page: int
    limit: int
    total: int
    pages: int

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response model."""

    data: List[T]
    meta: PaginationMeta


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response model."""

    success: bool = True
    data: T
    message: Optional[str] = None


class ErrorDetail(BaseModel):
    """Error detail model."""

    code: str
    message: str
    details: Optional[List[str]] = None


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: ErrorDetail


def create_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = status.HTTP_200_OK,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Create a standard API response.

    Args:
        data: Response data
        message: Optional response message
        status_code: HTTP status code
        headers: Optional HTTP headers

    Returns:
        JSONResponse with standardized structure
    """
    content = {"success": True}

    if data is not None:
        content["data"] = data

    if message:
        content["message"] = message

    return JSONResponse(
        content=content,
        status_code=status_code,
        headers=headers,
    )


def create_success_response(
    data: Any,
    message: Optional[str] = "Operation successful",
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """
    Create a success response.

    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code

    Returns:
        JSONResponse with success structure
    """
    return create_response(data, message, status_code)


def create_error_response(
    code: str,
    message: str,
    details: Optional[List[str]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    """
    Create an error response.

    Args:
        code: Error code
        message: Error message
        details: Optional list of detailed error messages
        status_code: HTTP status code

    Returns:
        JSONResponse with error structure
    """
    content = {
        "error": {
            "code": code,
            "message": message,
        }
    }

    if details:
        content["error"]["details"] = details

    return JSONResponse(
        content=content,
        status_code=status_code,
    )


def paginated_response(
    items: List[Any],
    total: int,
    page: int = 1,
    limit: int = 20,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """
    Create a paginated response.

    Args:
        items: List of items for the current page
        total: Total number of items
        page: Current page number
        limit: Number of items per page
        status_code: HTTP status code

    Returns:
        JSONResponse with paginated structure
    """
    # Calculate total pages
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return JSONResponse(
        content={
            "success": True,
            "data": items,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1,
            },
        },
        status_code=status_code,
    )


def created_response(
    data: Any,
    message: str = "Resource created successfully",
) -> JSONResponse:
    """
    Create a response for resource creation.

    Args:
        data: Created resource data
        message: Success message

    Returns:
        JSONResponse with 201 Created status
    """
    return create_success_response(
        data=data,
        message=message,
        status_code=status.HTTP_201_CREATED,
    )


def no_content_response() -> JSONResponse:
    """
    Create a response with no content.

    Returns:
        JSONResponse with 204 No Content status
    """
    return JSONResponse(
        content=None,
        status_code=status.HTTP_204_NO_CONTENT,
    )
