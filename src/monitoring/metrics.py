"""
Prometheus Metrics for VPBank Voice Agent
Tracks performance, errors, and business metrics
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, REGISTRY
from prometheus_client.core import CollectorRegistry
from functools import wraps
import time
from typing import Callable
from loguru import logger


# Create custom registry to avoid conflicts
metrics_registry = CollectorRegistry(auto_describe=True)

# ==================== Voice Bot Metrics ====================

# WebRTC connections
webrtc_connections_total = Counter(
    'vpbank_webrtc_connections_total',
    'Total number of WebRTC connections',
    ['status'],  # connected, failed, disconnected
    registry=metrics_registry
)

webrtc_active_connections = Gauge(
    'vpbank_webrtc_active_connections',
    'Currently active WebRTC connections',
    registry=metrics_registry
)

# Voice processing latency
voice_stt_latency = Histogram(
    'vpbank_voice_stt_latency_seconds',
    'Speech-to-text processing latency',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=metrics_registry
)

voice_tts_latency = Histogram(
    'vpbank_voice_tts_latency_seconds',
    'Text-to-speech processing latency',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=metrics_registry
)

voice_llm_latency = Histogram(
    'vpbank_voice_llm_latency_seconds',
    'LLM processing latency',
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0],
    registry=metrics_registry
)

# Total end-to-end latency (user speaks → bot responds)
voice_e2e_latency = Histogram(
    'vpbank_voice_e2e_latency_seconds',
    'End-to-end voice processing latency',
    buckets=[1.0, 2.0, 3.0, 5.0, 10.0, 15.0, 30.0],
    registry=metrics_registry
)

# ==================== Browser Agent Metrics ====================

browser_form_fills_total = Counter(
    'vpbank_browser_form_fills_total',
    'Total number of form fill operations',
    ['form_type', 'status'],  # loan/crm/hr/compliance/operations, success/failure
    registry=metrics_registry
)

browser_fill_latency = Histogram(
    'vpbank_browser_fill_latency_seconds',
    'Browser form fill latency',
    ['form_type'],
    buckets=[5.0, 10.0, 20.0, 30.0, 60.0, 120.0],
    registry=metrics_registry
)

browser_fields_filled = Counter(
    'vpbank_browser_fields_filled_total',
    'Total number of form fields filled',
    ['form_type', 'field_name'],
    registry=metrics_registry
)

browser_parallel_fills = Counter(
    'vpbank_browser_parallel_fills_total',
    'Number of parallel form fill operations',
    ['fields_count'],  # Number of fields filled in parallel
    registry=metrics_registry
)

# ==================== Session Metrics ====================

sessions_total = Counter(
    'vpbank_sessions_total',
    'Total number of voice sessions',
    ['status'],  # started, completed, failed
    registry=metrics_registry
)

session_duration = Histogram(
    'vpbank_session_duration_seconds',
    'Voice session duration',
    buckets=[30, 60, 120, 300, 600, 1800],  # 30s to 30min
    registry=metrics_registry
)

session_messages_total = Counter(
    'vpbank_session_messages_total',
    'Total messages in sessions',
    ['role'],  # user, assistant
    registry=metrics_registry
)

# ==================== Authentication Metrics ====================

auth_requests_total = Counter(
    'vpbank_auth_requests_total',
    'Total authentication requests',
    ['endpoint', 'status'],  # login/register/verify, success/failure
    registry=metrics_registry
)

auth_latency = Histogram(
    'vpbank_auth_latency_seconds',
    'Authentication request latency',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
    registry=metrics_registry
)

# ==================== Rate Limiting Metrics ====================

rate_limit_violations_total = Counter(
    'vpbank_rate_limit_violations_total',
    'Total rate limit violations',
    ['limit_name'],  # webrtc_offer, browser_execute, auth_login
    registry=metrics_registry
)

# ==================== Error Metrics ====================

errors_total = Counter(
    'vpbank_errors_total',
    'Total errors by component',
    ['component', 'error_type'],
    registry=metrics_registry
)

# ==================== AWS Service Metrics ====================

aws_api_calls_total = Counter(
    'vpbank_aws_api_calls_total',
    'Total AWS API calls',
    ['service', 'status'],  # transcribe/bedrock/cognito/dynamodb, success/failure
    registry=metrics_registry
)

aws_api_latency = Histogram(
    'vpbank_aws_api_latency_seconds',
    'AWS API call latency',
    ['service'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=metrics_registry
)

# ==================== System Info ====================

system_info = Info(
    'vpbank_system',
    'System information',
    registry=metrics_registry
)

# Set system info
system_info.info({
    'version': '1.0.0',
    'service': 'vpbank-voice-agent',
    'environment': 'production'
})

# ==================== Business Metrics ====================

forms_completed_total = Counter(
    'vpbank_forms_completed_total',
    'Total forms completed successfully',
    ['form_type'],
    registry=metrics_registry
)

vad_context_changes_total = Counter(
    'vpbank_vad_context_changes_total',
    'Total VAD context changes',
    ['from_context', 'to_context'],
    registry=metrics_registry
)

# ==================== Accuracy Metrics ====================

# Form filling accuracy
form_field_accuracy = Gauge(
    'vpbank_form_field_accuracy_percent',
    'Current form field filling accuracy percentage',
    ['form_type'],
    registry=metrics_registry
)

form_completion_rate = Gauge(
    'vpbank_form_completion_rate_percent',
    'Percentage of forms completed with 99%+ accuracy',
    ['form_type'],
    registry=metrics_registry
)

# Command understanding accuracy
command_understanding_rate = Gauge(
    'vpbank_command_understanding_rate_percent',
    'Command understanding accuracy percentage',
    registry=metrics_registry
)

# Overall system accuracy
overall_system_accuracy = Gauge(
    'vpbank_overall_system_accuracy_percent',
    'Overall system accuracy percentage',
    registry=metrics_registry
)

# Field-level errors
field_errors_total = Counter(
    'vpbank_field_errors_total',
    'Total field-level errors',
    ['field_name', 'error_type'],  # missing, incorrect, format_error
    registry=metrics_registry
)

# Accuracy tracking counters
accuracy_checks_total = Counter(
    'vpbank_accuracy_checks_total',
    'Total accuracy validation checks performed',
    ['check_type'],  # form, command, field
    registry=metrics_registry
)


# ==================== Decorator for automatic metrics ====================

def track_latency(metric: Histogram, labels: dict = None):
    """
    Decorator to automatically track function latency

    Usage:
        @track_latency(voice_llm_latency)
        async def process_llm(message):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start
                if labels:
                    metric.labels(**labels).observe(latency)
                else:
                    metric.observe(latency)
                return result
            except Exception as e:
                latency = time.time() - start
                if labels:
                    metric.labels(**labels).observe(latency)
                else:
                    metric.observe(latency)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start
                if labels:
                    metric.labels(**labels).observe(latency)
                else:
                    metric.observe(latency)
                return result
            except Exception as e:
                latency = time.time() - start
                if labels:
                    metric.labels(**labels).observe(latency)
                else:
                    metric.observe(latency)
                raise

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_counter(metric: Counter, labels: dict = None, increment: int = 1):
    """
    Decorator to automatically increment counter

    Usage:
        @track_counter(sessions_total, labels={'status': 'started'})
        async def start_session():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if labels:
                metric.labels(**labels).inc(increment)
            else:
                metric.inc(increment)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if labels:
                metric.labels(**labels).inc(increment)
            else:
                metric.inc(increment)
            return result

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# ==================== Helper functions ====================

def get_metrics() -> bytes:
    """
    Get all metrics in Prometheus format

    Returns:
        bytes: Prometheus metrics text format
    """
    return generate_latest(metrics_registry)


def log_metrics_summary():
    """Log current metrics summary"""
    try:
        logger.info("📊 Metrics Summary:")
        logger.info(f"   Active WebRTC connections: {webrtc_active_connections._value.get()}")
        logger.info(f"   Total sessions: {sessions_total._metrics}")
        logger.info(f"   Total forms filled: {forms_completed_total._metrics}")
    except Exception as e:
        logger.warning(f"Failed to log metrics summary: {e}")


# ==================== Context managers ====================

class track_operation:
    """
    Context manager for tracking operation metrics

    Usage:
        with track_operation('browser_fill', form_fills_total, fill_latency, form_type='loan'):
            # perform operation
            pass
    """
    def __init__(self, operation_name: str, counter: Counter, histogram: Histogram, **labels):
        self.operation_name = operation_name
        self.counter = counter
        self.histogram = histogram
        self.labels = labels
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        latency = time.time() - self.start_time

        # Record latency
        if self.labels:
            self.histogram.labels(**self.labels).observe(latency)
        else:
            self.histogram.observe(latency)

        # Record counter
        status = 'failure' if exc_type else 'success'
        counter_labels = {**self.labels, 'status': status}
        self.counter.labels(**counter_labels).inc()

        logger.debug(f"📊 {self.operation_name}: {latency:.3f}s ({status})")

        return False  # Don't suppress exceptions
