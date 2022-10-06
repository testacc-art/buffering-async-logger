from itertools import islice
from logging import LogRecord
from typing import Any, Callable, TypeVar

import httpx


C = TypeVar("C")
K = TypeVar("K")


def _format_logs_for_destination(
    records: list[LogRecord], format_func: Callable[[Any], Any]
) -> str:
    """Format a batch of log records for sending to a destination."""
    return "".join([f"{format_func(record)}" for record in records])


def _get_aggregated_logs(
    records: list[LogRecord],
    get_log_aggregator_key_func: Callable[[LogRecord, C | None], K],
    context: C | None,
) -> dict[K, list[LogRecord]]:
    """Get log records grouped by aggregator key."""
    records_aggregated: dict[K, list[LogRecord]] = {}

    for record in records:
        key = get_log_aggregator_key_func(record, context)
        records_aggregated.setdefault(key, []).append(record)

    return records_aggregated


async def _send_logs_chunk_to_destination(
    url: str,
    key: K,
    records: list[LogRecord],
    format_func: Callable[[Any], Any],
    get_request_headers_func: Callable[[dict[str, Any], K], dict[str, Any]],
):
    """Send one chunk of log records to the destination."""
    payload = _format_logs_for_destination(records, format_func)
    headers = get_request_headers_func(
        {
            "Content-Type": "text/plain",
            "charset": "utf-8",
        },
        key,
    )

    async with httpx.AsyncClient() as client:
        await client.post(url, content=payload, headers=headers)


async def _send_logs_to_destination_for_aggregator_key(
    url: str,
    key: K,
    records: list[LogRecord],
    format_func: Callable[[Any], Any],
    get_request_headers_func: Callable[[dict[str, Any], K], dict[str, Any]],
    chunk_size: int,
):
    """Send all log records for the specified aggregator key to the destination."""
    records_iter = iter(records)

    # Thanks to: chunked() in the more-itertools library
    for chunk in iter(lambda: list(islice(records_iter, chunk_size)), []):
        await _send_logs_chunk_to_destination(
            url,
            key,
            chunk,
            format_func,
            get_request_headers_func,
        )


async def send_logs_to_destination(
    url: str,
    records: list[LogRecord],
    format_func: Callable[[Any], Any],
    get_log_aggregator_key_func: Callable[[LogRecord, C | None], K],
    get_request_headers_func: Callable[[dict[str, Any], K], dict[str, Any]],
    chunk_size: int,
    context: C | None,
):
    """Send the specified log records to the destination."""
    records_aggregated = _get_aggregated_logs(
        records, get_log_aggregator_key_func, context
    )

    for key, _records in records_aggregated.items():
        await _send_logs_to_destination_for_aggregator_key(
            url,
            key,
            _records,
            format_func,
            get_request_headers_func,
            chunk_size,
        )
