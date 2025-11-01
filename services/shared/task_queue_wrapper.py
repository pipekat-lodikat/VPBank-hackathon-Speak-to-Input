"""
Task Queue Wrapper - Supports both in-memory and HTTP API modes
"""
import os
from typing import Optional
from loguru import logger

# Try to import API client
try:
    from services.shared.task_queue_api import TaskQueueAPIClient
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Try to import local queue
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
    from src.task_queue import task_queue as local_task_queue, Task, TaskType, TaskStatus
    LOCAL_AVAILABLE = True
except ImportError:
    LOCAL_AVAILABLE = False


class TaskQueueWrapper:
    """
    Wrapper cho task queue - supports cả local và API mode
    """
    
    def __init__(self):
        """Initialize wrapper - auto-detect mode"""
        use_api = os.getenv("USE_TASK_QUEUE_API", "false").lower() == "true"
        
        if use_api and API_AVAILABLE:
            self.mode = "api"
            self.client = TaskQueueAPIClient()
            logger.info("📡 Using Task Queue API mode")
        elif LOCAL_AVAILABLE:
            self.mode = "local"
            self.queue = local_task_queue
            logger.info("💾 Using local in-memory queue mode")
        else:
            raise RuntimeError("No task queue available!")
    
    async def push_task(self, task_data: dict) -> str:
        """Push task to queue"""
        if self.mode == "api":
            return await self.client.push_task(task_data)
        else:
            # Local mode
            from datetime import datetime
            task = Task(
                task_type=TaskType(task_data.get("task_type", "loan")),
                user_message=task_data.get("user_message", ""),
                session_id=task_data.get("session_id", ""),
                metadata=task_data.get("metadata", {})
            )
            return await self.queue.push(task)
    
    async def pop_task(self):
        """Pop task from queue"""
        if self.mode == "api":
            return await self.client.pop_task()
        else:
            return await self.queue.pop()
    
    async def update_task(self, task_id: str, status: str, result=None, error=None):
        """Update task status"""
        if self.mode == "api":
            await self.client.update_task(task_id, status, result, error)
        else:
            self.queue.update_task(task_id, TaskStatus(status), result, error)
    
    def get_task(self, task_id: str):
        """Get task by ID"""
        if self.mode == "api":
            # Sync call - need to wrap
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
            return loop.run_until_complete(self.client.get_task(task_id))
        else:
            return self.queue.get_task(task_id)
    
    async def close(self):
        """Close connections"""
        if self.mode == "api":
            await self.client.close()


# Global wrapper instance
task_queue_wrapper = TaskQueueWrapper()

