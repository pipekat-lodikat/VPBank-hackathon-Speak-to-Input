"""
Rate Limiting and DDoS Protection
Implements token bucket algorithm for rate limiting API requests
"""
import time
from typing import Dict, Optional
from collections import defaultdict
from dataclasses import dataclass
from loguru import logger


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    max_requests: int  # Maximum requests allowed
    window_seconds: int  # Time window in seconds
    burst_size: Optional[int] = None  # Maximum burst size (defaults to max_requests)

    def __post_init__(self):
        if self.burst_size is None:
            self.burst_size = self.max_requests


class TokenBucket:
    """
    Token bucket algorithm implementation
    Allows bursts while maintaining average rate limit
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket

        Args:
            capacity: Maximum number of tokens (burst size)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if not enough tokens
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time to wait until tokens are available

        Args:
            tokens: Number of tokens needed

        Returns:
            Seconds to wait (0 if tokens available now)
        """
        self._refill()

        if self.tokens >= tokens:
            return 0.0

        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class RateLimiter:
    """
    Multi-key rate limiter with configurable limits
    Supports per-IP, per-user, and global rate limiting
    """

    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.configs: Dict[str, RateLimitConfig] = {}
        self.violations: Dict[str, int] = defaultdict(int)

    def configure(self, name: str, config: RateLimitConfig):
        """
        Configure a rate limit

        Args:
            name: Rate limit identifier
            config: Rate limit configuration
        """
        self.configs[name] = config
        logger.info(f"📊 Rate limit configured: {name} = {config.max_requests} req/{config.window_seconds}s")

    def _get_bucket(self, limit_name: str, key: str) -> TokenBucket:
        """Get or create token bucket for given key"""
        bucket_key = f"{limit_name}:{key}"

        if bucket_key not in self.buckets:
            config = self.configs.get(limit_name)
            if not config:
                raise ValueError(f"Rate limit '{limit_name}' not configured")

            refill_rate = config.max_requests / config.window_seconds
            self.buckets[bucket_key] = TokenBucket(
                capacity=config.burst_size,
                refill_rate=refill_rate
            )

        return self.buckets[bucket_key]

    def check_limit(self, limit_name: str, key: str, tokens: int = 1) -> bool:
        """
        Check if request is within rate limit

        Args:
            limit_name: Rate limit identifier
            key: Unique key (e.g., IP address, user ID)
            tokens: Number of tokens to consume

        Returns:
            True if allowed, False if rate limited
        """
        try:
            bucket = self._get_bucket(limit_name, key)
            allowed = bucket.consume(tokens)

            if not allowed:
                self.violations[f"{limit_name}:{key}"] += 1
                logger.warning(f"🚨 Rate limit exceeded: {limit_name} for {key} (violations: {self.violations[f'{limit_name}:{key}']})")

            return allowed
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open (allow request) rather than fail closed
            return True

    def get_wait_time(self, limit_name: str, key: str, tokens: int = 1) -> float:
        """
        Get time to wait until request is allowed

        Args:
            limit_name: Rate limit identifier
            key: Unique key
            tokens: Number of tokens needed

        Returns:
            Seconds to wait
        """
        try:
            bucket = self._get_bucket(limit_name, key)
            return bucket.get_wait_time(tokens)
        except Exception as e:
            logger.error(f"Error getting wait time: {e}")
            return 0.0

    def reset(self, limit_name: str, key: str):
        """Reset rate limit for a specific key"""
        bucket_key = f"{limit_name}:{key}"
        if bucket_key in self.buckets:
            del self.buckets[bucket_key]
        if bucket_key in self.violations:
            del self.violations[bucket_key]

    def get_violations(self, limit_name: str, key: str) -> int:
        """Get number of violations for a key"""
        return self.violations.get(f"{limit_name}:{key}", 0)

    def cleanup_old_buckets(self, max_age_seconds: int = 3600):
        """
        Clean up old inactive buckets to prevent memory leak

        Args:
            max_age_seconds: Remove buckets inactive for this long
        """
        now = time.time()
        to_remove = []

        for bucket_key, bucket in self.buckets.items():
            if now - bucket.last_refill > max_age_seconds:
                to_remove.append(bucket_key)

        for key in to_remove:
            del self.buckets[key]
            logger.debug(f"🧹 Cleaned up inactive bucket: {key}")

        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} inactive rate limit buckets")


# Global rate limiter instance
rate_limiter = RateLimiter()


# Predefined rate limit configurations
RATE_LIMITS = {
    "webrtc_offer": RateLimitConfig(max_requests=10, window_seconds=60, burst_size=3),  # 10/min, burst 3
    "browser_execute": RateLimitConfig(max_requests=30, window_seconds=60, burst_size=10),  # 30/min
    "auth_login": RateLimitConfig(max_requests=5, window_seconds=300, burst_size=3),  # 5/5min (prevent brute force)
    "auth_register": RateLimitConfig(max_requests=3, window_seconds=3600),  # 3/hour
    "session_list": RateLimitConfig(max_requests=60, window_seconds=60),  # 60/min
    "websocket": RateLimitConfig(max_requests=100, window_seconds=60, burst_size=20),  # 100/min
}


def init_rate_limits():
    """Initialize default rate limits"""
    for name, config in RATE_LIMITS.items():
        rate_limiter.configure(name, config)
    logger.info(f"✅ Initialized {len(RATE_LIMITS)} rate limit configurations")


# Auto-initialize on import
init_rate_limits()
