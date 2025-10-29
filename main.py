#!/usr/bin/env python
"""
Main entry point for the VP Bank Form Filling Voice Agent.
Run this script to start the WebRTC server with Multi-Agent System.
"""

import sys
import os

# Add src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import multi-agent bot (new system)
from src.bot_multi_agent import create_app
from aiohttp import web
from loguru import logger

if __name__ == "__main__":
    logger.info("🚀 Starting VPBank Multi-Agent Bot Server...")
    logger.info("🎯 Multi-agent system: Router + 5 Specialists + Browser Executor")
    logger.info("📋 Supporting 5 use cases: Loan, CRM, HR, Compliance, Operations")
    
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=7860)