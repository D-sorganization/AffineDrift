import asyncio
from src.tools.utils.async_utils import run_sync_in_thread, run_async_task


def sync_function(x):
    return x * 2


async def async_function(x):
    return x + 1


def test_run_sync_in_thread():
    async def run_test():
        result = await run_sync_in_thread(sync_function, 10)
        assert result == 20

    asyncio.run(run_test())


def test_run_async_task():
    async def run_test():
        result = await run_async_task(async_function(5))
        assert result == 6

    asyncio.run(run_test())
