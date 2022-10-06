from asyncio import sleep
from unittest.mock import MagicMock, patch

import pytest

from buffering_async_logger.handlers import BufferingAsyncHandler


@pytest.mark.asyncio
@patch("buffering_async_logger.handlers.send_logs_to_destination")
async def test_buffering_async_handler(mock_send_logs_to_destination):
    url = "https://foo.logshmog.com/v1/logs/a1b2c3"
    get_log_aggregator_key_func = MagicMock()
    get_request_headers_func = MagicMock()
    chunk_size = 99
    context = MagicMock()

    handler = BufferingAsyncHandler(
        42,
        url,
        get_log_aggregator_key_func,
        get_request_headers_func,
        chunk_size,
        context=context,
    )
    handler.buffer.append("foo123")
    handler.flush()
    await sleep(0.000000001)

    mock_send_logs_to_destination.assert_called_with(
        url,
        ["foo123"],
        handler.format,
        get_log_aggregator_key_func,
        get_request_headers_func,
        chunk_size,
        context,
    )


@patch("buffering_async_logger.handlers.send_logs_to_destination")
def test_buffering_async_handler_buffer_empty(mock_send_logs_to_destination):
    get_log_aggregator_key_func = MagicMock()
    get_request_headers_func = MagicMock()
    chunk_size = 99
    context = MagicMock()

    handler = BufferingAsyncHandler(
        42,
        "https://foo.logshmog.com/v1/logs/a1b2c3",
        get_log_aggregator_key_func,
        get_request_headers_func,
        chunk_size,
        context=context,
    )
    handler.flush()

    mock_send_logs_to_destination.assert_not_called()
