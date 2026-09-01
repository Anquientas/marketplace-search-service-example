import uuid

from httpx import AsyncClient

from src.tracing import TRACE_ID_HEADER


def _is_uuid4(value: str) -> bool:
    try:
        return uuid.UUID(value).version == 4
    except ValueError:
        return False


async def test_generates_trace_id_when_header_absent(client: AsyncClient) -> None:
    resp = await client.get("/search")

    assert resp.status_code == 200
    assert _is_uuid4(resp.headers[TRACE_ID_HEADER])


async def test_echoes_incoming_trace_id(client: AsyncClient) -> None:
    resp = await client.get("/search", headers={TRACE_ID_HEADER: "fixed-123"})

    assert resp.status_code == 200
    assert resp.headers[TRACE_ID_HEADER] == "fixed-123"
