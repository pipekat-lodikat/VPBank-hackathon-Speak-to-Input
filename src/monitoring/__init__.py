"""
Monitoring and Observability Module
"""
from .metrics import (
    # Service health
    service_health,
    service_uptime_seconds,
    initialize_service_info,
    get_metrics,
    
    # HTTP metrics
    http_requests_total,
    http_request_duration_seconds,
    
    # Voice bot metrics
    voice_sessions_total,
    voice_messages_total,
    webrtc_connections_active,
    websocket_connections_active,
    
    # Browser metrics
    browser_sessions_total,
    browser_session_duration_seconds,
    browser_fields_filled_total,
    browser_form_submissions_total,
    
    # AI/LLM metrics
    llm_requests_total,
    llm_request_duration_seconds,
    llm_tokens_total,
    llm_cost_usd_total,
    llm_cache_hits_total,
    llm_cache_misses_total,
    
    # STT/TTS metrics
    stt_requests_total,
    tts_requests_total,
    
    # Database metrics
    database_operations_total,
    database_operation_duration_seconds,
    
    # Auth metrics
    auth_requests_total,
    
    # Error metrics
    errors_total,
    exceptions_total,
    
    # Business metrics
    forms_filled_total,
    forms_submitted_total,
    
    # Helper functions
    track_duration,
    track_counter,
)

__all__ = [
    'service_health',
    'service_uptime_seconds',
    'initialize_service_info',
    'get_metrics',
    'http_requests_total',
    'http_request_duration_seconds',
    'voice_sessions_total',
    'voice_messages_total',
    'webrtc_connections_active',
    'websocket_connections_active',
    'browser_sessions_total',
    'browser_session_duration_seconds',
    'browser_fields_filled_total',
    'browser_form_submissions_total',
    'llm_requests_total',
    'llm_request_duration_seconds',
    'llm_tokens_total',
    'llm_cost_usd_total',
    'llm_cache_hits_total',
    'llm_cache_misses_total',
    'stt_requests_total',
    'tts_requests_total',
    'database_operations_total',
    'database_operation_duration_seconds',
    'auth_requests_total',
    'errors_total',
    'exceptions_total',
    'forms_filled_total',
    'forms_submitted_total',
    'track_duration',
    'track_counter',
]
