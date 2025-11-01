"""
Shared Task Queue API Client
HTTP REST API client for communication between Voice Bot and Browser Worker
"""
import aiohttp
import asyncio
import os
from typing import Optional, Dict, Any
from loguru import logger
from dataclasses import asdict


class TaskQueueAPIClient:
    """
    HTTP client for task queue API
    Connects to task queue service (Redis-based hoặc HTTP API server)
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize API client
        
        Args:
            base_url: Base URL của task queue service
                     Default: http://localhost:7862 (task queue service)
        """
        self.base_url = base_url or os.getenv(
            "TASK_QUEUE_SERVICE_URL", 
            "http://localhost:7862"
        )
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info(f"📡 TaskQueueAPIClient initialized: {self.base_url}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy load HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def push_task(self, task_data: Dict[str, Any]) -> str:
        """
        Push task to queue via HTTP API
        
        Args:
            task_data: Task data dict (task_type, user_message, session_id, etc.)
            
        Returns:
            task_id: Unique task identifier
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/tasks/push"
        
        try:
            async with session.post(url, json=task_data) as resp:
                resp.raise_for_status()
                result = await resp.json()
                task_id = result.get("task_id")
                logger.info(f"✅ Task pushed via API: {task_id}")
                return task_id
        except Exception as e:
            logger.error(f"❌ Error pushing task via API: {e}")
            raise
    
    async def pop_task(self) -> Optional[Dict[str, Any]]:
        """
        Pop next task from queue (blocking via long polling)
        
        Returns:
            Task dict or None if no task available
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/tasks/pop"
        
        try:
            # Long polling: wait up to 30 seconds
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(url, timeout=timeout) as resp:
                if resp.status == 204:  # No task available
                    return None
                resp.raise_for_status()
                task = await resp.json()
                logger.info(f"⚡ Task popped via API: {task.get('task_id')}")
                return task
        except asyncio.TimeoutError:
            # Timeout is normal for long polling
            return None
        except Exception as e:
            logger.error(f"❌ Error popping task via API: {e}")
            raise
    
    async def update_task(self, task_id: str, status: str, result: Any = None, error: str = None):
        """
        Update task status via HTTP API
        
        Args:
            task_id: Task identifier
            status: New status (pending/processing/completed/failed)
            result: Result data (optional)
            error: Error message (optional)
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/tasks/{task_id}"
        
        payload = {
            "status": status,
            "result": result,
            "error": error
        }
        
        try:
            async with session.patch(url, json=payload) as resp:
                resp.raise_for_status()
                logger.debug(f"✅ Task {task_id} updated: {status}")
        except Exception as e:
            logger.error(f"❌ Error updating task via API: {e}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task by ID via HTTP API
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task dict or None if not found
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/tasks/{task_id}"
        
        try:
            async with session.get(url) as resp:
                if resp.status == 404:
                    return None
                resp.raise_for_status()
                return await resp.json()
        except Exception as e:
            logger.error(f"❌ Error getting task via API: {e}")
            raise


# Global client instance
task_queue_api = TaskQueueAPIClient()


# Import asyncio for timeout
import asyncio

