"""
Advanced Logging Configuration with Correlation IDs
Enables request tracing across microservices
"""
import uuid
import contextvars
from typing import Optional
from loguru import logger
import sys


# Context variable for correlation ID (thread-safe)
correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'correlation_id', default=None
)


def get_correlation_id() -> str:
    """
    Get current correlation ID or generate new one
    
    Returns:
        Correlation ID string
    """
    corr_id = correlation_id_var.get()
    if not corr_id:
        corr_id = str(uuid.uuid4())
        correlation_id_var.set(corr_id)
    return corr_id


def set_correlation_id(corr_id: str):
    """
    Set correlation ID for current context
    
    Args:
        corr_id: Correlation ID to set
    """
    correlation_id_var.set(corr_id)


def clear_correlation_id():
    """Clear correlation ID from current context"""
    correlation_id_var.set(None)


def correlation_id_filter(record):
    """
    Loguru filter to add correlation ID to log records
    
    Args:
        record: Loguru log record
        
    Returns:
        Modified record with correlation_id
    """
    record["extra"]["correlation_id"] = get_correlation_id()
    return record


def configure_logging(
    level: str = "INFO",
    format_type: str = "detailed",
    enable_file_logging: bool = True,
    log_file_path: str = "logs/app.log"
):
    """
    Configure advanced logging with correlation IDs
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format_type: Format type (simple, detailed, json)
        enable_file_logging: Enable file logging
        log_file_path: Path to log file
    """
    # Remove default logger
    logger.remove()
    
    # Define formats
    formats = {
        "simple": (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[correlation_id]}</cyan> | "
            "<level>{message}</level>"
        ),
        "detailed": (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[correlation_id]}</cyan> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        "json": (
            "{{"
            '"timestamp": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
            '"level": "{level}", '
            '"correlation_id": "{extra[correlation_id]}", '
            '"module": "{name}", '
            '"function": "{function}", '
            '"line": {line}, '
            '"message": "{message}"'
            "}}"
        )
    }
    
    log_format = formats.get(format_type, formats["detailed"])
    
    # Add console handler with correlation ID filter
    logger.add(
        sys.stdout,
        format=log_format,
        level=level,
        colorize=True,
        filter=correlation_id_filter
    )
    
    # Add file handler if enabled
    if enable_file_logging:
        logger.add(
            log_file_path,
            format=log_format,
            level=level,
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            filter=correlation_id_filter
        )
    
    # Add error-only file handler
    if enable_file_logging:
        logger.add(
            log_file_path.replace(".log", "_errors.log"),
            format=log_format,
            level="ERROR",
            rotation="50 MB",
            retention="90 days",
            compression="zip",
            filter=correlation_id_filter
        )
    
    logger.info(f"✅ Logging configured (level: {level}, format: {format_type})")


# Decorator for automatic correlation ID handling
def with_correlation_id(func):
    """
    Decorator to ensure correlation ID exists for function execution
    
    Usage:
        @with_correlation_id
        async def my_function():
            logger.info("This will include correlation_id")
    """
    import functools
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Generate new correlation ID if not exists
        if not correlation_id_var.get():
            set_correlation_id(str(uuid.uuid4()))
        
        try:
            return await func(*args, **kwargs)
        finally:
            # Don't clear - might be nested
            pass
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        if not correlation_id_var.get():
            set_correlation_id(str(uuid.uuid4()))
        
        try:
            return func(*args, **kwargs)
        finally:
            pass
    
    # Return appropriate wrapper
    if hasattr(func, '__code__') and func.__code__.co_flags & 0x00000080:  # CO_COROUTINE
        return async_wrapper
    else:
        return sync_wrapper


class CorrelationIdMiddleware:
    """
    aiohttp middleware for correlation ID propagation
    
    Usage:
        app.middlewares.append(CorrelationIdMiddleware())
    """
    
    CORRELATION_ID_HEADER = "X-Correlation-ID"
    
    @staticmethod
    async def middleware(app, handler):
        async def middleware_handler(request):
            # Extract or generate correlation ID
            corr_id = request.headers.get(
                CorrelationIdMiddleware.CORRELATION_ID_HEADER,
                str(uuid.uuid4())
            )
            
            # Set in context
            set_correlation_id(corr_id)
            
            # Log request
            logger.info(
                f"📥 Incoming request: {request.method} {request.path}",
                extra={"correlation_id": corr_id}
            )
            
            try:
                # Handle request
                response = await handler(request)
                
                # Add correlation ID to response headers
                response.headers[CorrelationIdMiddleware.CORRELATION_ID_HEADER] = corr_id
                
                # Log response
                logger.info(
                    f"📤 Outgoing response: {request.method} {request.path} "
                    f"[{response.status}]",
                    extra={"correlation_id": corr_id}
                )
                
                return response
                
            except Exception as e:
                logger.error(
                    f"❌ Request failed: {request.method} {request.path} - {str(e)}",
                    extra={"correlation_id": corr_id}
                )
                raise
            finally:
                # Clear correlation ID after request
                clear_correlation_id()
        
        return middleware_handler


# Auto-configure logging on import
configure_logging(
    level="INFO",
    format_type="detailed",
    enable_file_logging=True
)

