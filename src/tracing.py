import contextvars
import uuid
from collections.abc import Iterator
from contextlib import contextmanager

TRACE_ID_HEADER = "X-Trace-Id"

_trace_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "trace_id", default=None
)


def get_trace_id() -> str | None:
    return _trace_id.get()


def generate_trace_id() -> str:
    return str(uuid.uuid4())


def set_trace_id(value: str | None) -> contextvars.Token:
    return _trace_id.set(value)


def reset_trace_id(token: contextvars.Token) -> None:
    _trace_id.reset(token)


@contextmanager
def bound_trace_id(value: str | None) -> Iterator[str | None]:
    """Bind ``value`` exactly (may be ``None``); reset on exit. Never generates."""
    token = _trace_id.set(value)
    try:
        yield value
    finally:
        _trace_id.reset(token)
