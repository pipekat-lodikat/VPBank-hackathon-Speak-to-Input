"""
VPBank Multi-Agent System - Supervisor Pattern
"""
from .graph import build_supervisor_workflow, MultiAgentState, create_initial_state

__all__ = [
    "build_supervisor_workflow",
    "MultiAgentState",
    "create_initial_state"
]
"""
Multi-agent orchestration using LangGraph for automated form filling
across 5 business use cases.
"""
