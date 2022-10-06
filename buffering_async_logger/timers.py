from asyncio import create_task, sleep
from typing import Any, Awaitable, Callable

from buffering_async_logger import caches as logger_caches


async def _run_flush_buffer_timer(
    flush_buffer_every_x_secs: int,
    max_iterations: int | None = None,
    sleep_func: Callable[[int], Awaitable[None]] | None = None,
    caches_obj: Any | None = None,
):
    """Send logs to the destination at regular intervals."""
    _caches_obj = caches_obj if caches_obj is not None else logger_caches
    buffering_handler = _caches_obj.BUFFERING_HANDLER

    if buffering_handler is not None:
        buffering_handler.flush()
        _sleep_func = sleep_func if sleep_func is not None else sleep
        i = 0

        while max_iterations is None or i < max_iterations:
            await _sleep_func(flush_buffer_every_x_secs)
            buffering_handler.flush()

            if max_iterations is not None:
                i += 1


async def start_flush_buffer_timer(
    flush_buffer_every_x_secs: int,
    max_iterations: int | None = None,
    sleep_func: Callable[[int], Awaitable[None]] | None = None,
    caches_obj: Any | None = None,
):
    """Start a timer that will send logs to the destination at regular intervals."""
    _caches_obj = caches_obj if caches_obj is not None else logger_caches
    buffering_handler = _caches_obj.BUFFERING_HANDLER

    if flush_buffer_every_x_secs and buffering_handler is not None:
        create_task(
            _run_flush_buffer_timer(
                flush_buffer_every_x_secs,
                max_iterations=max_iterations,
                sleep_func=sleep_func,
                caches_obj=caches_obj,
            )
        )
