"""
Workflow Worker - Background service that processes tasks from queue
Continuously polls task queue and executes multi-agent workflow
"""
import asyncio
from typing import Optional
from loguru import logger
from langchain_aws import ChatBedrockConverse

from .task_queue import task_queue, Task, TaskStatus, TaskType
from .multi_agent.graph.builder import build_supervisor_workflow
from .multi_agent.graph.state import MultiAgentState


class WorkflowWorker:
    """
    Background worker that processes tasks from queue
    Runs independently from voice bot pipeline
    """
    
    def __init__(self):
        """Initialize workflow worker"""
        self.running = False
        self.workflow = None
        self.llm = None
        logger.info("🔧 WorkflowWorker initialized")
    
    def _get_llm(self):
        """Lazy load LLM"""
        if self.llm is None:
            import os
            
            model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
            region = os.getenv("AWS_REGION", "us-east-1")
            
            self.llm = ChatBedrockConverse(
                model=model_id,
                region_name=region,
                temperature=0,
                max_tokens=4096,
            )
            logger.info(f"🤖 LLM initialized for workflow worker (model: {model_id}, region: {region})")
        return self.llm
    
    def _get_workflow(self):
        """Lazy load workflow"""
        if self.workflow is None:
            llm = self._get_llm()
            self.workflow = build_supervisor_workflow(llm)
            logger.info("📊 Workflow graph compiled")
        return self.workflow
    
    async def start(self):
        """
        Start the background worker
        Continuously processes tasks from queue
        """
        if self.running:
            logger.warning("⚠️  Worker already running")
            return
        
        self.running = True
        logger.info("🚀 WorkflowWorker started - waiting for tasks...")
        
        try:
            while self.running:
                # Get next task from queue (blocking)
                task = await task_queue.pop()
                
                if task is None:
                    continue
                
                # Process the task
                await self._process_task(task)
                
        except asyncio.CancelledError:
            logger.info("❌ WorkflowWorker cancelled")
        except Exception as e:
            logger.error(f"💥 WorkflowWorker crashed: {e}", exc_info=True)
        finally:
            self.running = False
            logger.info("🛑 WorkflowWorker stopped")
    
    async def _process_task(self, task: Task):
        """
        Process a single task through multi-agent workflow
        
        Args:
            task: Task object to process
        """
        logger.info(f"⚙️  Processing task {task.task_id} ({task.task_type.value})")
        logger.info(f"   Message: {task.user_message}")
        
        try:
            # Get workflow
            workflow = self._get_workflow()
            
            # Create initial state
            initial_state: MultiAgentState = {
                "messages": [
                    ("user", task.user_message)
                ],
                "next": "supervisor",
                "task_id": task.task_id,
                "metadata": {
                    "task_type": task.task_type.value,
                    "created_at": task.created_at.isoformat()
                }
            }
            
            # Execute workflow
            logger.info(f"🔄 Executing workflow for task {task.task_id}")
            result = await workflow.ainvoke(initial_state)
            
            # Extract result
            final_message = result["messages"][-1].content if result["messages"] else "No response"
            
            # Update task status
            task_queue.update_task(
                task.task_id,
                TaskStatus.COMPLETED,
                result=final_message
            )
            
            logger.info(f"✅ Task {task.task_id} completed successfully")
            logger.info(f"   Result: {final_message[:200]}...")
            
            # TODO: Notify voice agent about completion
            # For now, result is stored in task_queue.get_task(task_id).result
            # Voice agent can poll this to speak the result
            
        except Exception as e:
            error_msg = f"Error processing task: {str(e)}"
            logger.error(f"❌ Task {task.task_id} failed: {error_msg}", exc_info=True)
            
            # Update task as failed
            task_queue.update_task(
                task.task_id,
                TaskStatus.FAILED,
                error=error_msg
            )
    
    async def stop(self):
        """Stop the worker gracefully"""
        logger.info("🛑 Stopping WorkflowWorker...")
        self.running = False
    
    def get_stats(self):
        """Get worker statistics"""
        return {
            "running": self.running,
            "workflow_loaded": self.workflow is not None,
            "llm_loaded": self.llm is not None,
            **task_queue.get_task_stats()
        }


# Global worker instance
workflow_worker = WorkflowWorker()


async def start_worker():
    """Start the workflow worker in background"""
    await workflow_worker.start()


def create_worker_task() -> asyncio.Task:
    """
    Create an asyncio task for the worker
    Use this to run worker in background
    
    Returns:
        asyncio.Task object
    """
    task = asyncio.create_task(start_worker())
    logger.info("📦 Worker task created")
    return task
