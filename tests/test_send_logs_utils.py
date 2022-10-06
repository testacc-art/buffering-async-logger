import json
from logging import LogRecord
from typing import Any, NamedTuple
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from buffering_async_logger.send_logs_utils import send_logs_to_destination


class LogAggregatorContextTest(NamedTuple):
    foo: str
    moo: str


class LogAggregatorKeyTest(NamedTuple):
    woo: str
    hoo: str


def get_log_aggregator_context_test_func() -> LogAggregatorContextTest:
    return LogAggregatorContextTest(
        foo="foo123",
        moo="moo123",
    )


def get_log_aggregator_key_for_record_test_func(
    record: LogRecord, context: LogAggregatorContextTest | None
) -> LogAggregatorKeyTest:
    if context is None:  # pragma: no cover
        raise ValueError(
            "context is required by get_log_aggregator_key_for_record_test_func"
        )

    return LogAggregatorKeyTest(
        woo=context.foo,
        hoo=f"{context.moo}/{record.levelname}",
    )


def get_request_headers_test_func(
    headers: dict[str, Any], key: LogAggregatorKeyTest
) -> dict[str, Any]:
    new_headers = headers.copy()

    new_headers["X-Logshmog-Woo"] = key.woo
    new_headers["X-Logshmog-Hoo"] = key.hoo

    return new_headers


def log_formatter_test_func(record: Any) -> Any:
    _record = {
        "timestamp": record.extra["time"],
        "level": record.extra["level"],
        "logger": record.extra["name"],
        "message": record.extra["message"],
    }

    if record.extra.get("woo"):
        _record["woo"] = record.extra["woo"]
    if record.extra.get("hoo"):
        _record["hoo"] = record.extra["hoo"]

    return f"{json.dumps(_record)}\n"


@pytest.mark.asyncio
@patch("buffering_async_logger.send_logs_utils.httpx")
async def test_send_logs_to_destination(mock_httpx):
    mock_resp = MagicMock()
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp
    mock_client_context = MagicMock()
    mock_client_context.__aenter__.return_value = mock_client
    mock_httpx.AsyncClient.return_value = mock_client_context

    record1 = MagicMock()
    record1.levelname = "INFO"
    record1.extra = {
        "time": "2020-01-02 03:04:05.678+0000",
        "level": "INFO",
        "name": "foologger",
        "message": "do foo",
        "woo": "foo123",
        "hoo": "moo123/INFO",
    }

    record2 = MagicMock()
    record2.levelname = "WARNING"
    record2.extra = {
        "time": "2020-01-02 03:04:06.678+0000",
        "level": "WARNING",
        "name": "foologger",
        "message": "oh my foo",
        "woo": "foo123",
        "hoo": "moo123/WARNING",
    }

    record3 = MagicMock()
    record3.levelname = "INFO"
    record3.extra = {
        "time": "2020-01-02 03:04:07.678+0000",
        "level": "INFO",
        "name": "foologger",
        "message": "do more foo",
        "woo": "foo123",
        "hoo": "moo123/INFO",
    }

    record4 = MagicMock()
    record4.levelname = "INFO"
    record4.extra = {
        "time": "2020-01-02 03:04:08.678+0000",
        "level": "INFO",
        "name": "foologger",
        "message": "still more foo",
        "woo": "foo123",
        "hoo": "moo123/INFO",
    }

    records = [record1, record2, record3, record4]
    url = "https://foo.logshmog.com/v1/logs/a1b2c3"
    _headers = {
        "Content-Type": "text/plain",
        "charset": "utf-8",
        "X-Logshmog-Woo": "foo123",
    }

    await send_logs_to_destination(
        url,
        records,
        log_formatter_test_func,
        get_log_aggregator_key_for_record_test_func,
        get_request_headers_test_func,
        2,
        get_log_aggregator_context_test_func(),
    )

    mock_client.post.assert_has_calls(
        [
            call(
                url,
                content="".join(
                    [
                        f"{json.dumps(_content)}\n"
                        for _content in [
                            {
                                "timestamp": "2020-01-02 03:04:05.678+0000",
                                "level": "INFO",
                                "logger": "foologger",
                                "message": "do foo",
                                "woo": "foo123",
                                "hoo": "moo123/INFO",
                            },
                            {
                                "timestamp": "2020-01-02 03:04:07.678+0000",
                                "level": "INFO",
                                "logger": "foologger",
                                "message": "do more foo",
                                "woo": "foo123",
                                "hoo": "moo123/INFO",
                            },
                        ]
                    ]
                ),
                headers=_headers | {"X-Logshmog-Hoo": "moo123/INFO"},
            ),
            call(
                url,
                content="".join(
                    [
                        f"{json.dumps(_content)}\n"
                        for _content in [
                            {
                                "timestamp": "2020-01-02 03:04:08.678+0000",
                                "level": "INFO",
                                "logger": "foologger",
                                "message": "still more foo",
                                "woo": "foo123",
                                "hoo": "moo123/INFO",
                            },
                        ]
                    ]
                ),
                headers=_headers | {"X-Logshmog-Hoo": "moo123/INFO"},
            ),
            call(
                url,
                content="".join(
                    [
                        f"{json.dumps(_content)}\n"
                        for _content in [
                            {
                                "timestamp": "2020-01-02 03:04:06.678+0000",
                                "level": "WARNING",
                                "logger": "foologger",
                                "message": "oh my foo",
                                "woo": "foo123",
                                "hoo": "moo123/WARNING",
                            },
                        ]
                    ]
                ),
                headers=_headers | {"X-Logshmog-Hoo": "moo123/WARNING"},
            ),
        ],
    )
