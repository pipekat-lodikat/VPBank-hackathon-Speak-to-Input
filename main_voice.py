#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Voice Bot Service - Entry Point
Standalone service chỉ chạy Voice Bot (WebRTC, STT, TTS, LLM)
Giao tiếp với Browser Agent Service qua HTTP API

Copyright (c) 2025 Pipekat Lodikat Team
Licensed under the MIT License - see LICENSE file for details
"""
import sys
import os

# Filter ONNX Runtime GPU warning (harmless on CPU-only systems)
class FilteredStderr:
    def __init__(self, stream):
        self.stream = stream
        self.buffer = ""

    def write(self, text):
        # Filter out ONNX GPU device discovery warning (with or without ANSI codes)
        if "GPU device discovery failed" in text or "device_discovery.cc" in text or "DiscoverDevicesForPlatform" in text:
            return len(text)  # Skip this line
        self.stream.write(text)
        return len(text)

    def flush(self):
        self.stream.flush()

sys.stderr = FilteredStderr(sys.stderr)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import voice bot
from src.voice_bot import create_app
from src.env_validator import validate_voice_bot_env, warn_optional_env_vars
from aiohttp import web
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Validate required environment variables
validate_voice_bot_env()

# Warn about optional environment variables
warn_optional_env_vars([
    "STUN_SERVER",
    "TURN_SERVER",
    "TURN_USERNAME",
    "TURN_CREDENTIAL",
], "Voice Bot Service")

if __name__ == "__main__":
    # Support environment variables for deployment flexibility
    PORT = int(os.getenv("PORT", "7860"))
    HOST = os.getenv("HOST", "0.0.0.0")
    BROWSER_SERVICE_URL = os.getenv("BROWSER_SERVICE_URL", "http://localhost:7863")
    
    logger.info("🎤 Starting Voice Bot Service...")
    logger.info(f"📡 Service runs on {HOST}:{PORT}")
    logger.info(f"🔗 Connects to Browser Agent Service: {BROWSER_SERVICE_URL}")
    logger.info("📋 Endpoints:")
    logger.info("   POST   /offer (WebRTC)")
    logger.info("   GET    /ws (WebSocket)")
    logger.info("   GET    /api/sessions (List sessions)")
    logger.info("   GET    /api/sessions/{id} (Get session)")
    
    app = create_app()
    web.run_app(app, host=HOST, port=PORT)

