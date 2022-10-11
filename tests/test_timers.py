from asyncio import sleep
from unittest.mock import AsyncMock, MagicMock

import pytest

from buffering_async_logger.timers import start_flush_buffer_timer


@pytest.mark.asyncio
async def test_start_flush_buffer_timer():
    mock_caches_obj = MagicMock()
    await start_flush_buffer_timer(
        10,
        max_iterations=3,
        sleep_func=AsyncMock(),
        caches_obj=mock_caches_obj,
    )
    await sleep(0.000000001)

    assert mock_caches_obj.BUFFERING_HANDLER.flush.call_count == 4
