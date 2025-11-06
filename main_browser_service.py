#!/usr/bin/env python
"""
Browser Agent Service - Standalone HTTP/WebSocket Server
Lắng nghe requests từ Voice Bot và thực hiện browser automation
"""
import asyncio
import os
import sys
from aiohttp import web
from aiohttp.web import RouteTableDef
from dotenv import load_dotenv
from loguru import logger
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.browser_agent import browser_agent

load_dotenv(override=True)

routes = RouteTableDef()

# No workflow; we call browser_agent directly


@routes.post("/api/execute")
async def execute_workflow(request):
    """
    Execute workflow từ user message
    
    Body:
    {
        "user_message": "full conversation context",
        "session_id": "session_123"
    }
    
    Returns:
    {
        "success": true/false,
        "result": "workflow result message",
        "error": "error message if failed"
    }
    """
    try:
        data = await request.json()
        user_message = data.get("user_message", "")
        session_id = data.get("session_id", "")
        
        if not user_message:
            return web.json_response({
                "success": False,
                "error": "user_message is required"
            }, status=400)
        
        logger.info(f"🚀 Received workflow request for session {session_id}")
        logger.debug(f"   Message length: {len(user_message)} chars")
        
        # Execute directly via browser agent (freeform instruction)
        logger.info(f"🔄 Executing via browser agent...")
        agent_result = await browser_agent.execute_freeform(user_message, session_id=session_id)
        
        # Extract short message to return
        if agent_result.get("success"):
            final_message = agent_result.get("result") or agent_result.get("message") or "Đã xử lý thành công"
        else:
            raise RuntimeError(agent_result.get("error", "Unknown error from browser agent"))
        
        # Filter out empty or invalid responses
        if not final_message or final_message == "No response" or len(final_message.strip()) < 3:
            final_message = "Đã xử lý thành công"
        
        logger.info(f"✅ Workflow completed! Result: {final_message[:200]}...")
        
        return web.json_response({
            "success": True,
            "result": final_message,
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}", exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@routes.get("/api/health")
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "browser-agent-service"
    })


def create_app():
    """Create aiohttp application"""
    app = web.Application()
    app.add_routes(routes)
    
    # Add CORS headers (for frontend)
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            if request.method == 'OPTIONS':
                response = web.Response()
            else:
                response = await handler(request)
            
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        return middleware_handler
    
    app.middlewares.append(cors_middleware)
    return app


if __name__ == "__main__":
    logger.info("🌐 Starting Browser Agent Service...")
    logger.info("📡 Service runs on port 7863")
    logger.info("🔗 Endpoints:")
    logger.info("   POST   /api/execute - Execute workflow")
    logger.info("   GET    /api/health - Health check")
    
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=7863)

