#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Browser Agent Service - Standalone HTTP/WebSocket Server
Lắng nghe requests từ Voice Bot và thực hiện browser automation

Copyright (c) 2025 Pipekat Lodikat Team
Licensed under the MIT License - see LICENSE file for details
"""
import asyncio
import os
import sys
import time
from aiohttp import web
from aiohttp.web import RouteTableDef
from dotenv import load_dotenv
from loguru import logger
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.browser_agent import browser_agent
from src.env_validator import validate_browser_service_env
from src.input_validator import sanitize_user_message, validate_session_id
from src.exceptions import (
    InvalidInputError,
    BrowserExecutionError,
    ServiceError
)

# Import monitoring
from src.monitoring import (
    initialize_service_info,
    http_requests_total,
    http_request_duration_seconds,
    browser_sessions_total,
    browser_session_duration_seconds,
    browser_form_submissions_total,
    errors_total,
    llm_cache_hits_total,
    llm_cache_misses_total
)
from src.monitoring.middleware import setup_metrics_endpoint

# Import correlation ID logging
from src.utils.logging_config import (
    configure_logging,
    CorrelationIdMiddleware,
    get_correlation_id
)
from src.nlp import extract_structured_instructions

# LLM caching
from src.cost.llm_cache import llm_cache

load_dotenv(override=True)

# Configure logging with correlation IDs
configure_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format_type="detailed",
    enable_file_logging=True,
    log_file_path="logs/browser_agent.log"
)

# Initialize Prometheus metrics
initialize_service_info("browser-agent", "2.0.0")

# Validate required environment variables
validate_browser_service_env()

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
    start_time = time.time()
    request_id = "unknown"
    session_id = "unknown"
    form_type = "unknown"
    
    service_name = "browser-agent"

    try:
        data = await request.json()
        user_message = data.get("user_message", "")
        session_id = data.get("session_id", "")
        request_id = data.get("request_id", "unknown")
        
        # Get correlation ID from logging context
        correlation_id = get_correlation_id()
        logger.info(
            f"📝 Request ID: {request_id} | Correlation ID: {correlation_id} - "
            f"Received request from Voice Bot"
        )

        # Validate and sanitize inputs
        if not user_message:
            errors_total.labels(
                service="browser-agent",
                error_type="validation",
                error_code="MISSING_USER_MESSAGE"
            ).inc()
            
            raise InvalidInputError(
                field="user_message",
                reason="Field is required"
            )

        user_message = sanitize_user_message(user_message)
        if not user_message:
            errors_total.labels(
                service="browser-agent",
                error_type="validation",
                error_code="INVALID_USER_MESSAGE"
            ).inc()
            
            raise InvalidInputError(
                field="user_message",
                reason="Message contains invalid content"
            )

        if session_id and not validate_session_id(session_id):
            errors_total.labels(
                service="browser-agent",
                error_type="validation",
                error_code="INVALID_SESSION_ID"
            ).inc()
            
            raise InvalidInputError(
                field="session_id",
                reason="Invalid format"
            )

        # Detect form type from user message
        msg_lower = user_message.lower()
        if "loan" in msg_lower or "vay" in msg_lower:
            form_type = "loan"
        elif "crm" in msg_lower or "khách hàng" in msg_lower:
            form_type = "crm"
        elif "hr" in msg_lower or "nhân sự" in msg_lower:
            form_type = "hr"
        elif "compliance" in msg_lower or "tuân thủ" in msg_lower:
            form_type = "compliance"
        elif "operations" in msg_lower or "giao dịch" in msg_lower:
            form_type = "operations"

        logger.info(f"🚀 Received workflow request for session {session_id}")
        logger.debug(f"   Message length: {len(user_message)} chars")
        logger.debug(f"   Detected form type: {form_type}")
        
        # Attempt to serve from cache first (reduce GPT-4 browser costs)
        cache_key = f"{form_type}:{user_message}"
        cached_response = llm_cache.get(cache_key, model="browser-agent", temperature=0.0)
        if cached_response:
            llm_cache_hits_total.labels(cache_type="browser_agent").inc()
            logger.info(f"♻️ Cache HIT for request {request_id} (form: {form_type})")
            duration = time.time() - start_time

            http_requests_total.labels(
                service=service_name,
                method="POST",
                endpoint="/api/execute",
                status_code="200"
            ).inc()
            http_request_duration_seconds.labels(
                service=service_name,
                method="POST",
                endpoint="/api/execute"
            ).observe(duration)

            return web.json_response({
                "success": True,
                "result": cached_response,
                "session_id": session_id,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "duration_seconds": round(duration, 2),
                "cached": True
            })

        # Extract structured INSTRUCTION lines and execute deterministic actions first
        cleaned_message, structured_instructions = extract_structured_instructions(user_message)
        instruction_results = []
        effective_session = session_id or "default"

        if structured_instructions:
            logger.info(f"🧭 Structured instructions detected: {structured_instructions}")

            for instruction in structured_instructions:
                action_type = instruction.get("type")
                result = {"success": False, "message": "Session not available"}

                if not effective_session:
                    logger.warning("No session_id provided; skipping structured instruction execution")
                else:
                    try:
                        if action_type == "clear_form":
                            result = await browser_agent.clear_all_fields_incremental(session_id=effective_session)
                        elif action_type == "clear_field":
                            field = instruction.get("field")
                            if field:
                                result = await browser_agent.remove_field_incremental(field_name=field, session_id=effective_session)
                            else:
                                result = {"success": False, "message": "Missing field for clear_field instruction"}
                        elif action_type == "focus_field":
                            field = instruction.get("field")
                            if field:
                                result = await browser_agent.focus_field_incremental(field_name=field, session_id=effective_session)
                            else:
                                result = {"success": False, "message": "Missing field for focus_field instruction"}
                        elif action_type == "read_field":
                            field = instruction.get("field")
                            if field:
                                result = await browser_agent.read_field_value(field_name=field, session_id=effective_session)
                            else:
                                result = {"success": False, "message": "Missing field for read_field instruction"}
                        elif action_type == "summarize_fields":
                            result = await browser_agent.summarize_filled_fields(session_id=effective_session)
                        elif action_type == "navigate_section":
                            section = instruction.get("section")
                            if section:
                                result = await browser_agent.navigate_to_section(section_name=section, session_id=effective_session)
                            else:
                                result = {"success": False, "message": "Missing section for navigate_section instruction"}
                        else:
                            result = {"success": False, "message": f"Unsupported instruction type: {action_type}"}
                    except Exception as exec_err:  # pragma: no cover - defensive logging
                        result = {"success": False, "message": str(exec_err)}
                        logger.error(f"❌ Structured instruction execution failed: {instruction} => {exec_err}")

                instruction_results.append({
                    "instruction": instruction,
                    "result": result
                })

        user_message = cleaned_message

        # If no user message remains after executing structured instructions, return early
        if not user_message:
            duration = time.time() - start_time
            all_successful = all(item["result"].get("success") for item in instruction_results) if instruction_results else True
            instruction_messages = [
                item["result"].get("message")
                for item in instruction_results
                if item["result"].get("message")
            ]
            combined_message = "\n".join(instruction_messages) if instruction_messages else "Structured instructions executed"

            status_code = "200" if all_successful else "500"
            http_requests_total.labels(
                service=service_name,
                method="POST",
                endpoint="/api/execute",
                status_code=status_code
            ).inc()
            http_request_duration_seconds.labels(
                service=service_name,
                method="POST",
                endpoint="/api/execute"
            ).observe(duration)

            if not all_successful:
                errors_total.labels(
                    service=service_name,
                    error_type="instruction",
                    error_code="INSTRUCTION_FAILED"
                ).inc()

            response_payload = {
                "success": all_successful,
                "result": combined_message,
                "instruction_results": instruction_results,
                "session_id": session_id,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "duration_seconds": round(duration, 2)
            }

            status = 200 if all_successful else 500
            return web.json_response(response_payload, status=status)

        # Cache miss -> execute via browser agent (freeform instruction)
        llm_cache_misses_total.labels(cache_type="browser_agent").inc()
        logger.info(f"🔄 Executing via browser agent (cache miss)...")
        agent_result = await browser_agent.execute_freeform(user_message, session_id=session_id)
        
        # Track metrics
        duration = time.time() - start_time
        
        if agent_result.get("success"):
            # Success metrics
            browser_sessions_total.labels(
                status="success",
                form_type=form_type
            ).inc()
            
            browser_session_duration_seconds.labels(
                form_type=form_type
            ).observe(duration)
            
            final_message = agent_result.get("result") or agent_result.get("message") or "Đã xử lý thành công"
            
            # Filter out empty or invalid responses
            if not final_message or final_message == "No response" or len(final_message.strip()) < 3:
                final_message = "Đã xử lý thành công"
            
            logger.info(f"✅ Request ID: {request_id} - Workflow completed! Result: {final_message[:200]}...")
            
            http_requests_total.labels(
                service=service_name,
                method="POST",
                endpoint="/api/execute",
                status_code="200"
            ).inc()
            http_request_duration_seconds.labels(
                service=service_name,
                method="POST",
                endpoint="/api/execute"
            ).observe(duration)

            # Cache successful result for future reuse (temperature 0 for deterministic behavior)
            llm_cache.put(cache_key, final_message, model="browser-agent", temperature=0.0)

            return web.json_response({
                "success": True,
                "result": final_message,
                "session_id": session_id,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "duration_seconds": round(duration, 2),
                "cached": False,
                "instruction_results": instruction_results
            })
        else:
            # Failure metrics
            browser_sessions_total.labels(
                status="failed",
                form_type=form_type
            ).inc()
            
            errors_total.labels(
                service="browser-agent",
                error_type="execution",
                error_code="BROWSER_EXECUTION_FAILED"
            ).inc()
            
            error_msg = agent_result.get("error", "Unknown error from browser agent")
            raise BrowserExecutionError(
                task="form_filling",
                reason=error_msg
            )

    except InvalidInputError as e:
        # Validation errors - 400
        logger.warning(f"⚠️  Validation error: {e.message}")
        return web.json_response(e.to_dict(), status=400)
        
    except BrowserExecutionError as e:
        # Browser execution errors - 500
        logger.error(f"❌ Browser execution error: {e.message}")
        errors_total.labels(
            service="browser-agent",
            error_type="browser",
            error_code=e.error_code
        ).inc()
        return web.json_response({
            "success": False,
            "error": error_msg,
            "session_id": session_id,
            "request_id": request_id,
            "correlation_id": correlation_id,
            "duration_seconds": round(duration, 2),
            "instruction_results": instruction_results
        }, status=500)
        
    except Exception as e:
        # Unexpected errors - 500
        duration = time.time() - start_time
        http_requests_total.labels(
            service=service_name,
            method="POST",
            endpoint="/api/execute",
            status_code="500"
        ).inc()
        http_request_duration_seconds.labels(
            service=service_name,
            method="POST",
            endpoint="/api/execute"
        ).observe(duration)

        logger.error(
            f"❌ Request ID: {request_id} - Unexpected error: {e}",
            exc_info=True
        )
        errors_total.labels(
            service="browser-agent",
            error_type="unexpected",
            error_code="INTERNAL_SERVER_ERROR"
        ).inc()
        
        error = ServiceError(
            message=f"Internal server error: {str(e)}",
            error_code="INTERNAL_SERVER_ERROR",
            details={"request_id": request_id, "session_id": session_id}
        )
        return web.json_response(error.to_dict(), status=500)


@routes.get("/api/health")
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "browser-agent-service"
    })


@routes.get("/api/live")
async def get_live_url(request):
    """Expose current live_url of persistent browser session (if any)."""
    try:
        url = getattr(browser_agent, "live_url", None)

        return web.json_response({
            "live_url": url
        })
    except Exception as e:
        logger.error(f"❌ Failed to get live url: {e}")
        return web.json_response({"live_url": None, "display_name": None, "error": str(e)}, status=500)


def create_app():
    """Create aiohttp application with monitoring and logging"""
    app = web.Application()
    
    # Store service name for metrics middleware
    app['service_name'] = 'browser-agent'
    
    app.add_routes(routes)
    
    # Add Correlation ID middleware (FIRST - to track all requests)
    app.middlewares.append(CorrelationIdMiddleware.middleware)
    
    # Add CORS headers (for frontend)
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            if request.method == 'OPTIONS':
                response = web.Response()
            else:
                response = await handler(request)
            
            # CORS: Allow only specific origins (Voice Bot and Frontend)
            origin = request.headers.get('Origin')
            allowed_origins = {
                'http://localhost:7860',  # Voice Bot (local)
                'http://127.0.0.1:7860',  # Voice Bot (loopback)
                'http://localhost:5173',  # Frontend (local)
                'http://127.0.0.1:5173',  # Frontend (loopback)
            }

            # Add production origin if configured
            prod_origin = os.getenv('ALLOWED_ORIGIN')
            if prod_origin:
                allowed_origins.add(prod_origin)

            if origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                logger.warning(f"Blocked CORS request from unauthorized origin: {origin}")
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:7860'  # Default to Voice Bot

            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Correlation-ID'
            return response
        return middleware_handler
    
    app.middlewares.append(cors_middleware)
    
    # Setup Prometheus metrics endpoint
    setup_metrics_endpoint(app, path="/metrics")
    
    logger.info("✅ Browser Agent application configured with:")
    logger.info("   - Correlation ID tracking")
    logger.info("   - Prometheus metrics (/metrics)")
    logger.info("   - Structured exception handling")
    logger.info("   - CORS protection")
    
    return app


if __name__ == "__main__":
    logger.info("🌐 Starting Browser Agent Service...")
    logger.info("📡 Service runs on port 7863")
    logger.info("🔗 Endpoints:")
    logger.info("   POST   /api/execute - Execute workflow")
    logger.info("   GET    /api/health - Health check")
    logger.info("   GET    /api/live  - Current browser live URL")
    
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=7863)

