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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

