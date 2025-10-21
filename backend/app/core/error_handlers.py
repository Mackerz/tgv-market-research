"""Centralized error handling middleware and exception handlers"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback
from typing import Union

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions (400s, 500s, etc.)
    Provides consistent error response format
    """
    # Log the error
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "status_code": exc.status_code,
                "message": exc.detail,
                "path": request.url.path
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation errors (422 Unprocessable Entity)
    Provides detailed validation error information
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={"errors": errors}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "status_code": 422,
                "message": "Request validation failed",
                "path": request.url.path,
                "details": errors
            }
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle database errors (SQLAlchemy exceptions)
    Provides safe error messages without exposing sensitive database details
    """
    # Log the full error for debugging
    logger.error(
        f"Database error on {request.method} {request.url.path}: {str(exc)}",
        extra={"traceback": traceback.format_exc()}
    )

    # Check for specific error types
    if isinstance(exc, IntegrityError):
        # Constraint violation (unique, foreign key, etc.)
        error_message = "Database constraint violation. The operation conflicts with existing data."
        status_code = status.HTTP_409_CONFLICT
    else:
        # Generic database error
        error_message = "A database error occurred. Please try again later."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": "database_error",
                "status_code": status_code,
                "message": error_message,
                "path": request.url.path
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unhandled exceptions
    Logs the full error and returns a safe error message to the client
    """
    # Log the full error with traceback
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )

    # Return a generic error message (don't expose internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_error",
                "status_code": 500,
                "message": "An unexpected error occurred. Please try again later.",
                "path": request.url.path
            }
        }
    )


def register_error_handlers(app):
    """
    Register all error handlers with the FastAPI application

    Usage:
        from app.core.error_handlers import register_error_handlers
        register_error_handlers(app)
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("✅ Error handlers registered successfully")
