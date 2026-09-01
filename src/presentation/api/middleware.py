from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.tracing import (
    TRACE_ID_HEADER,
    generate_trace_id,
    reset_trace_id,
    set_trace_id,
)

_HEADER_KEY = TRACE_ID_HEADER.lower().encode("latin-1")


class TraceIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        incoming = dict(scope["headers"]).get(_HEADER_KEY)
        trace_id = incoming.decode("latin-1").strip() if incoming else ""
        trace_id = trace_id or generate_trace_id()
        token = set_trace_id(trace_id)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((_HEADER_KEY, trace_id.encode("latin-1")))
                message["headers"] = headers
            await send(message)

        try:
            await self._app(scope, receive, send_wrapper)
        finally:
            reset_trace_id(token)
