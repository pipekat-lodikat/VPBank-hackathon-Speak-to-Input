"""
Custom Exception Classes for VPBank Voice Agent
Structured error handling across all services
"""


class VPBankException(Exception):
    """Base exception for all VPBank Voice Agent errors"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


# ==================== Service Errors ====================

class ServiceError(VPBankException):
    """Base class for service-level errors"""
    pass


class ServiceUnavailableError(ServiceError):
    """Service is temporarily unavailable"""
    def __init__(self, service_name: str, details: dict = None):
        super().__init__(
            message=f"Service {service_name} is currently unavailable",
            error_code="SERVICE_UNAVAILABLE",
            details=details or {"service": service_name}
        )


class ServiceTimeoutError(ServiceError):
    """Service request timed out"""
    def __init__(self, service_name: str, timeout: float, details: dict = None):
        super().__init__(
            message=f"Service {service_name} timed out after {timeout}s",
            error_code="SERVICE_TIMEOUT",
            details=details or {"service": service_name, "timeout": timeout}
        )


class ServiceConnectionError(ServiceError):
    """Failed to connect to service"""
    def __init__(self, service_name: str, url: str, details: dict = None):
        super().__init__(
            message=f"Failed to connect to {service_name} at {url}",
            error_code="SERVICE_CONNECTION_ERROR",
            details=details or {"service": service_name, "url": url}
        )


# ==================== Browser Automation Errors ====================

class BrowserError(VPBankException):
    """Base class for browser automation errors"""
    pass


class BrowserSessionNotFoundError(BrowserError):
    """Browser session not found"""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Browser session '{session_id}' not found",
            error_code="BROWSER_SESSION_NOT_FOUND",
            details={"session_id": session_id}
        )


class BrowserNavigationError(BrowserError):
    """Failed to navigate to URL"""
    def __init__(self, url: str, reason: str = None):
        super().__init__(
            message=f"Failed to navigate to {url}" + (f": {reason}" if reason else ""),
            error_code="BROWSER_NAVIGATION_ERROR",
            details={"url": url, "reason": reason}
        )


class BrowserFieldNotFoundError(BrowserError):
    """Form field not found on page"""
    def __init__(self, field_name: str, form_url: str = None):
        super().__init__(
            message=f"Field '{field_name}' not found on page",
            error_code="BROWSER_FIELD_NOT_FOUND",
            details={"field_name": field_name, "form_url": form_url}
        )


class BrowserFormSubmissionError(BrowserError):
    """Failed to submit form"""
    def __init__(self, reason: str, form_url: str = None):
        super().__init__(
            message=f"Failed to submit form: {reason}",
            error_code="BROWSER_FORM_SUBMISSION_ERROR",
            details={"reason": reason, "form_url": form_url}
        )


class BrowserExecutionError(BrowserError):
    """Browser agent execution failed"""
    def __init__(self, task: str, reason: str):
        super().__init__(
            message=f"Browser execution failed for task: {task}",
            error_code="BROWSER_EXECUTION_ERROR",
            details={"task": task, "reason": reason}
        )


# ==================== Authentication Errors ====================

class AuthenticationError(VPBankException):
    """Base class for authentication errors"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Invalid username or password"""
    def __init__(self, username: str = None):
        super().__init__(
            message="Invalid username or password",
            error_code="INVALID_CREDENTIALS",
            details={"username": username} if username else {}
        )


class TokenExpiredError(AuthenticationError):
    """Access token has expired"""
    def __init__(self):
        super().__init__(
            message="Access token has expired",
            error_code="TOKEN_EXPIRED"
        )


class TokenInvalidError(AuthenticationError):
    """Access token is invalid"""
    def __init__(self):
        super().__init__(
            message="Access token is invalid",
            error_code="TOKEN_INVALID"
        )


class UnauthorizedError(AuthenticationError):
    """User is not authorized for this action"""
    def __init__(self, action: str = None):
        super().__init__(
            message=f"Not authorized" + (f" to {action}" if action else ""),
            error_code="UNAUTHORIZED",
            details={"action": action} if action else {}
        )


# ==================== Validation Errors ====================

class ValidationError(VPBankException):
    """Base class for validation errors"""
    pass


class InvalidInputError(ValidationError):
    """Input validation failed"""
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Invalid input for field '{field}': {reason}",
            error_code="INVALID_INPUT",
            details={"field": field, "reason": reason}
        )


class MissingRequiredFieldError(ValidationError):
    """Required field is missing"""
    def __init__(self, field: str):
        super().__init__(
            message=f"Required field '{field}' is missing",
            error_code="MISSING_REQUIRED_FIELD",
            details={"field": field}
        )


