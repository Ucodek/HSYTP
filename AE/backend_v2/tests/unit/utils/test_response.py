import json

from fastapi import status
from fastapi.responses import JSONResponse

from app.utils.response import (
    create_error_response,
    create_response,
    create_success_response,
    paginated_response,
)


def test_create_response():
    """Test create_response function."""
    # Test with only data
    response = create_response(data={"key": "value"})
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_200_OK
    assert response.body
    content = json.loads(response.body.decode())
    assert content["success"] is True
    assert content["data"]["key"] == "value"

    # Test with message
    response = create_response(message="Test message")
    assert response.status_code == status.HTTP_200_OK
    content = json.loads(response.body.decode())
    # Use direct dictionary access instead of string comparison
    assert content["message"] == "Test message"

    # Test with custom status code
    response = create_response(status_code=status.HTTP_201_CREATED)
    assert response.status_code == status.HTTP_201_CREATED

    # Test with headers
    response = create_response(headers={"X-Custom-Header": "value"})
    assert response.headers.get("X-Custom-Header") == "value"


def test_create_success_response():
    """Test create_success_response function."""
    # Test with data and default message
    response = create_success_response(data={"key": "value"})
    assert response.status_code == status.HTTP_200_OK
    content = json.loads(response.body.decode())
    assert content["success"] is True
    assert content["data"]["key"] == "value"
    assert content["message"] == "Operation successful"

    # Test with custom message
    response = create_success_response(data={"key": "value"}, message="Custom message")
    content = json.loads(response.body.decode())
    # Use direct dictionary access instead of string comparison
    assert content["message"] == "Custom message"

    # Test with custom status code
    response = create_success_response(
        data={"key": "value"}, status_code=status.HTTP_201_CREATED
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_create_error_response():
    """Test create_error_response function."""
    # Test with basic error
    response = create_error_response(code="TEST_ERROR", message="Test error message")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = json.loads(response.body.decode())
    assert content["error"]["code"] == "TEST_ERROR"
    assert content["error"]["message"] == "Test error message"

    # Test with details
    response = create_error_response(
        code="TEST_ERROR",
        message="Test error message",
        details=["Detail 1", "Detail 2"],
    )
    content = response.body.decode()
    assert '"details":' in content
    assert '"Detail 1"' in content
    assert '"Detail 2"' in content

    # Test with custom status code
    response = create_error_response(
        code="TEST_ERROR",
        message="Test error message",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_paginated_response():
    """Test paginated_response function."""
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    total = 10
    page = 2
    limit = 3

    response = paginated_response(items=items, total=total, page=page, limit=limit)

    assert response.status_code == status.HTTP_200_OK
    content = json.loads(response.body.decode())

    # Check data
    assert content["data"] == [{"id": 1}, {"id": 2}, {"id": 3}]

    # Check meta
    assert content["meta"]["page"] == 2
    assert content["meta"]["limit"] == 3
    assert content["meta"]["total"] == 10
    assert content["meta"]["pages"] == 4
    assert content["meta"]["has_next"] is True
    assert content["meta"]["has_prev"] is True

    # Test with first page
    response = paginated_response(items=items, total=total, page=1, limit=limit)
    content = json.loads(response.body.decode())
    assert content["meta"]["has_next"] is True
    assert content["meta"]["has_prev"] is False

    # Test with last page
    response = paginated_response(items=items, total=total, page=4, limit=limit)
    content = json.loads(response.body.decode())
    assert content["meta"]["has_next"] is False
    assert content["meta"]["has_prev"] is True

    # Test with custom status code
    response = paginated_response(
        items=items, total=total, status_code=status.HTTP_201_CREATED
    )
    assert response.status_code == status.HTTP_201_CREATED
