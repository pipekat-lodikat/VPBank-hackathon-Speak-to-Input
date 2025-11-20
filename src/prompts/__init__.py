"""
System Prompts for VPBank Voice Agent
Multiple versions for A/B testing and optimization
"""
from src.prompts.system_prompt_v2 import (
    SYSTEM_PROMPT_V2,
    SYSTEM_PROMPT_V2_COMPACT,
    SYSTEM_PROMPT_V2_MINIMAL,
    get_system_prompt
)

__all__ = [
    "SYSTEM_PROMPT_V2",
    "SYSTEM_PROMPT_V2_COMPACT",
    "SYSTEM_PROMPT_V2_MINIMAL",
    "get_system_prompt"
]
