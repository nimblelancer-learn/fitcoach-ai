import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base exception for expected application errors."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Any = None,
    ) -> None:
        super().__init__(message)

        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def create_error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)

    content = {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
        "request_id": request_id,
    }

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content),
        headers=headers,
    )


async def app_error_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    logger.warning(
        "application_error request_id=%s code=%s message=%s",
        getattr(request.state, "request_id", None),
        exc.code,
        exc.message,
    )

    return create_error_response(
        request,
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "request_validation_failed request_id=%s errors=%s",
        getattr(request.state, "request_id", None),
        exc.errors(),
    )

    return create_error_response(
        request,
        status_code=422,
        code="REQUEST_VALIDATION_ERROR",
        message="The request data is invalid.",
        details=exc.errors(),
    )


async def http_error_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    if isinstance(exc.detail, str):
        message = exc.detail
        details = None
    else:
        message = "The HTTP request failed."
        details = exc.detail

    return create_error_response(
        request,
        status_code=exc.status_code,
        code=f"HTTP_{exc.status_code}",
        message=message,
        details=details,
        headers=exc.headers,
    )


async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        "unexpected_error request_id=%s",
        request_id,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return create_error_response(
        request,
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler,
    )
    app.add_exception_handler(
        StarletteHTTPException,
        http_error_handler,
    )
    app.add_exception_handler(
        Exception,
        unexpected_error_handler,
    )