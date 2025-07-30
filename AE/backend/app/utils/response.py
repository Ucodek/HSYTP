import time
from typing import Any, Dict, List, Optional, TypeVar, Union

T = TypeVar("T")


def create_response(
    data: Any,
    data_timestamp: Optional[int] = None,
    pagination: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """Create a standardized API response according to PRD."""
    response = {
        "success": True,
        "data": data,
        "meta": {
            "timestamp": int(time.time()),
        },
    }

    if data_timestamp:
        response["meta"]["data_timestamp"] = data_timestamp

    if pagination:
        response["meta"]["pagination"] = pagination

    return response


def create_list_response(
    data: List[Any],
    total: int,
    limit: int,
    offset: int,
    data_timestamp: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a standardized list response with pagination according to PRD."""
    return create_response(
        data=data,
        data_timestamp=data_timestamp,
        pagination={"total": total, "limit": limit, "offset": offset},
    )


def create_error_response(
    code: str,
    message: str,
    details: Optional[Any] = None,
    status_code: int = 400,
) -> Dict[str, Union[bool, Dict[str, Any]]]:
    """Create a standardized error response according to PRD."""
    error_response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }

    if details:
        error_response["error"]["details"] = details

    return error_response
