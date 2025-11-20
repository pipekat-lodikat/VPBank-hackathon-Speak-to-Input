"""
Request ID Correlation Utility
Generates and manages request IDs for distributed tracing
"""

import uuid
from contextvars import ContextVar
from typing import Optional


# Context variable for storing current request ID
_request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


def generate_request_id() -> str:
    """
    Generate a new unique request ID.

    Returns:
        UUID string in format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    """
    return str(uuid.uuid4())


def set_request_id(request_id: str) -> None:
    """
    Set the request ID for the current context.

    Args:
        request_id: The request ID to set
    """
    _request_id_ctx.set(request_id)


def get_request_id() -> Optional[str]:
    """
    Get the request ID for the current context.

    Returns:
        The current request ID, or None if not set
    """
    return _request_id_ctx.get()


def get_or_create_request_id() -> str:
    """
    Get the current request ID, or create a new one if not set.

    Returns:
        The current or newly created request ID
    """
    request_id = _request_id_ctx.get()
    if request_id is None:
        request_id = generate_request_id()
        _request_id_ctx.set(request_id)
    return request_id


def clear_request_id() -> None:
    """Clear the request ID from the current context."""
    _request_id_ctx.set(None)
