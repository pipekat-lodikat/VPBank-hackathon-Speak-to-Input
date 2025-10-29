"""
Configuration file for VPBank Multi-Agent System
Centralized configuration management
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)


# ==========================================
# AWS Configuration
# ==========================================
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Bedrock Model ID - use inference profile ARN for on-demand access
# Option 1: Cross-region inference profile (recommended)
# Option 2: Direct model ID (requires provisioned throughput)
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-3-5-sonnet-20241022-v2:0"  # Standard model ID
)


# ==========================================
# OpenAI Configuration
# ==========================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ==========================================
# VPBank Forms URLs
# ==========================================
FORM_BASE_URL = os.getenv("FORM_BASE_URL", "http://localhost:5173/vpbank-forms")

FORM_URLS = {
    "loan": f"{FORM_BASE_URL}/use-case-1-loan-origination/index.html",
    "crm": f"{FORM_BASE_URL}/use-case-2-crm-update/index.html",
    "hr": f"{FORM_BASE_URL}/use-case-3-hr-workflow/index.html",
    "compliance": f"{FORM_BASE_URL}/use-case-4-compliance-reporting/index.html",
    "operations": f"{FORM_BASE_URL}/use-case-5-operations-validation/index.html",
}


# ==========================================
# Server Configuration
# ==========================================
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "7860"))


# ==========================================
# Task Queue Configuration
# ==========================================
TASK_QUEUE_MAX_SIZE = int(os.getenv("TASK_QUEUE_MAX_SIZE", "100"))
TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", "300"))  # 5 minutes


# ==========================================
# Logging Configuration
# ==========================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PIPECAT_LOG_LEVEL = os.getenv("PIPECAT_LOG_LEVEL", "INFO")


# ==========================================
# LangSmith Configuration (Optional)
# ==========================================
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "vpbank-voice-agent")


# ==========================================
# Validation
# ==========================================
def validate_config():
    """
    Validate that all required configuration is present
    
    Raises:
        ValueError: If required configuration is missing
    """
    required_vars = {
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "OPENAI_API_KEY": OPENAI_API_KEY,
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please check your .env file or environment variables."
        )


def get_form_url(form_type: str) -> str:
    """
    Get form URL by type
    
    Args:
        form_type: One of 'loan', 'crm', 'hr', 'compliance', 'operations'
        
    Returns:
        Full URL to the form
        
    Raises:
        ValueError: If form_type is invalid
    """
    if form_type not in FORM_URLS:
        raise ValueError(
            f"Invalid form type: {form_type}. "
            f"Must be one of: {', '.join(FORM_URLS.keys())}"
        )
    
    return FORM_URLS[form_type]


# Auto-validate on import (optional - comment out if needed)
# validate_config()

