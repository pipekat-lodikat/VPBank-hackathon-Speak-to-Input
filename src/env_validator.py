"""
Environment Variable Validation Utility
Validates required environment variables at service startup
"""

import os
import sys
from typing import List, Dict
from loguru import logger


def validate_required_env_vars(required_vars: List[str], service_name: str = "Service") -> Dict[str, str]:
    """
    Validate that all required environment variables are set.

    Args:
        required_vars: List of required environment variable names
        service_name: Name of the service for error messages

    Returns:
        Dictionary of validated environment variables

    Raises:
        SystemExit: If any required variables are missing
    """
    missing = []
    validated = {}

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            validated[var] = value

    if missing:
        logger.error(f"❌ {service_name} - Missing required environment variables:")
        for var in missing:
            logger.error(f"   - {var}")
        logger.error("\n💡 Please check your .env file or environment configuration")
        logger.error("   See .env.example for required variables\n")
        sys.exit(1)

    logger.info(f"✅ {service_name} - All required environment variables validated")
    return validated


def validate_voice_bot_env() -> Dict[str, str]:
    """Validate Voice Bot service environment variables."""
    required = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "BEDROCK_MODEL_ID",
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY",
        "ELEVENLABS_VOICE_ID",
        "BROWSER_SERVICE_URL",
        "COGNITO_USER_POOL_ID",
        "COGNITO_CLIENT_ID",
        "DYNAMODB_TABLE_NAME",
    ]

    return validate_required_env_vars(required, "Voice Bot Service")


def validate_browser_service_env() -> Dict[str, str]:
    """Validate Browser Service environment variables."""
    required = [
        "OPENAI_API_KEY",
    ]

    return validate_required_env_vars(required, "Browser Agent Service")


def warn_optional_env_vars(optional_vars: List[str], service_name: str = "Service") -> None:
    """
    Warn about optional environment variables that are not set.

    Args:
        optional_vars: List of optional environment variable names
        service_name: Name of the service for warning messages
    """
    missing = [var for var in optional_vars if not os.getenv(var)]

    if missing:
        logger.warning(f"⚠️  {service_name} - Optional environment variables not set:")
        for var in missing:
            logger.warning(f"   - {var}")
        logger.warning("   Service will use default values\n")
