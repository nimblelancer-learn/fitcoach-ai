import logging
from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response

logger = logging.getLogger("app.request")

CallNext = Callable[[Request], Awaitable[Response]]


async def request_logging_middleware(
    request: Request,
    call_next: CallNext,
) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id

    started_at = perf_counter()

    response = await call_next(request)

    duration_ms = (perf_counter() - started_at) * 1000

    response.headers["X-Request-ID"] = request_id

    logger.info(
        (
            "request_completed request_id=%s method=%s "
            "path=%s status=%s duration_ms=%.2f"
        ),
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response