import logging

from src.tracing import get_trace_id

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] [trace_id=%(trace_id)s] %(message)s"

_DEFAULT_FACTORY = logging.getLogRecordFactory()
_configured = False


def _record_factory(*args: object, **kwargs: object) -> logging.LogRecord:
    record = _DEFAULT_FACTORY(*args, **kwargs)
    record.trace_id = get_trace_id() or "-"
    return record


def configure_logging(level: int = logging.INFO) -> None:
    global _configured
    if _configured:
        return
    _configured = True

    logging.setLogRecordFactory(_record_factory)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handler.set_name("trace-console")

    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(level)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
