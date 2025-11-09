"""
Retry Utility with Exponential Backoff
Implements retry logic for transient failures
"""

import asyncio
from typing import TypeVar, Callable, Optional
from loguru import logger
import functools

T = TypeVar('T')


async def retry_with_exponential_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    retry_on_exceptions: tuple = (Exception,),
    **kwargs
) -> T:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        *args: Positional arguments to pass to func
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 30.0)
        backoff_factor: Multiplication factor for delay (default: 2.0)
        retry_on_exceptions: Tuple of exception types to retry on (default: all exceptions)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result from func

    Raises:
        Last exception if all retries are exhausted
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except retry_on_exceptions as e:
            last_exception = e

            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
                raise

    # This should never be reached, but included for type safety
    if last_exception:
        raise last_exception


def async_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    retry_on_exceptions: tuple = (Exception,)
):
    """
    Decorator for automatic retry with exponential backoff.

    Usage:
        @async_retry(max_retries=3, initial_delay=1.0)
        async def my_function():
            # Your code here
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_exponential_backoff(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                retry_on_exceptions=retry_on_exceptions,
                **kwargs
            )
        return wrapper
    return decorator
