"""
Request Debouncer and Batcher
Reduces unnecessary API calls by batching and debouncing requests
"""
import asyncio
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger


@dataclass
class DebouncedTask:
    """Represents a debounced task"""
    task_id: str
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    callback: Optional[Callable] = None


class RequestDebouncer:
    """
    Debounces requests to prevent rapid-fire API calls
    
    Example:
        debouncer = RequestDebouncer(delay_seconds=2.0)
        await debouncer.debounce("task-1", data, callback=process_func)
    """
    
    def __init__(self, delay_seconds: float = 2.0):
        """
        Initialize debouncer
        
        Args:
            delay_seconds: Delay before executing task (resets on new call)
        """
        self.delay_seconds = delay_seconds
        self.tasks: Dict[str, DebouncedTask] = {}
        self.timers: Dict[str, asyncio.Task] = {}
        logger.info(f"🕐 RequestDebouncer initialized (delay: {delay_seconds}s)")
    
    async def debounce(
        self,
        task_id: str,
        data: Any,
        callback: Callable,
        *args,
        **kwargs
    ) -> None:
        """
        Debounce a task - only executes after delay_seconds of inactivity
        
        Args:
            task_id: Unique identifier for the task
            data: Data to pass to callback
            callback: Function to call after debounce period
            *args, **kwargs: Additional arguments for callback
        """
        # Cancel existing timer for this task
        if task_id in self.timers:
            self.timers[task_id].cancel()
            logger.debug(f"⏸️  Debounced: Task '{task_id}' reset")
        
        # Store task
        self.tasks[task_id] = DebouncedTask(
            task_id=task_id,
            data=data,
            callback=callback
        )
        
        # Create new timer
        async def execute_after_delay():
            await asyncio.sleep(self.delay_seconds)
            
            # Execute callback
            if task_id in self.tasks:
                task = self.tasks[task_id]
                logger.info(f"✅ Executing debounced task: {task_id}")
                
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(task.data, *args, **kwargs)
                    else:
                        callback(task.data, *args, **kwargs)
                except Exception as e:
                    logger.error(f"❌ Error executing debounced task {task_id}: {e}")
                finally:
                    # Cleanup
                    del self.tasks[task_id]
                    if task_id in self.timers:
                        del self.timers[task_id]
        
        # Start timer
        self.timers[task_id] = asyncio.create_task(execute_after_delay())
    
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a debounced task
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if cancelled, False if not found
        """
        if task_id in self.timers:
            self.timers[task_id].cancel()
            del self.timers[task_id]
            del self.tasks[task_id]
            logger.info(f"🚫 Cancelled debounced task: {task_id}")
            return True
        return False
    
    def cancel_all(self):
        """Cancel all pending tasks"""
        for task_id in list(self.timers.keys()):
            self.cancel(task_id)
        logger.info("🚫 Cancelled all debounced tasks")
    
    def get_pending_count(self) -> int:
        """Get number of pending tasks"""
        return len(self.tasks)


class RequestBatcher:
    """
    Batches multiple requests together and processes them in bulk
    
    Example:
        batcher = RequestBatcher(batch_size=5, timeout_seconds=3.0)
        await batcher.add_request("user-message", callback=process_batch)
    """
    
    def __init__(
        self,
        batch_size: int = 5,
        timeout_seconds: float = 3.0
    ):
        """
        Initialize batcher
        
        Args:
            batch_size: Maximum items per batch
            timeout_seconds: Maximum wait time before processing partial batch
        """
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.batch: List[Any] = []
        self.batch_callbacks: List[Callable] = []
        self.timer: Optional[asyncio.Task] = None
        self.lock = asyncio.Lock()
        logger.info(
            f"📦 RequestBatcher initialized "
            f"(batch_size: {batch_size}, timeout: {timeout_seconds}s)"
        )
    
    async def add_request(
        self,
        data: Any,
        callback: Optional[Callable] = None
    ) -> None:
        """
        Add request to batch
        
        Args:
            data: Request data
            callback: Optional callback for this specific request
        """
        async with self.lock:
            self.batch.append(data)
            if callback:
                self.batch_callbacks.append(callback)
            
            logger.debug(f"📥 Added to batch (current size: {len(self.batch)})")
            
            # Process immediately if batch is full
            if len(self.batch) >= self.batch_size:
                logger.info(f"🔥 Batch full ({self.batch_size} items), processing now")
                await self._process_batch()
            else:
                # Start/restart timer for partial batch
                await self._start_timer()
    
    async def _start_timer(self):
        """Start or restart the batch timeout timer"""
        # Cancel existing timer
        if self.timer and not self.timer.done():
            self.timer.cancel()
        
        # Create new timer
        async def process_after_timeout():
            await asyncio.sleep(self.timeout_seconds)
            async with self.lock:
                if self.batch:
                    logger.info(
                        f"⏰ Batch timeout reached, "
                        f"processing {len(self.batch)} items"
                    )
                    await self._process_batch()
        
        self.timer = asyncio.create_task(process_after_timeout())
    
    async def _process_batch(self):
        """Process current batch"""
        if not self.batch:
            return
        
        # Get current batch
        current_batch = self.batch.copy()
        current_callbacks = self.batch_callbacks.copy()
        
        # Clear batch
        self.batch.clear()
        self.batch_callbacks.clear()
        
        # Cancel timer
        if self.timer and not self.timer.done():
            self.timer.cancel()
            self.timer = None
        
        logger.info(f"🎯 Processing batch of {len(current_batch)} items")
        
        # Execute callbacks
        for idx, callback in enumerate(current_callbacks):
            if callback:
                try:
                    data = current_batch[idx] if idx < len(current_batch) else None
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"❌ Error in batch callback: {e}")
    
    async def flush(self):
        """Force process current batch immediately"""
        async with self.lock:
            if self.batch:
                logger.info(f"🚀 Flushing batch ({len(self.batch)} items)")
                await self._process_batch()
    
    def get_batch_size(self) -> int:
        """Get current batch size"""
        return len(self.batch)


class ThrottledExecutor:
    """
    Throttles function execution to a maximum rate
    
    Example:
        throttler = ThrottledExecutor(max_per_second=5)
        await throttler.execute(expensive_function, arg1, arg2)
    """
    
    def __init__(self, max_per_second: float = 5.0):
        """
        Initialize throttler
        
        Args:
            max_per_second: Maximum executions per second
        """
        self.max_per_second = max_per_second
        self.min_interval = 1.0 / max_per_second
        self.last_execution = 0.0
        self.lock = asyncio.Lock()
        logger.info(f"🚦 ThrottledExecutor initialized (max: {max_per_second}/s)")
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with throttling
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
        """
        async with self.lock:
            # Calculate time to wait
            now = asyncio.get_event_loop().time()
            time_since_last = now - self.last_execution
            
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                logger.debug(f"⏳ Throttling: waiting {wait_time:.3f}s")
                await asyncio.sleep(wait_time)
            
            # Update last execution time
            self.last_execution = asyncio.get_event_loop().time()
        
        # Execute function
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Error in throttled execution: {e}")
            raise

