"""
Cost optimization module for VPBank Voice Agent
Includes LLM caching and model fallback strategies
"""
from src.cost.llm_cache import LLMCache, llm_cache, init_common_responses, COMMON_RESPONSES

__all__ = [
    "LLMCache",
    "llm_cache",
    "init_common_responses",
    "COMMON_RESPONSES",
]
