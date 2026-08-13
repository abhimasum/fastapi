"""
Centralised exception hierarchy and FastAPI exception handlers.

Rules:
- Every exception maps to exactly one HTTP status code.
- Error responses NEVER expose stack traces, internal IDs, or DB details.
- All responses follow the same envelope: { "error": { "code", "message", "details" } }
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# ── Domain Exceptions ─────────────────────────────────────────────────────────

class AppError(Exception):
    """Base class for all application-level exceptions."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None, details: Any = None):
        self.message = message or self.__class__.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"
    message = "Resource not found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"
    message = "Resource already exists"


class CredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "INVALID_CREDENTIALS"
    message = "Invalid credentials"


class TokenExpiredError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "TOKEN_EXPIRED"
    message = "Access token has expired"


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "FORBIDDEN"
    message = "You do not have permission to perform this action"


class BadRequestError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "BAD_REQUEST"
    message = "Invalid request"


class RateLimitError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests. Please slow down."


# ── Response Builder ──────────────────────────────────────────────────────────

def _error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "error": {
            "code": error_code,
            "message": message,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


# ── Exception Handlers ────────────────────────────────────────────────────────

def _handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
    """Handle all domain-layer AppError subclasses."""
    logger.warning(
        "app_error",
        extra={"error_code": exc.error_code, "error_message": exc.message},
    )
    return _error_response(exc.status_code, exc.error_code, exc.message, exc.details)


def _handle_validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Transform Pydantic v2 validation errors into a clean, user-facing format.
    Groups errors by field so clients know exactly what to fix.
    """
    field_errors: list[dict[str, Any]] = []
    for err in exc.errors():
        loc = " → ".join(str(p) for p in err["loc"] if p != "body")
        field_errors.append({
            "field": loc or "body",
            "message": err["msg"],
            "type": err["type"],
        })

    logger.info("validation_error", extra={"errors": field_errors})
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "VALIDATION_ERROR",
        "Request validation failed",
        field_errors,
    )


def _handle_http_exception(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Catch any raw HTTPException and wrap in our error envelope."""
    return _error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))


def _handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    """
    Last-resort handler — log the real error internally, return generic 500.
    NEVER expose exc details to the client.
    """
    # Log with full traceback for debugging
    import traceback
    import sys
    
    tb_str = traceback.format_exc()
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"UNHANDLED EXCEPTION: {type(exc).__name__}: {str(exc)}", file=sys.stderr)
    print(tb_str, file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)
    
    # Use simple logging without exception context to avoid LogRecord issues
    logger.error("Unhandled exception occurred")
    
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "INTERNAL_ERROR",
        "An internal error occurred. Please try again later.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all handlers on the FastAPI application instance."""
    app.add_exception_handler(AppError, _handle_app_error)                         # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _handle_validation_error)     # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)       # type: ignore[arg-type]
    app.add_exception_handler(Exception, _handle_unhandled_exception)               # type: ignore[arg-type]
