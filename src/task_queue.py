"""
Task Queue System - Decouples Voice Bot from Multi-Agent Workflow
Voice Bot pushes tasks → Queue → Workflow Worker processes
"""
import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from loguru import logger


class TaskType(Enum):
    """Types of tasks that can be processed"""
    LOAN = "loan"
    CRM = "crm"
    HR = "hr"
    COMPLIANCE = "compliance"
    OPERATIONS = "operations"


class TaskStatus(Enum):
    """Task lifecycle states"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """
    Task object representing a form-filling request
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.LOAN
    user_message: str = ""
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "user_message": self.user_message,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskQueue:
    """
    Async task queue for managing form-filling tasks
    Thread-safe queue between Voice Bot and Multi-Agent Workflow
    """
    
    def __init__(self, maxsize: int = 100):
        """
        Initialize task queue
        
        Args:
            maxsize: Maximum queue size (default 100)
        """
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self.tasks: Dict[str, Task] = {}  # Track all tasks by ID
        self._running = False
        logger.info(f"📋 TaskQueue initialized (maxsize={maxsize})")
    
    async def push(self, task: Task) -> str:
        """
        Push a new task to the queue
        
        Args:
            task: Task object to queue
            
        Returns:
            task_id: Unique task identifier
        """
        await self.queue.put(task)
        self.tasks[task.task_id] = task
        logger.info(f"✅ Task pushed to queue: {task.task_id} ({task.task_type.value})")
        logger.debug(f"   Message: {task.user_message[:100]}...")
        logger.debug(f"   Queue size: {self.queue.qsize()}")
        return task.task_id
    
    async def pop(self) -> Optional[Task]:
        """
        Pop next task from queue (blocking)
        
        Returns:
            Task object or None if queue is empty
        """
        try:
            task = await self.queue.get()
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.now()
            logger.info(f"⚡ Task popped from queue: {task.task_id}")
            return task
        except asyncio.CancelledError:
            logger.warning("Task pop cancelled")
            return None
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task object or None if not found
        """
        return self.tasks.get(task_id)
    
    def update_task(self, task_id: str, status: TaskStatus, 
                   result: Optional[str] = None, error: Optional[str] = None):
        """
        Update task status and result
        
        Args:
            task_id: Task identifier
            status: New status
            result: Result message (for completed tasks)
            error: Error message (for failed tasks)
        """
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            task.result = result
            task.error = error
            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.now()
            logger.info(f"📝 Task updated: {task_id} → {status.value}")
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    def get_task_stats(self) -> Dict[str, int]:
        """
        Get task statistics
        
        Returns:
            Dict with counts by status
        """
        stats = {
            "total": len(self.tasks),
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "queue_size": self.queue.qsize()
        }
        
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                stats["pending"] += 1
            elif task.status == TaskStatus.PROCESSING:
                stats["processing"] += 1
            elif task.status == TaskStatus.COMPLETED:
                stats["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                stats["failed"] += 1
        
        return stats
    
    async def clear(self):
        """Clear all tasks (for testing/reset)"""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        self.tasks.clear()
        logger.warning("⚠️  Task queue cleared")


task_queue = TaskQueue(maxsize=100)
