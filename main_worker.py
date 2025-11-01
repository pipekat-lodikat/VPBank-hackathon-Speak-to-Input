#!/usr/bin/env python
"""
Browser Worker Service - Entry Point
Standalone service chỉ chạy Browser Worker (workflow + browser automation)
Giao tiếp với Voice Bot qua Task Queue API
"""
import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'shared'))

from loguru import logger
from src.workflow_worker import WorkflowWorker

if __name__ == "__main__":
    logger.info("🔨 Starting Browser Worker Service...")
    logger.info("📡 Service connects to Task Queue Service (port 7862)")
    logger.info("🌐 Runs browser automation workflows")
    
    worker = WorkflowWorker()
    
    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        logger.info("🛑 Browser Worker stopped")

