import logging

from src.logging_config import configure_logging
from src.tracing import bound_trace_id


class _CapturingHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_every_record_gets_trace_id() -> None:
    configure_logging()

    handler = _CapturingHandler()
    root = logging.getLogger()
    root.addHandler(handler)
    logger = logging.getLogger("test.trace")
    try:
        with bound_trace_id("z9"):
            logger.warning("inside")
        logger.warning("outside")
    finally:
        root.removeHandler(handler)

    inside, outside = handler.records[-2:]
    assert inside.trace_id == "z9"
    assert outside.trace_id == "-"
