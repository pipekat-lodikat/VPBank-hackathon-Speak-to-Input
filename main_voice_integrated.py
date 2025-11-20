#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Voice Bot Service - Enhanced Entry Point with Full Integrations
Integrated with: Prometheus metrics, Correlation IDs, Structured exceptions, LLM caching

Copyright (c) 2025 Pipekat Lodikat Team
Licensed under the MIT License - see LICENSE file for details
"""
import sys
import os

# Filter ONNX Runtime GPU warning
class FilteredStderr:
    def __init__(self, stream):
        self.stream = stream
        self.buffer = ""

    def write(self, text):
        if "GPU device discovery failed" in text or "device_discovery.cc" in text:
            return len(text)
        self.stream.write(text)
        return len(text)

    def flush(self):
        self.stream.flush()

sys.stderr = FilteredStderr(sys.stderr)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aiohttp import web
from loguru import logger
from dotenv import load_dotenv

# Load environment first
load_dotenv()

# Import monitoring
from src.monitoring import (
    initialize_service_info,
    voice_sessions_total,
    voice_messages_total,
    webrtc_connections_active,
    websocket_connections_active,
    llm_requests_total,
    stt_requests_total,
    tts_requests_total
)
from src.monitoring.middleware import setup_metrics_endpoint

# Import correlation ID logging
from src.utils.logging_config import (
    configure_logging,
    CorrelationIdMiddleware
)

# Import LLM caching
from src.cost.llm_cache import llm_cache

# Import request debouncer
from src.utils.debouncer import RequestDebouncer

# Configure logging with correlation IDs
configure_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format_type="detailed",
    enable_file_logging=True,
    log_file_path="logs/voice_bot.log"
)

# Initialize Prometheus metrics
initialize_service_info("voice-bot", "2.0.0")

# Initialize request debouncer (2 second delay)
browser_service_debouncer = RequestDebouncer(delay_seconds=2.0)

logger.info("🎤 Voice Bot Service - Enhanced Edition")
logger.info("✨ Integrated features:")
logger.info("   - Prometheus metrics (/metrics)")
logger.info("   - Correlation ID tracking")
logger.info("   - LLM response caching")
logger.info("   - Request debouncing (2s)")
logger.info("   - Structured exception handling")

# Import voice bot
from src.voice_bot import create_app as create_voice_app
from src.env_validator import validate_voice_bot_env, warn_optional_env_vars

# Validate required environment variables
validate_voice_bot_env()

# Warn about optional environment variables
warn_optional_env_vars([
    "STUN_SERVER",
    "TURN_SERVER",
    "TURN_USERNAME",
    "TURN_CREDENTIAL",
], "Voice Bot Service")

def create_integrated_app():
    """Create voice bot app with all integrations"""
    # Create base voice bot app
    app = create_voice_app()
    
    # Store service name for metrics
    app['service_name'] = 'voice-bot'
    
    # Add Correlation ID middleware (FIRST)
    app.middlewares.insert(0, CorrelationIdMiddleware.middleware)
    
    # Setup Prometheus metrics endpoint
    setup_metrics_endpoint(app, path="/metrics")
    
    # Track WebSocket connections
    original_ws_handler = None
    for route in app.router._resources:
        if hasattr(route, '_path') and route._path == '/ws':
            # Found WebSocket route - wrap it to track connections
            logger.info("📡 WebSocket route found, adding connection tracking")
            break
    
    logger.info("✅ Voice Bot application configured with all integrations")
    logger.info("   - Metrics endpoint: /metrics")
    logger.info("   - WebSocket: /ws")
    logger.info("   - Health check: /health")
    logger.info("   - Auth: /api/auth/*")
    logger.info("   - Sessions: /api/sessions")
    
    return app

if __name__ == "__main__":
    # Support environment variables for deployment flexibility
    PORT = int(os.getenv("PORT", "7860"))
    HOST = os.getenv("HOST", "0.0.0.0")
    BROWSER_SERVICE_URL = os.getenv("BROWSER_SERVICE_URL", "http://localhost:7863")
    
    logger.info("🚀 Starting Enhanced Voice Bot Service...")
    logger.info(f"📡 Service runs on {HOST}:{PORT}")
    logger.info(f"🔗 Connects to Browser Agent Service: {BROWSER_SERVICE_URL}")
    logger.info("📋 Enhanced Endpoints:")
    logger.info("   POST   /offer (WebRTC)")
    logger.info("   GET    /ws (WebSocket with tracking)")
    logger.info("   GET    /metrics (Prometheus)")
    logger.info("   GET    /api/sessions (List sessions)")
    logger.info("   GET    /api/sessions/{id} (Get session)")
    logger.info("   POST   /api/auth/* (Authentication)")
    
    app = create_integrated_app()
    
    # Track service startup
    voice_sessions_total.labels(status="started").inc()
    
    web.run_app(app, host=HOST, port=PORT)

