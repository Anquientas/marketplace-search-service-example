import httpx

from src.tracing import TRACE_ID_HEADER, get_trace_id


async def trace_request_hook(request: httpx.Request) -> None:
    trace_id = get_trace_id()
    if trace_id and TRACE_ID_HEADER not in request.headers:
        request.headers[TRACE_ID_HEADER] = trace_id
