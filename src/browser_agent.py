# browser_agent.py - Browser automation using browser-use Agent

import asyncio
import os
from typing import Optional
from loguru import logger
from browser_use import Agent, Browser
from langchain_aws import ChatBedrock

class BrowserAgentHandler:
    """
    Handles browser automation using browser-use Agent.
    This replaces the old Playwright-based browser_handler.
    """

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.llm = None

    async def start(self):
        """Initialize browser with browser-use"""
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

            # Initialize browser (headless=False to see what's happening)
            self.browser = Browser(
                headless=False,  # Set to True for production
            )

            logger.info("🌐 Browser-use Agent initialized successfully with AWS Bedrock Claude 3.5 Sonnet")

        except Exception as e:
            logger.error(f"Failed to initialize browser-use Agent: {e}")
            raise

    async def navigate_to_sheet(self, sheet_url: str):
        """
        Navigate to Google Sheets URL.
        With browser-use, we can include this as part of the task description.
        """
        try:
            if not self.browser:
                await self.start()

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

    async def run_task(self, task_description: str) -> dict:
        """
        Execute a task using browser-use Agent with natural language description.

        Args:
            task_description: Natural language description of the task to perform

        Returns:
            dict with success status and result information
        """
        try:
            if not self.browser:
                await self.start()

            logger.info(f"🤖 Running browser-use task: {task_description}")

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
                "message": "Task completed successfully"
            }

        except Exception as e:
            logger.error(f"❌ Failed to execute task: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Task failed: {str(e)}"
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
