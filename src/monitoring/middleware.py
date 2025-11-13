"""
Prometheus Metrics Middleware for aiohttp
Tracks HTTP request metrics automatically
"""
import time
from aiohttp import web
from aiohttp.web import middleware
from loguru import logger
from .metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_request_size_bytes,
    http_response_size_bytes
)


@middleware
async def metrics_middleware(request: web.Request, handler):
    """
    Middleware to track HTTP request metrics
    
    Tracks:
    - Total requests by method, endpoint, status code
    - Request duration
    - Request/response sizes
    """
    start_time = time.time()
    
    # Extract request info
    method = request.method
    path = request.path
    service = request.app.get('service_name', 'unknown')
    
    # Sanitize path (replace IDs with placeholders)
    sanitized_path = sanitize_path(path)
    
    try:
        # Get request size
        request_size = request.content_length or 0
        
        # Handle request
        response = await handler(request)
        
        # Track metrics
        duration = time.time() - start_time
        status = response.status
        
        # Get response size
        response_size = response.content_length or 0
        if hasattr(response, 'body') and response.body:
            response_size = len(response.body)
        
        # Record metrics
        http_requests_total.labels(
            service=service,
            method=method,
            endpoint=sanitized_path,
            status_code=str(status)
        ).inc()
        
        http_request_duration_seconds.labels(
            service=service,
            method=method,
            endpoint=sanitized_path
        ).observe(duration)
        
        http_request_size_bytes.labels(
            service=service,
            method=method,
            endpoint=sanitized_path
        ).observe(request_size)
        
        http_response_size_bytes.labels(
            service=service,
            method=method,
            endpoint=sanitized_path
        ).observe(response_size)
        
        # Log slow requests (>1s)
        if duration > 1.0:
            logger.warning(
                f"⏱️  Slow request: {method} {path} took {duration:.2f}s"
            )
        
        return response
        
    except web.HTTPException as e:
        # Handle HTTP exceptions
        duration = time.time() - start_time
        status = e.status
        
        http_requests_total.labels(
            service=service,
            method=method,
            endpoint=sanitized_path,
            status_code=str(status)
        ).inc()
        
        http_request_duration_seconds.labels(
            service=service,
            method=method,
            endpoint=sanitized_path
        ).observe(duration)
        
        raise
        
    except Exception as e:
        # Handle unexpected exceptions
        duration = time.time() - start_time
        
        http_requests_total.labels(
            service=service,
            method=method,
            endpoint=sanitized_path,
            status_code='500'
        ).inc()
        
        http_request_duration_seconds.labels(
            service=service,
            method=method,
            endpoint=sanitized_path
        ).observe(duration)
        
        logger.error(f"❌ Request error: {method} {path} - {str(e)}")
        raise


def sanitize_path(path: str) -> str:
    """
    Sanitize URL path to replace dynamic segments with placeholders
    
    Examples:
        /api/sessions/123456 -> /api/sessions/{id}
        /api/users/abc-def-ghi -> /api/users/{id}
    """
    import re
    
    # Replace UUIDs
    path = re.sub(
        r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        '/{uuid}',
        path,
        flags=re.IGNORECASE
    )
    
    # Replace numeric IDs
    path = re.sub(r'/\d+', '/{id}', path)
    
    # Replace alphanumeric IDs (session IDs, etc.)
    path = re.sub(
        r'/[a-zA-Z0-9_-]{10,}',
        '/{id}',
        path
    )
    
    return path


async def metrics_endpoint(request: web.Request):
    """
    Prometheus metrics endpoint
    Returns metrics in Prometheus exposition format
    """
    from .metrics import get_metrics
    
    metrics = get_metrics()
    return web.Response(
        body=metrics,
        content_type='text/plain; version=0.0.4',
        charset='utf-8'
    )


def setup_metrics_endpoint(app: web.Application, path: str = '/metrics'):
    """
    Setup metrics endpoint on aiohttp application
    
    Args:
        app: aiohttp Application instance
        path: Path for metrics endpoint (default: /metrics)
    """
    from aiohttp import web
    
    # Add metrics route
    app.router.add_get(path, metrics_endpoint)
    
    logger.info(f"📊 Metrics endpoint available at {path}")

