from asyncio import get_running_loop, run
from logging import LogRecord
from logging.handlers import BufferingHandler
from typing import Any, Callable

from buffering_async_logger import caches as logger_caches
from buffering_async_logger.send_logs_utils import C, K, send_logs_to_destination


class BufferingAsyncHandler(BufferingHandler):
    """Builds up a buffer of log records and sends them to a destination when full."""

    def __init__(
        self,
        capacity: int,
        url: str,
        get_log_aggregator_key_func: Callable[[LogRecord, C | None], K],
        get_request_headers_func: Callable[[dict[str, Any], K], dict[str, Any]],
        chunk_size: int,
        context: C | None = None,
    ):
        super().__init__(capacity)
        self.url = url
        self.get_log_aggregator_key_func = get_log_aggregator_key_func
        self.get_request_headers_func = get_request_headers_func
        self.chunk_size = chunk_size
        self.context = context

        logger_caches.BUFFERING_HANDLER = self

    def flush(self):
        """Send log records to a destination and empty the buffer."""
        if not len(self.buffer):
            return

        send_logs_args = [
            self.url,
            [x for x in self.buffer],
            self.format,
            self.get_log_aggregator_key_func,
            self.get_request_headers_func,
            self.chunk_size,
            self.context,
        ]

        self.buffer = []

        try:
            loop = get_running_loop()
        except RuntimeError:  # pragma: no cover
            loop = None

        if loop and loop.is_running():
            loop.create_task(send_logs_to_destination(*send_logs_args))
        else:  # pragma: no cover
            run(send_logs_to_destination(*send_logs_args))
