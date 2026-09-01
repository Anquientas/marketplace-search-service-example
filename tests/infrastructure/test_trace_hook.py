import httpx

from src.infrastructure.http.trace_hook import trace_request_hook
from src.tracing import TRACE_ID_HEADER, bound_trace_id


async def test_hook_sets_header_from_context() -> None:
    request = httpx.Request("GET", "http://ad/internal/users/1")

    with bound_trace_id("h1"):
        await trace_request_hook(request)

    assert request.headers[TRACE_ID_HEADER] == "h1"


async def test_hook_noop_without_context() -> None:
    request = httpx.Request("GET", "http://ad/internal/users/1")

    await trace_request_hook(request)

    assert TRACE_ID_HEADER not in request.headers


async def test_hook_does_not_overwrite_existing_header() -> None:
    request = httpx.Request(
        "GET", "http://ad/internal/users/1", headers={TRACE_ID_HEADER: "explicit"}
    )

    with bound_trace_id("h1"):
        await trace_request_hook(request)

    assert request.headers[TRACE_ID_HEADER] == "explicit"
