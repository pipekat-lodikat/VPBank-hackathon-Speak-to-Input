"""
LLM Response Caching
Caches common LLM responses to reduce API costs and improve latency
"""
import hashlib
import json
import time
from typing import Optional, Dict, Any
from collections import OrderedDict
from loguru import logger


class LRUCache:
    """Least Recently Used (LRU) cache implementation"""

    def __init__(self, capacity: int = 1000):
        """
        Initialize LRU cache

        Args:
            capacity: Maximum number of items in cache
        """
        self.cache: OrderedDict = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            value, timestamp = self.cache[key]
            logger.debug(f"💚 Cache HIT: {key[:50]}...")
            return value
        else:
            self.misses += 1
            logger.debug(f"💔 Cache MISS: {key[:50]}...")
            return None

    def put(self, key: str, value: Any):
        """
        Put value in cache

        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Remove least recently used
                removed_key = next(iter(self.cache))
                del self.cache[removed_key]
                logger.debug(f"🗑️ Cache eviction: {removed_key[:50]}...")

        self.cache[key] = (value, time.time())
        logger.debug(f"💾 Cache PUT: {key[:50]}...")

    def clear(self):
        """Clear all cached items"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("🧹 Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
        }


class LLMCache:
    """
    Intelligent LLM response caching with TTL and similarity matching
    """

    def __init__(self, capacity: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize LLM cache

        Args:
            capacity: Maximum number of cached responses
            ttl_seconds: Time-to-live for cached responses (default 1 hour)
        """
        self.cache = LRUCache(capacity)
        self.ttl_seconds = ttl_seconds

    def _normalize_prompt(self, prompt: str) -> str:
        """
        Normalize prompt for caching

        Args:
            prompt: Raw prompt text

        Returns:
            Normalized prompt
        """
        # Lowercase and strip whitespace
        normalized = prompt.lower().strip()

        # Remove extra whitespace
        normalized = " ".join(normalized.split())

        return normalized

    def _get_cache_key(self, prompt: str, model: str = "default", temperature: float = 0.0) -> str:
        """
        Generate cache key for prompt

        Args:
            prompt: Prompt text
            model: Model name
            temperature: Temperature parameter

        Returns:
            Cache key (hash)
        """
        normalized = self._normalize_prompt(prompt)

        # Include model and temperature in key
        key_data = f"{model}|{temperature}|{normalized}"

        # Hash for compact key
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()

        return key_hash

    def get(self, prompt: str, model: str = "default", temperature: float = 0.0) -> Optional[str]:
        """
        Get cached LLM response

        Args:
            prompt: Prompt text
            model: Model name
            temperature: Temperature parameter

        Returns:
            Cached response or None
        """
        # Only cache deterministic responses (low temperature)
        if temperature > 0.3:
            return None

        key = self._get_cache_key(prompt, model, temperature)
        cached = self.cache.get(key)

        if cached:
            response, timestamp = cached

            # Check TTL
            if time.time() - timestamp > self.ttl_seconds:
                logger.debug(f"⏰ Cache entry expired: {key[:50]}...")
                return None

            logger.info(f"✅ LLM cache hit! Saved API call")
            return response

        return None

    def put(self, prompt: str, response: str, model: str = "default", temperature: float = 0.0):
        """
        Cache LLM response

        Args:
            prompt: Prompt text
            response: LLM response
            model: Model name
            temperature: Temperature parameter
        """
        # Only cache deterministic responses
        if temperature > 0.3:
            return

        key = self._get_cache_key(prompt, model, temperature)
        self.cache.put(key, (response, time.time()))

        logger.info(f"💾 Cached LLM response for future use")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.cache.get_stats()
        stats["ttl_seconds"] = self.ttl_seconds

        # Calculate potential cost savings (rough estimate)
        # Assume $0.003 per request (Claude Sonnet 4 cost)
        estimated_savings = stats["hits"] * 0.003

        stats["estimated_cost_savings_usd"] = round(estimated_savings, 2)

        return stats

    def clear(self):
        """Clear cache"""
        self.cache.clear()


# Global LLM cache instance
llm_cache = LLMCache(capacity=1000, ttl_seconds=3600)


# Common greeting responses (pre-cached)
COMMON_RESPONSES = {
    "xin chào": "Xin chào! Tôi là trợ lý ảo của VPBank. Tôi có thể giúp anh/chị điền form qua giọng nói. Anh/chị cần làm gì hôm nay?",
    "chào": "Chào anh/chị! Tôi có thể hỗ trợ điền các loại form: đơn vay vốn, cập nhật CRM, yêu cầu HR, báo cáo tuân thủ, và kiểm tra giao dịch. Anh/chị muốn làm gì?",
    "hello": "Hello! I'm VPBank's voice assistant. How can I help you today?",
    "hi": "Hi! I can help you fill forms using voice. What would you like to do?",
    "cảm ơn": "Rất vui được hỗ trợ anh/chị! Nếu cần gì thêm, hãy cho tôi biết nhé.",
    "thank you": "You're welcome! Feel free to ask if you need anything else.",
    "tạm biệt": "Tạm biệt! Chúc anh/chị một ngày tốt lành.",
    "goodbye": "Goodbye! Have a great day!",
}


def init_common_responses():
    """Pre-populate cache with common responses"""
    for prompt, response in COMMON_RESPONSES.items():
        llm_cache.put(prompt, response)

    logger.info(f"✅ Pre-cached {len(COMMON_RESPONSES)} common responses")


# Auto-initialize on import
init_common_responses()
