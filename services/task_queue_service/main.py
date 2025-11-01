#!/usr/bin/env python
"""
Task Queue Service - HTTP REST API Server
Standalone service để quản lý task queue giữa Voice Bot và Browser Worker
"""
import asyncio
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from aiohttp import web
from aiohttp.web import RouteTableDef
from dotenv import load_dotenv
from loguru import logger

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Import shared task queue
from src.task_queue import TaskQueue, Task, TaskType, TaskStatus

load_dotenv(override=True)

routes = RouteTableDef()

# Global task queue instance
task_queue = TaskQueue(maxsize=100)


@routes.post("/api/tasks/push")
async def push_task(request):
    """Push task to queue"""
    try:
        data = await request.json()
        
        # Create Task object
        task = Task(
            task_id=data.get("task_id") or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            task_type=TaskType(data.get("task_type", "loan")),
            user_message=data.get("user_message", ""),
            session_id=data.get("session_id", ""),
            metadata=data.get("metadata", {})
        )
        
        # Push to queue
        task_id = await task_queue.push(task)
        
        return web.json_response({
            "success": True,
            "task_id": task_id,
            "status": task.status.value
        })
    except Exception as e:
        logger.error(f"Error pushing task: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@routes.get("/api/tasks/pop")
async def pop_task(request):
    """Pop next task from queue (long polling)"""
    try:
        # Get task (blocking, with timeout via asyncio.wait_for)
        try:
            task = await asyncio.wait_for(
                task_queue.pop(),
                timeout=30.0  # Long polling: wait max 30 seconds
            )
            
            if task:
                return web.json_response({
                    "task_id": task.task_id,
                    "task_type": task.task_type.value,
                    "user_message": task.user_message,
                    "session_id": task.session_id,
                    "metadata": task.metadata,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                })
            else:
                return web.Response(status=204)  # No content
        except asyncio.TimeoutError:
            # Timeout after 30 seconds - normal for long polling
            return web.Response(status=204)  # No content
    except Exception as e:
        logger.error(f"Error popping task: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@routes.patch("/api/tasks/{task_id}")
async def update_task(request):
    """Update task status"""
    try:
        task_id = request.match_info["task_id"]
        data = await request.json()
        
        task_queue.update_task(
            task_id,
            TaskStatus(data.get("status")),
            result=data.get("result"),
            error=data.get("error")
        )
        
        return web.json_response({
            "success": True,
            "task_id": task_id
        })
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@routes.get("/api/tasks/{task_id}")
async def get_task(request):
    """Get task by ID"""
    try:
        task_id = request.match_info["task_id"]
        task = task_queue.get_task(task_id)
        
        if task:
            return web.json_response({
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "user_message": task.user_message,
                "session_id": task.session_id,
                "metadata": task.metadata,
                "status": task.status.value,
                "result": task.result,
                "error": task.error,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            })
        else:
            return web.json_response({
                "error": "Task not found"
            }, status=404)
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@routes.get("/api/health")
async def health_check(request):
    """Health check endpoint"""
    stats = task_queue.get_task_stats()
    return web.json_response({
        "status": "healthy",
        "queue_size": stats.get("queue_size", 0),
        "total_tasks": stats.get("total_tasks", 0),
        "pending": stats.get("pending", 0),
        "processing": stats.get("processing", 0),
        "completed": stats.get("completed", 0),
        "failed": stats.get("failed", 0)
    })


def create_app():
    """Create aiohttp application"""
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == "__main__":
    logger.info("🚀 Starting Task Queue Service...")
    logger.info("📡 REST API Server on port 7862")
    logger.info("🔗 Endpoints:")
    logger.info("   POST   /api/tasks/push")
    logger.info("   GET    /api/tasks/pop (long polling)")
    logger.info("   PATCH  /api/tasks/{task_id}")
    logger.info("   GET    /api/tasks/{task_id}")
    logger.info("   GET    /api/health")
    
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=7862)

