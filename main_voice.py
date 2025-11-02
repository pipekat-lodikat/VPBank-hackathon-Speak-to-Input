#!/usr/bin/env python
"""
Voice Bot Service - Entry Point
Standalone service chỉ chạy Voice Bot (WebRTC, STT, TTS, LLM)
Giao tiếp với Browser Agent Service qua HTTP API
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import voice bot
from src.voice_bot import create_app
from aiohttp import web
from loguru import logger

if __name__ == "__main__":
    logger.info("🎤 Starting Voice Bot Service...")
    logger.info("📡 Service runs on port 7860")
    logger.info("🔗 Connects to Browser Agent Service (port 7863)")
    logger.info("📋 Endpoints:")
    logger.info("   POST   /offer (WebRTC)")
    logger.info("   GET    /ws (WebSocket)")
    
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=7860)

