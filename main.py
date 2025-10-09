#!/usr/bin/env python
"""
Main entry point for the VP Bank Form Filling Voice Agent.
Run this script to start the WebRTC server.
"""

import sys
import os

# Add src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the form filling bot application
from src.bot_form import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())