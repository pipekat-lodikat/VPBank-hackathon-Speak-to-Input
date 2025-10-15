"""
AWS Bedrock Configuration
Module để cấu hình và tạo kết nối với AWS Bedrock cho browser-use Agent
Uses browser-use's native ChatAnthropicBedrock class for compatibility
"""

import os
import boto3
from browser_use.llm import ChatAnthropicBedrock
from typing import Optional
import logging
from dotenv import load_dotenv
from .rate_limiter import bedrock_rate_limiter, with_retry_and_backoff

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class BedrockConfig:
    """Configuration class for AWS Bedrock with Singleton pattern"""

    _instance = None
    _client = None
    _credentials_validated = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BedrockConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, '_initialized'):
            # Use Claude Sonnet 4 (latest and most powerful)
            # us.anthropic.claude-sonnet-4-20250514-v1:0 - requires access permission
            self.model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
            self.region_name = os.getenv("AWS_REGION", "us-east-1")  # Most reliable region
            self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            self._initialized = True

    def create_bedrock_client(self) -> ChatAnthropicBedrock:
        """
        Tạo ChatAnthropicBedrock client với singleton pattern
        Uses browser-use's native class for full compatibility
        """
        # Return existing client if available
        if self._client is not None:
            logger.info(f"♻️ Reusing existing Bedrock client - Model: {self.model_id}")
            return self._client

        try:
            # Tạo ChatAnthropicBedrock client (browser-use native)
            bedrock_client = ChatAnthropicBedrock(
                model=self.model_id,
                aws_region=self.region_name,
                temperature=0.7,  # Higher temperature for more creative responses
                max_tokens=4096,  # Add explicit max_tokens for stability
            )

            # Cache the client
            self._client = bedrock_client
            logger.info(f"✅ ChatAnthropicBedrock client created - Model: {self.model_id}")
            logger.info(f"   Region: {self.region_name}")
            logger.info(f"   Max tokens: 4096")
            return bedrock_client

        except Exception as e:
            logger.error(f"❌ Failed to create Bedrock client: {str(e)}")
            logger.error(f"   Model: {self.model_id}")
            logger.error(f"   Region: {self.region_name}")
            raise

    def validate_credentials(self) -> bool:
        """
        Kiểm tra tính hợp lệ của AWS credentials (cached)
        """
        # Return cached result if already validated
        if self._credentials_validated:
            return True

        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )

            # Test credentials bằng cách gọi STS
            sts = session.client('sts')
            identity = sts.get_caller_identity()

            self._credentials_validated = True
            logger.info(f"✅ AWS Credentials valid. Account: {identity.get('Account')}")
            return True

        except Exception as e:
            logger.error(f"❌ Invalid AWS credentials: {str(e)}")
            return False

# Global singleton instance
_bedrock_config = None

def get_bedrock_llm(temperature: float = 0.3, max_tokens: int = 4096):
    """
    Convenience function để tạo ChatAnthropicBedrock instance với singleton pattern
    Uses browser-use's native Bedrock class for full compatibility.

    Args:
        temperature: Độ sáng tạo của model (0.0-1.0)
        max_tokens: Số token tối đa cho response (not used by ChatAnthropicBedrock)

    Returns:
        ChatAnthropicBedrock: browser-use native Bedrock client
    """
    global _bedrock_config

    if _bedrock_config is None:
        _bedrock_config = BedrockConfig()

    # Validate credentials trước khi tạo client (cached)
    if not _bedrock_config.validate_credentials():
        raise ValueError("❌ Invalid AWS credentials. Please check your environment variables.")

    bedrock_client = _bedrock_config.create_bedrock_client()

    # Override temperature if provided
    bedrock_client.temperature = temperature

    logger.info(f"✅ Returning ChatAnthropicBedrock client (Claude Sonnet 4, temperature={temperature})")

    return bedrock_client
