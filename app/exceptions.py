"""
BehaveDrift API — Custom Exceptions & FastAPI Exception Handlers
All errors return the standard ErrorResponse shape defined in ADR-004.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
import uuid


# ============================================================
# Custom Exception Classes
# ============================================================

class BehaveDriftError(Exception):
    """Base exception for all BehaveDrift errors."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"

    def __init__(self, message: str, details: list | None = None):
        self.message = message
        self.details = details or []
        super().__init__(message)


class AuthenticationError(BehaveDriftError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "authentication_required"


class InvalidCredentialsError(BehaveDriftError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "invalid_credentials"


class ForbiddenError(BehaveDriftError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"


class NotFoundError(BehaveDriftError):
    """Used for both missing resources AND tenant isolation violations."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class ConflictError(BehaveDriftError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"


class ValidationError(BehaveDriftError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "validation_error"


class BaselineInsufficientError(BehaveDriftError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "baseline_insufficient"


class RateLimitError(BehaveDriftError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "rate_limit_exceeded"


# ============================================================
# Error Response Builder
# ============================================================

def _build_error_response(
    request: Request,
    error_code: str,
    message: str,
    status_code: int,
    details: list | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    body = {
        "error": error_code,
        "message": message,
        "code": status_code,
        "request_id": request_id,
    }
    if details:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)


# ============================================================
# Exception Handlers
# ============================================================

async def behavedrift_exception_handler(
    request: Request, exc: BehaveDriftError
) -> JSONResponse:
    return _build_error_response(
        request, exc.error_code, exc.message, exc.status_code, exc.details
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle Pydantic validation errors from FastAPI."""
    from fastapi.exceptions import RequestValidationError
    if isinstance(exc, RequestValidationError):
        details = [
            {
                "field": ".".join(str(loc) for loc in err["loc"] if loc != "body"),
                "issue": err["type"],
                "value": err.get("input"),
            }
            for err in exc.errors()
        ]
        return _build_error_response(
            request,
            "validation_error",
            "Request body validation failed.",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            details,
        )
    raise exc


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic HTTP exceptions."""
    from fastapi import HTTPException
    if isinstance(exc, HTTPException):
        error_map = {
            401: ("authentication_required", "Authentication required."),
            403: ("forbidden", "You do not have permission to perform this action."),
            404: ("not_found", "The requested resource does not exist."),
            405: ("method_not_allowed", "Method not allowed."),
            429: ("rate_limit_exceeded", "Too many requests."),
        }
        code, msg = error_map.get(exc.status_code, ("http_error", str(exc.detail)))
        return _build_error_response(request, code, msg, exc.status_code)
    raise exc


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected server errors — never expose internals."""
    import logging
    request_id = getattr(request.state, "request_id", "unknown")
    logging.getLogger("behavedrift").error(
        "Unhandled exception",
        exc_info=exc,
        extra={"request_id": request_id},
    )
    return _build_error_response(
        request,
        "internal_error",
        f"An unexpected error occurred. Reference: {request_id}",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
