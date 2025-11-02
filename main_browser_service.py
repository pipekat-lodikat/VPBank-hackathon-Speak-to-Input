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
from src.multi_agent.graph.builder import build_supervisor_workflow
from src.multi_agent.graph.state import MultiAgentState
from langchain_aws import ChatBedrockConverse

load_dotenv(override=True)

routes = RouteTableDef()

# Global workflow instance (lazy loaded)
_workflow = None
_llm = None


def get_workflow():
    """Lazy load workflow"""
    global _workflow, _llm
    
    if _workflow is None:
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        
        _llm = ChatBedrockConverse(
            model=model_id,
            region_name=region,
            temperature=0,
            max_tokens=4096,
        )
        
        _workflow = build_supervisor_workflow(_llm)
        logger.info(f"✅ Workflow initialized (model: {model_id})")
    
    return _workflow


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
        
        # Get workflow
        workflow = get_workflow()
        
        # Create initial state
        # Note: user_message chứa TOÀN BỘ conversation history (format: "user: msg1\nuser: msg2\n...")
        # Supervisor sẽ parse TẤT CẢ messages để extract TẤT CẢ fields
        initial_state: MultiAgentState = {
            "messages": [("user", user_message)],  # Full conversation history as single message
            "next": "supervisor",
            "task_id": session_id,
            "metadata": {
                "session_id": session_id,
                "created_at": asyncio.get_event_loop().time(),
                "message_count": len(user_message.split("\n"))  # Count of messages in history
            }
        }
        
        logger.debug(f"   Conversation history contains {len(user_message.split('\n'))} lines")
        logger.debug(f"   Full context length: {len(user_message)} chars")
        
        # Execute workflow
        logger.info(f"🔄 Running workflow...")
        result = await workflow.ainvoke(initial_state)
        
        # Extract result
        final_message = result["messages"][-1].content if result["messages"] else "No response"
        
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
        "service": "browser-agent-service",
        "workflow_loaded": _workflow is not None
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

