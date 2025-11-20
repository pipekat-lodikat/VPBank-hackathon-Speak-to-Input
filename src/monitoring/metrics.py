"""
Prometheus Metrics for VPBank Voice Agent
Comprehensive monitoring and observability
"""
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    Info,
    generate_latest,
    REGISTRY
)
from typing import Optional
import time
from functools import wraps
from loguru import logger


# ==================== Service Health Metrics ====================

service_info = Info(
    'vpbank_voice_agent_service_info',
    'Service information'
)

service_health = Gauge(
    'vpbank_voice_agent_service_health',
    'Service health status (1=healthy, 0=unhealthy)',
    ['service_name']
)

service_uptime_seconds = Gauge(
    'vpbank_voice_agent_service_uptime_seconds',
    'Service uptime in seconds',
    ['service_name']
)


# ==================== HTTP Request Metrics ====================

http_requests_total = Counter(
    'vpbank_voice_agent_http_requests_total',
    'Total HTTP requests',
    ['service', 'method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'vpbank_voice_agent_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['service', 'method', 'endpoint'],
    buckets=(.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, float("inf"))
)

http_request_size_bytes = Summary(
    'vpbank_voice_agent_http_request_size_bytes',
    'HTTP request size in bytes',
    ['service', 'method', 'endpoint']
)

http_response_size_bytes = Summary(
    'vpbank_voice_agent_http_response_size_bytes',
    'HTTP response size in bytes',
    ['service', 'method', 'endpoint']
)


# ==================== Voice Bot Metrics ====================

voice_sessions_total = Counter(
    'vpbank_voice_agent_voice_sessions_total',
    'Total voice sessions started',
    ['status']  # status: started, completed, failed
)

voice_session_duration_seconds = Histogram(
    'vpbank_voice_agent_voice_session_duration_seconds',
    'Voice session duration in seconds',
    buckets=(10, 30, 60, 120, 300, 600, 1800, 3600, float("inf"))
)

voice_messages_total = Counter(
    'vpbank_voice_agent_voice_messages_total',
    'Total voice messages processed',
    ['role', 'status']  # role: user/assistant, status: success/failed
)

voice_message_processing_duration_seconds = Histogram(
    'vpbank_voice_agent_voice_message_processing_duration_seconds',
    'Voice message processing duration',
    ['message_type'],  # message_type: user/assistant
    buckets=(.1, .25, .5, 1.0, 2.5, 5.0, 10.0, float("inf"))
)

webrtc_connections_active = Gauge(
    'vpbank_voice_agent_webrtc_connections_active',
    'Active WebRTC connections'
)

websocket_connections_active = Gauge(
    'vpbank_voice_agent_websocket_connections_active',
    'Active WebSocket connections'
)


# ==================== Browser Automation Metrics ====================

browser_sessions_total = Counter(
    'vpbank_voice_agent_browser_sessions_total',
    'Total browser automation sessions',
    ['status', 'form_type']  # status: success/failed, form_type: loan/crm/hr/etc
)

browser_session_duration_seconds = Histogram(
    'vpbank_voice_agent_browser_session_duration_seconds',
    'Browser session duration in seconds',
    ['form_type'],
    buckets=(1, 5, 10, 20, 30, 60, 120, 300, float("inf"))
)

browser_actions_total = Counter(
    'vpbank_voice_agent_browser_actions_total',
    'Total browser actions performed',
    ['action_type', 'status']  # action_type: navigate/fill/click/submit
)

browser_action_duration_seconds = Histogram(
    'vpbank_voice_agent_browser_action_duration_seconds',
    'Browser action duration in seconds',
    ['action_type'],
    buckets=(.1, .5, 1.0, 2.0, 5.0, 10.0, 30.0, float("inf"))
)

browser_fields_filled_total = Counter(
    'vpbank_voice_agent_browser_fields_filled_total',
    'Total form fields filled',
    ['form_type', 'field_name']
)

browser_form_submissions_total = Counter(
    'vpbank_voice_agent_browser_form_submissions_total',
    'Total form submissions',
    ['form_type', 'status']  # status: success/failed
)


# ==================== AI/LLM Metrics ====================

llm_requests_total = Counter(
    'vpbank_voice_agent_llm_requests_total',
    'Total LLM requests',
    ['provider', 'model', 'status']  # provider: aws/openai, status: success/failed
)

llm_request_duration_seconds = Histogram(
    'vpbank_voice_agent_llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['provider', 'model'],
    buckets=(.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0, float("inf"))
)

llm_tokens_total = Counter(
    'vpbank_voice_agent_llm_tokens_total',
    'Total LLM tokens consumed',
    ['provider', 'model', 'token_type']  # token_type: prompt/completion
)

llm_cost_usd_total = Counter(
    'vpbank_voice_agent_llm_cost_usd_total',
    'Total LLM cost in USD',
    ['provider', 'model']
)

llm_cache_hits_total = Counter(
    'vpbank_voice_agent_llm_cache_hits_total',
    'LLM cache hits',
    ['cache_type']  # cache_type: response/embedding
)

llm_cache_misses_total = Counter(
    'vpbank_voice_agent_llm_cache_misses_total',
    'LLM cache misses',
    ['cache_type']
)


# ==================== STT/TTS Metrics ====================

stt_requests_total = Counter(
    'vpbank_voice_agent_stt_requests_total',
    'Total speech-to-text requests',
    ['provider', 'language', 'status']
)

stt_request_duration_seconds = Histogram(
    'vpbank_voice_agent_stt_request_duration_seconds',
    'STT request duration in seconds',
    ['provider'],
    buckets=(.1, .25, .5, 1.0, 2.0, 5.0, float("inf"))
)

stt_audio_duration_seconds = Summary(
    'vpbank_voice_agent_stt_audio_duration_seconds',
    'Audio duration processed by STT',
    ['provider']
)

tts_requests_total = Counter(
    'vpbank_voice_agent_tts_requests_total',
    'Total text-to-speech requests',
    ['provider', 'language', 'status']
)

tts_request_duration_seconds = Histogram(
    'vpbank_voice_agent_tts_request_duration_seconds',
    'TTS request duration in seconds',
    ['provider'],
    buckets=(.1, .25, .5, 1.0, 2.0, 5.0, float("inf"))
)

tts_characters_total = Counter(
    'vpbank_voice_agent_tts_characters_total',
    'Total characters synthesized by TTS',
    ['provider']
)


# ==================== Database Metrics ====================

database_operations_total = Counter(
    'vpbank_voice_agent_database_operations_total',
    'Total database operations',
    ['database', 'operation', 'status']  # database: dynamodb, operation: get/put/scan/update
)

database_operation_duration_seconds = Histogram(
    'vpbank_voice_agent_database_operation_duration_seconds',
    'Database operation duration in seconds',
    ['database', 'operation'],
    buckets=(.005, .01, .025, .05, .1, .25, .5, 1.0, float("inf"))
)

database_connection_pool_size = Gauge(
    'vpbank_voice_agent_database_connection_pool_size',
    'Database connection pool size',
    ['database']
)


# ==================== Authentication Metrics ====================

auth_requests_total = Counter(
    'vpbank_voice_agent_auth_requests_total',
    'Total authentication requests',
    ['operation', 'status']  # operation: login/register/verify/refresh
)

auth_request_duration_seconds = Histogram(
    'vpbank_voice_agent_auth_request_duration_seconds',
    'Authentication request duration in seconds',
    ['operation'],
    buckets=(.1, .25, .5, 1.0, 2.0, 5.0, float("inf"))
)

auth_active_sessions = Gauge(
    'vpbank_voice_agent_auth_active_sessions',
    'Active authenticated sessions'
)


# ==================== Error Metrics ====================

errors_total = Counter(
    'vpbank_voice_agent_errors_total',
    'Total errors',
    ['service', 'error_type', 'error_code']
)

exceptions_total = Counter(
    'vpbank_voice_agent_exceptions_total',
    'Total exceptions raised',
    ['service', 'exception_class']
)


# ==================== Business Metrics ====================

forms_filled_total = Counter(
    'vpbank_voice_agent_forms_filled_total',
    'Total forms filled',
    ['form_type', 'status']  # form_type: loan/crm/hr/compliance/operations
)

forms_submitted_total = Counter(
    'vpbank_voice_agent_forms_submitted_total',
    'Total forms submitted',
    ['form_type', 'status']
)

user_intents_detected_total = Counter(
    'vpbank_voice_agent_user_intents_detected_total',
    'Total user intents detected',
    ['intent_type']  # intent_type: loan/crm/hr/etc
)


# ==================== Helper Functions ====================

def track_duration(metric: Histogram):
    """Decorator to track duration of function execution"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # Extract labels from function arguments if available
                labels = kwargs.get('_metric_labels', {})
                metric.labels(**labels).observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                labels = kwargs.get('_metric_labels', {})
                metric.labels(**labels).observe(duration)
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x00000080:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def track_counter(metric: Counter):
    """Decorator to track counter increments"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            labels = kwargs.get('_metric_labels', {})
            try:
                result = await func(*args, **kwargs)
                metric.labels(**labels, status='success').inc()
                return result
            except Exception as e:
                metric.labels(**labels, status='failed').inc()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            labels = kwargs.get('_metric_labels', {})
            try:
                result = func(*args, **kwargs)
                metric.labels(**labels, status='success').inc()
                return result
            except Exception as e:
                metric.labels(**labels, status='failed').inc()
                raise
        
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x00000080:
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def get_metrics():
    """Get current metrics in Prometheus format"""
    return generate_latest(REGISTRY)


def initialize_service_info(service_name: str, version: str):
    """Initialize service information"""
    service_info.info({
        'service_name': service_name,
        'version': version,
        'environment': 'production'  # Can be configured via env var
    })
    service_health.labels(service_name=service_name).set(1)
    logger.info(f"📊 Prometheus metrics initialized for {service_name}")
