import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.errors.error_codes import ErrorCode
from app.errors.exceptions import BaseAPIException, DatabaseError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers with the FastAPI application."""

    @app.exception_handler(BaseAPIException)
    async def handle_base_api_exception(
        request: Request, exc: BaseAPIException
    ) -> JSONResponse:
        """Handle BaseAPIException instances."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI request validation errors."""
        errors = []
        for error in exc.errors():
            # Extract field information
            loc = ".".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "")
            type_error = error.get("type", "")
            errors.append(f"{loc}: {msg} ({type_error})")

        # Log the validation error details
        logger.warning(f"Request validation error: {errors}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": ErrorCode.VAL_INVALID_INPUT,
                    "message": "Request validation error",
                    "details": errors,
                }
            },
        )

    @app.exception_handler(PydanticValidationError)
    async def handle_pydantic_validation_error(
        request: Request, exc: PydanticValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            # Extract field information
            loc = ".".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "")
            type_error = error.get("type", "")
            errors.append(f"{loc}: {msg} ({type_error})")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": ErrorCode.VAL_INVALID_INPUT,
                    "message": "Data validation error",
                    "details": errors,
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_sqlalchemy_error(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle SQLAlchemy errors."""
        error_msg = str(exc)
        logger.error(f"Database error: {error_msg}")

        # Convert SQLAlchemy error to our custom DatabaseError
        db_error = DatabaseError(
            detail=f"A database error occurred: {type(exc).__name__}"
        )

        return JSONResponse(
            status_code=db_error.status_code,
            content={
                "error": {
                    "code": db_error.error_code,
                    "message": db_error.detail,
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_general_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle any unhandled exceptions."""
        error_msg = str(exc)
        logger.error(f"Unhandled exception: {error_msg}", exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": ErrorCode.INT_SERVER_ERROR,
                    "message": "An unexpected error occurred",
                }
            },
        )
