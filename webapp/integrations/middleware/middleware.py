import uuid
from time import monotonic
from typing import Any, Awaitable, Callable

from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from webapp.integrations.metrics.metrics import (ERROR_COUNT, REQUEST_COUNT,
                                                 ROUTES_LATENCY)
from webapp.logger import correlation_id_ctx


class LogServerMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ('http', 'websocket'):
            await self.app(scope, receive, send)
            return

        for header, value in scope["headers"]:
            if header == b'x-correlation-id':
                correlation_id_ctx.set(value.decode())
                break
        else:
            correlation_id_ctx.set(uuid.uuid4().hex)

        await self.app(scope, receive, send)


async def prometheus_metrics(request: Request, call_next: Callable[..., Awaitable[Any]]) -> Awaitable[Any]:
    method = request.method
    path = request.url.path

    start_time = monotonic()
    response = await call_next(request)
    process_time = monotonic() - start_time
    if path in ['/favicon.ico', '/metrics']:
        return response
    REQUEST_COUNT.labels(method=method, endpoint=path, http_status=str(response.status_code)).inc()
    ROUTES_LATENCY.labels(method=method, endpoint=path).observe(process_time)

    if 400 <= response.status_code < 600:
        ERROR_COUNT.labels(method=method, endpoint=path, http_status=str(response.status_code)).inc()

    return response