"""
Monitoring module for VPBank Voice Agent
Includes Prometheus metrics and distributed tracing
"""
from src.monitoring.metrics import (
    # WebRTC metrics
    webrtc_connections_total,
    webrtc_active_connections,

    # Voice processing metrics
    voice_stt_latency,
    voice_tts_latency,
    voice_llm_latency,
    voice_e2e_latency,

    # Browser agent metrics
    browser_form_fills_total,
    browser_fill_latency,
    browser_fields_filled,
    browser_parallel_fills,

    # Session metrics
    sessions_total,
    session_duration,
    session_messages_total,

    # Auth metrics
    auth_requests_total,
    auth_latency,

    # Rate limiting metrics
    rate_limit_violations_total,

    # Error metrics
    errors_total,

    # AWS metrics
    aws_api_calls_total,
    aws_api_latency,

    # Business metrics
    forms_completed_total,
    vad_context_changes_total,

    # Helper functions
    get_metrics,
    log_metrics_summary,
    track_latency,
    track_counter,
    track_operation,

    # Registry
    metrics_registry,
)

__all__ = [
    "webrtc_connections_total",
    "webrtc_active_connections",
    "voice_stt_latency",
    "voice_tts_latency",
    "voice_llm_latency",
    "voice_e2e_latency",
    "browser_form_fills_total",
    "browser_fill_latency",
    "browser_fields_filled",
    "browser_parallel_fills",
    "sessions_total",
    "session_duration",
    "session_messages_total",
    "auth_requests_total",
    "auth_latency",
    "rate_limit_violations_total",
    "errors_total",
    "aws_api_calls_total",
    "aws_api_latency",
    "forms_completed_total",
    "vad_context_changes_total",
    "get_metrics",
    "log_metrics_summary",
    "track_latency",
    "track_counter",
    "track_operation",
    "metrics_registry",
]
