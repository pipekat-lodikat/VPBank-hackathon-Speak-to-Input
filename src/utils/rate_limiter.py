"""
Rate Limiter cho AWS Bedrock
Xử lý throttling và rate limiting
"""

import time
import logging
from functools import wraps
from typing import Any, Callable
from botocore.exceptions import ClientError
import random

logger = logging.getLogger(__name__)

class BedrockRateLimiter:
    """Rate limiter cho AWS Bedrock requests"""

    def __init__(self,
                 requests_per_minute: int = 10,
                 max_retries: int = 3,
                 base_delay: float = 1.0):
        self.requests_per_minute = requests_per_minute
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.last_request_time = 0
        self.request_count = 0
        self.minute_start = time.time()

    def wait_if_needed(self):
        """Chờ nếu cần để tránh rate limit"""
        current_time = time.time()

        # Reset counter mỗi phút
        if current_time - self.minute_start >= 60:
            self.request_count = 0
            self.minute_start = current_time

        # Kiểm tra rate limit
        if self.request_count >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.minute_start)
            if wait_time > 0:
                logger.info(f"⏳ Rate limit reached. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
                self.request_count = 0
                self.minute_start = time.time()

        # Minimum delay giữa các requests
        time_since_last = current_time - self.last_request_time
        min_delay = 60 / self.requests_per_minute  # Phân bố đều trong phút

        if time_since_last < min_delay:
            wait_time = min_delay - time_since_last
            time.sleep(wait_time)

        self.last_request_time = time.time()
        self.request_count += 1

def with_retry_and_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator để retry với exponential backoff
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    last_exception = e

                    if error_code in ['ThrottlingException', 'TooManyRequestsException']:
                        if attempt < max_retries:
                            # Exponential backoff với jitter
                            delay = base_delay * (3 ** attempt) + random.uniform(1, 5)
                            logger.warning(f"⚠️ AWS Bedrock Throttling detected. Retrying in {delay:.2f}s... (attempt {attempt + 1}/{max_retries + 1})")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error("❌ Max retries reached for throttling")
                            raise
                    else:
                        # Lỗi khác, không retry
                        raise

                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"⚠️ Request failed. Retrying in {delay:.2f}s... (attempt {attempt + 1}/{max_retries + 1})")
                        time.sleep(delay)
                        continue
                    else:
                        raise

            # Nếu đến đây thì đã hết retries
            if last_exception:
                raise last_exception

        return wrapper
    return decorator

# Global rate limiter instance
bedrock_rate_limiter = BedrockRateLimiter(
    requests_per_minute=5,  # 5 requests per minute
    max_retries=3,
    base_delay=2.0
)
