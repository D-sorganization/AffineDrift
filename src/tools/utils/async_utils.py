"""Utilities for asynchronous operations.

This module provides helper functions for managing asyncio event loops
and running synchronous code in separate threads.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)


async def run_async_task(coroutine: Coroutine[Any, Any, Any]) -> Any:
    """Run a coroutine and return the result.

    This function is a simple wrapper around await, primarily useful
    for standardizing async calls or adding logging/error handling.
    """
    return await coroutine


def run_sync_in_thread(func: Callable[..., Any], *args: Any) -> Awaitable[Any]:
    """Run a synchronous function in a separate thread to avoid blocking the event loop.

    Args:
        func: The synchronous function to run.
        *args: Arguments to pass to the function.

    Returns:
        A coroutine that resolves to the function's result.
    """
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, func, *args)
