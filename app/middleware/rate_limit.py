"""
In-memory sliding-window rate limiter.

For multi-instance deployments (multiple Cloud Run instances) replace the
in-memory store with a Redis or Memorystore backend.

Excluded paths: /health, /docs, /redoc, /openapi.json
"""
import time
from collections import deque
from threading import Lock
from typing import Callable

from fastapi import Request, Response

from app.core.config import get_settings
from app.core.exceptions import RateLimitError

settings = get_settings()

# ip_address → deque of request timestamps within the window
_store: dict[str, deque] = {}
_lock = Lock()

_EXCLUDED_PATHS = frozenset({"/health", "/docs", "/redoc", "/openapi.json"})


class RateLimitMiddleware:
    """ASGI middleware (not Starlette BaseHTTPMiddleware for lower overhead)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            if request.url.path not in _EXCLUDED_PATHS:
                self._check_rate_limit(request)
        await self.app(scope, receive, send)

    def _check_rate_limit(self, request: Request) -> None:
        ip = _get_ip(request)
        now = time.monotonic()
        window = settings.rate_limit_window_seconds
        limit = settings.rate_limit_requests

        with _lock:
            if ip not in _store:
                _store[ip] = deque()

            dq = _store[ip]

            # Evict timestamps outside the current window
            while dq and dq[0] < now - window:
                dq.popleft()

            if len(dq) >= limit:
                raise RateLimitError(
                    f"Rate limit exceeded: {limit} requests per {window}s"
                )

            dq.append(now)


def _get_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "0.0.0.0"
