# browser_agent.py - Browser automation using browser-use Agent

import asyncio
import os
from typing import Optional
from loguru import logger
from browser_use import Agent, Browser
from langchain_aws import ChatBedrock

class BrowserAgentHandler:
    """
    Handles browser automation using browser-use Agent with lazy initialization.
    Singleton pattern to reuse browser instance across sessions.
    """

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.llm = None
        self._initialized = False
        self._initializing = False
        self._init_lock = asyncio.Lock()

    async def ensure_initialized(self):
        """
        Lazy initialization - only initialize when needed.
        Thread-safe with async lock to prevent multiple initializations.
        """
        if self._initialized:
            return

        async with self._init_lock:
            # Double-check after acquiring lock
            if self._initialized:
                return

            if self._initializing:
                # Another coroutine is initializing, wait for it
                while self._initializing:
                    await asyncio.sleep(0.1)
                return

            self._initializing = True
            try:
                await self._initialize()
                self._initialized = True
                logger.info("✅ Browser agent fully initialized and ready")
            except Exception as e:
                logger.error(f"❌ Failed to initialize browser agent: {e}")
                self._initialized = False
                raise
            finally:
                self._initializing = False

    async def _initialize(self):
        """Internal initialization logic"""
        try:
            # Initialize AWS Bedrock LLM with Claude 3.5 Sonnet
            self.llm = ChatBedrock(
                model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                model_kwargs={
                    "temperature": 0.1,  # Low temperature for more deterministic behavior
                    "max_tokens": 4096
                }
            )
            logger.info("🧠 LLM initialized: AWS Bedrock Claude 3.5 Sonnet")

            # Initialize browser (headless=False to see what's happening)
            self.browser = Browser(
                headless=False,  # Set to True for production
            )
            logger.info("🌐 Browser initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize browser-use components: {e}")
            raise

    async def start(self):
        """
        Legacy method for backward compatibility.
        Use ensure_initialized() instead.
        """
        await self.ensure_initialized()

    async def navigate_to_sheet(self, sheet_url: str):
        """
        Navigate to Google Sheets URL with lazy initialization.
        """
        try:
            # Ensure browser is initialized first
            await self.ensure_initialized()

            # Create a simple agent to navigate
            task = f"Navigate to this URL: {sheet_url} and wait for the page to load completely."

            agent = Agent(
                task=task,
                llm=self.llm,
                browser=self.browser
            )

            result = await agent.run()
            logger.info(f"📊 Navigated to Google Sheets: {sheet_url}")
            logger.info(f"Navigation result: {result}")

        except Exception as e:
            logger.error(f"Failed to navigate to sheet: {e}")
            raise

    async def run_task(self, task_description: str, retry_count: int = 2) -> dict:
        """
        Execute a task using browser-use Agent with natural language description.
        Includes retry logic for robustness.

        Args:
            task_description: Natural language description of the task to perform
            retry_count: Number of retries on failure (default: 2)

        Returns:
            dict with success status and result information
        """
        attempt = 0
        last_error = None

        while attempt <= retry_count:
            try:
                # Ensure browser is initialized
                await self.ensure_initialized()

                logger.info(f"🤖 Running browser-use task (attempt {attempt + 1}/{retry_count + 1}): {task_description}")

                # Create agent with the task using AWS Bedrock LLM
                agent = Agent(
                    task=task_description,
                    llm=self.llm,
                    browser=self.browser
                )

                # Run the agent
                result = await agent.run()

                logger.info(f"✅ Task completed successfully")
                logger.info(f"Result: {result}")

                return {
                    "success": True,
                    "result": result,
                    "message": "Task completed successfully",
                    "attempt": attempt + 1
                }

            except Exception as e:
                last_error = e
                attempt += 1
                logger.warning(f"⚠️ Task attempt {attempt} failed: {e}")

                if attempt <= retry_count:
                    logger.info(f"🔄 Retrying... ({attempt}/{retry_count})")
                    await asyncio.sleep(1)  # Brief delay before retry

        # All retries exhausted
        logger.error(f"❌ Failed to execute task after {retry_count + 1} attempts: {last_error}")
        return {
            "success": False,
            "error": str(last_error),
            "message": f"Task failed after {retry_count + 1} attempts: {str(last_error)}",
            "attempts": retry_count + 1
        }

    async def fill_sheet_row(self, data: dict) -> dict:
        """
        Fill a Google Sheets row with data using natural language task.

        Args:
            data: Dictionary with field names and values to fill

        Returns:
            dict with success status and result
        """
        try:
            # Create a natural language task description in Vietnamese
            task_parts = ["Hãy tìm hàng trống đầu tiên trong Google Sheet hiện tại và điền các thông tin sau:"]

            # Map common field names to Vietnamese
            field_translations = {
                "name": "Tên",
                "email": "Email",
                "phone": "Số điện thoại",
                "address": "Địa chỉ",
                "company": "Công ty",
                "date": "Ngày",
                "notes": "Ghi chú"
            }

            for field_name, field_value in data.items():
                # Translate field name if possible
                display_name = field_translations.get(field_name.lower(), field_name)
                task_parts.append(f"- Cột '{display_name}' (hoặc '{field_name}'): {field_value}")

            task_parts.append("\nSau khi điền xong, hãy nhấn Enter để xác nhận.")

            task_description = "\n".join(task_parts)

            logger.info(f"📝 Task description for filling sheet:\n{task_description}")

            # Execute the task
            result = await self.run_task(task_description)

            if result["success"]:
                logger.info(f"✅ Successfully filled sheet row with {len(data)} fields")
            else:
                logger.error(f"❌ Failed to fill sheet row")

            return result

        except Exception as e:
            logger.error(f"❌ Failed to fill sheet row: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to fill sheet: {str(e)}"
            }

    async def close(self):
        """Close the browser"""
        try:
            if self.browser:
                await self.browser.close()
                logger.info("🔒 Browser closed successfully")
        except Exception as e:
            logger.error(f"Failed to close browser: {e}")

# Global instance
browser_agent = BrowserAgentHandler()
