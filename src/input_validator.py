"""
Input Validation Utility
Validates and sanitizes user inputs to prevent injection attacks
"""

import re
from typing import Optional
from loguru import logger


def validate_field_name(field_name: str) -> bool:
    """
    Validate form field name.

    Args:
        field_name: The field name to validate

    Returns:
        True if valid, False otherwise
    """
    if not field_name:
        return False

    # Field name should be alphanumeric with hyphens, underscores, dots, or brackets
    # Examples: firstName, first_name, first-name, address[0], person.name
    if not re.match(r'^[a-zA-Z0-9_\-.\[\]]+$', field_name):
        logger.warning(f"Invalid field name format: {field_name}")
        return False

    # Prevent excessively long field names
    if len(field_name) > 255:
        logger.warning(f"Field name too long: {len(field_name)} characters")
        return False

    return True


def validate_field_value(value: str, max_length: int = 10000) -> bool:
    """
    Validate form field value.

    Args:
        value: The field value to validate
        max_length: Maximum allowed length (default: 10000)

    Returns:
        True if valid, False otherwise
    """
    if value is None:
        return False

    # Check length
    if len(str(value)) > max_length:
        logger.warning(f"Field value too long: {len(value)} characters (max: {max_length})")
        return False

    # Check for potential script injection
    dangerous_patterns = [
        r'<script[^>]*>',
        r'javascript:',
        r'on\w+\s*=',  # Event handlers like onclick=, onload=
        r'<iframe[^>]*>',
        r'eval\s*\(',
    ]

    value_str = str(value).lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, value_str, re.IGNORECASE):
            logger.warning(f"Potentially dangerous content detected in value: {pattern}")
            return False

    return True


def sanitize_user_message(message: str, max_length: int = 50000) -> Optional[str]:
    """
    Sanitize user message for LLM processing.

    Args:
        message: The user message to sanitize
        max_length: Maximum allowed length (default: 50000)

    Returns:
        Sanitized message or None if invalid
    """
    if not message:
        return None

    # Trim whitespace
    message = message.strip()

    # Check length
    if len(message) > max_length:
        logger.warning(f"User message too long: {len(message)} characters (max: {max_length})")
        return message[:max_length]

    return message


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.

    Args:
        session_id: The session ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not session_id:
        return False

    # Session ID should be alphanumeric with hyphens or underscores
    if not re.match(r'^[a-zA-Z0-9_\-]+$', session_id):
        logger.warning(f"Invalid session ID format: {session_id}")
        return False

    # Prevent excessively long session IDs
    if len(session_id) > 100:
        logger.warning(f"Session ID too long: {len(session_id)} characters")
        return False

    return True