class InvalidFormatError(ValidationError):
    """Input format is invalid"""
    def __init__(self, field: str, expected_format: str, actual_value: str = None):
        super().__init__(
            message=f"Invalid format for field '{field}'. Expected: {expected_format}",
            error_code="INVALID_FORMAT",
            details={
                "field": field,
                "expected_format": expected_format,
                "actual_value": actual_value
            }
        )


# ==================== Database Errors ====================

class DatabaseError(VPBankException):
    """Base class for database errors"""
    pass


class SessionNotFoundError(DatabaseError):
    """Session not found in database"""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session '{session_id}' not found",
            error_code="SESSION_NOT_FOUND",
            details={"session_id": session_id}
        )


class DatabaseConnectionError(DatabaseError):
    """Failed to connect to database"""
    def __init__(self, db_name: str, reason: str = None):
        super().__init__(
            message=f"Failed to connect to database '{db_name}'" + (f": {reason}" if reason else ""),
            error_code="DATABASE_CONNECTION_ERROR",
            details={"database": db_name, "reason": reason}
        )


class DatabaseOperationError(DatabaseError):
    """Database operation failed"""
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Database operation '{operation}' failed: {reason}",
            error_code="DATABASE_OPERATION_ERROR",
            details={"operation": operation, "reason": reason}
        )


# ==================== AI/LLM Errors ====================

class AIError(VPBankException):
    """Base class for AI/LLM errors"""
    pass


class LLMTimeoutError(AIError):
    """LLM request timed out"""
    def __init__(self, model: str, timeout: float):
        super().__init__(
            message=f"LLM request to {model} timed out after {timeout}s",
            error_code="LLM_TIMEOUT",
            details={"model": model, "timeout": timeout}
        )


class LLMRateLimitError(AIError):
    """LLM rate limit exceeded"""
    def __init__(self, model: str, retry_after: int = None):
        super().__init__(
            message=f"Rate limit exceeded for {model}",
            error_code="LLM_RATE_LIMIT",
            details={"model": model, "retry_after": retry_after}
        )


class LLMInvalidResponseError(AIError):
    """LLM returned invalid response"""
    def __init__(self, model: str, reason: str):
        super().__init__(
            message=f"Invalid response from {model}: {reason}",
            error_code="LLM_INVALID_RESPONSE",
            details={"model": model, "reason": reason}
        )


class STTError(AIError):
    """Speech-to-text error"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Speech-to-text failed: {reason}",
            error_code="STT_ERROR",
            details={"reason": reason}
        )


class TTSError(AIError):
    """Text-to-speech error"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Text-to-speech failed: {reason}",
            error_code="TTS_ERROR",
            details={"reason": reason}
        )


# ==================== WebRTC Errors ====================

class WebRTCError(VPBankException):
    """Base class for WebRTC errors"""
    pass


class WebRTCConnectionError(WebRTCError):
    """WebRTC connection failed"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"WebRTC connection failed: {reason}",
            error_code="WEBRTC_CONNECTION_ERROR",
            details={"reason": reason}
        )


class WebRTCInvalidOfferError(WebRTCError):
    """Invalid WebRTC offer"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid WebRTC offer: {reason}",
            error_code="WEBRTC_INVALID_OFFER",
            details={"reason": reason}
        )


# ==================== Configuration Errors ====================

class ConfigurationError(VPBankException):
    """Base class for configuration errors"""
    pass


class MissingEnvironmentVariableError(ConfigurationError):
    """Required environment variable is missing"""
    def __init__(self, var_name: str):
        super().__init__(
            message=f"Required environment variable '{var_name}' is not set",
            error_code="MISSING_ENV_VAR",
            details={"variable": var_name}
        )


class InvalidConfigurationError(ConfigurationError):
    """Configuration is invalid"""
    def __init__(self, config_name: str, reason: str):
        super().__init__(
            message=f"Invalid configuration for '{config_name}': {reason}",
            error_code="INVALID_CONFIGURATION",
            details={"config": config_name, "reason": reason}
        )


# ==================== Rate Limiting Errors ====================

class RateLimitError(VPBankException):
    """Rate limit exceeded"""
    def __init__(self, resource: str, limit: int, window: str, retry_after: int = None):
        super().__init__(
            message=f"Rate limit exceeded for {resource}: {limit} requests per {window}",
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "resource": resource,
                "limit": limit,
                "window": window,
                "retry_after": retry_after
            }
        )

