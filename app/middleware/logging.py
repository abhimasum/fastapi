"""
Structured request/response logging middleware.
Produces JSON-compatible log entries compatible with Cloud Logging.
"""
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.access")

# Headers that should NEVER appear in logs
_SENSITIVE_HEADERS = frozenset(
    {"authorization", "cookie", "set-cookie", "x-api-key"}
)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        # Attach request_id so endpoints can log it
        request.state.request_id = request_id

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "http_request",
            extra={
                "json_fields": {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query),
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "client_ip": _get_client_ip(request),
                    "user_agent": request.headers.get("user-agent", ""),
                }
            },
        )

        # Propagate request ID to client for correlation
        response.headers["X-Request-ID"] = request_id
        return response


def _get_client_ip(request: Request) -> str:
    """Respect X-Forwarded-For set by Cloud Run / Load Balancer."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
