# browser_agent.py - Browser automation using browser-use Agent

import asyncio
import os
from typing import Optional
from loguru import logger
from browser_use import Agent, Browser
from utils.aws_config import get_bedrock_llm

class BrowserAgentHandler:
    """
    Handles browser automation using browser-use Agent with lazy initialization.
    Singleton pattern to reuse LLM instance.
    """

    def __init__(self):
        self.llm = None
        self._initialized = False
        self._initializing = False
        self._init_lock = asyncio.Lock()

    async def ensure_initialized(self):
        """
        Lazy initialization - only initialize LLM when needed.
        Browser lifecycle is managed by Agent itself.
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
        """Internal initialization logic - only LLM, browser managed by Agent"""
        try:
            # Initialize AWS Bedrock LLM using browser-use native class
            # Use higher temperature for Claude Sonnet 4's action execution
            self.llm = get_bedrock_llm(temperature=0.3)  # Balanced for action + analysis
            logger.info("🧠 LLM initialized: ChatAnthropicBedrock (Claude Sonnet 4)")
            logger.info("🌐 Browser will be managed by Agent (auto-lifecycle)")
            logger.info("🎯 Optimized for Google Sheets interaction")

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
        Navigate to Google Sheets URL.
        Creates Agent instance that manages its own browser.
        """
        try:
            # Ensure LLM is initialized
            await self.ensure_initialized()

            # Create a simple agent to navigate (Agent manages browser lifecycle)
            task = f"Navigate to this URL: {sheet_url} and wait for the page to load completely."

            agent = Agent(
                task=task,
                llm=self.llm,
                # Don't pass browser - let Agent create and manage it
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
        Agent manages its own browser lifecycle.
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
                # Ensure LLM is initialized
                await self.ensure_initialized()

                logger.info(f"🤖 Running browser-use task (attempt {attempt + 1}/{retry_count + 1}): {task_description}")

                # Create agent with the task (Agent manages browser)
                agent = Agent(
                    task=task_description,
                    llm=self.llm,
                    # Don't pass browser - let Agent create and manage it
                )

                # Run the agent with minimal steps for quick execution
                result = await agent.run(max_steps=8)  # Reduced: navigate + 3 fills + submit = ~6 steps

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
                
                # Check for specific model identifier error
                error_str = str(e)
                if "model identifier is invalid" in error_str.lower():
                    logger.error(f"❌ Model identifier error detected: {error_str}")
                    logger.error("💡 This might be a temporary AWS Bedrock issue or region-specific problem")
                    logger.error("   Try switching to a different region or waiting a few minutes")
                    
                logger.warning(f"⚠️ Task attempt {attempt} failed: {e}")

                if attempt <= retry_count:
                    logger.info(f"🔄 Retrying... ({attempt}/{retry_count})")
                    await asyncio.sleep(2)  # Longer delay for model errors

        # All retries exhausted
        logger.error(f"❌ Failed to execute task after {retry_count + 1} attempts: {last_error}")
        return {
            "success": False,
            "error": str(last_error),
            "message": f"Task failed after {retry_count + 1} attempts: {str(last_error)}",
            "attempts": retry_count + 1
        }

    async def fill_form(self, form_url: str, data: dict) -> dict:
        """
        Fill a web form with data using browser-use Agent.
        Specialized for VP Bank form with fields: Họ và tên, CMND/CCCD/Hộ chiếu, Số điện thoại.

        Args:
            form_url: URL of the form to fill
            data: Dictionary with field names and values to fill

        Returns:
            dict with success status and result
        """
        try:
            # Map common field names to Vietnamese form fields
            field_mapping = {
                "name": "Họ và tên",
                "họ và tên": "Họ và tên",
                "full_name": "Họ và tên",
                "id": "CMND/CCCD/Hộ chiếu",
                "id_number": "CMND/CCCD/Hộ chiếu",
                "cmnd": "CMND/CCCD/Hộ chiếu",
                "cccd": "CMND/CCCD/Hộ chiếu",
                "phone": "Số điện thoại",
                "phone_number": "Số điện thoại",
                "số điện thoại": "Số điện thoại"
            }

            # Build task with mapped field names
            form_data_list = []
            for key, value in data.items():
                mapped_key = field_mapping.get(key.lower(), key)
                form_data_list.append(f"  - {mapped_key}: {value}")
            
            form_data_string = "\n".join(form_data_list)

            # Extract values for direct use
            name_value = data.get("name") or data.get("họ và tên") or data.get("full_name") or ""
            id_value = data.get("id") or data.get("cmnd") or data.get("cccd") or data.get("id_number") or ""
            phone_value = data.get("phone") or data.get("số điện thoại") or data.get("phone_number") or ""

            task_description = f"""
Go to {form_url} and fill the form. DO NOT THINK. JUST ACT.

ACTIONS TO EXECUTE IMMEDIATELY:
1. Go to {form_url}
2. Click input field with placeholder "Nhap ho va ten" and type: {name_value}
3. Click input field with placeholder "Nhap so CMND" and type: {id_value}
4. Click input field with placeholder "Nhap so dien thoai" and type: {phone_value}
5. Click the BLUE button "Gui thong tin"
6. Done

DO NOT CREATE FILES. DO NOT PLAN. JUST FILL THE FORM.
FOCUS ON CLICKING AND TYPING ONLY.
"""

            logger.info(f"📋 Filling VP Bank form with {len(data)} fields")
            logger.info(f"🌐 Form URL: {form_url}")
            logger.info(f"📊 Data to fill:\n{form_data_string}")

            result = await self.run_task(task_description, retry_count=2)

            if result["success"]:
                logger.info(f"✅ Successfully filled and submitted form")
                return {
                    "success": True,
                    "result": result["result"],
                    "message": f"Successfully filled form with {len(data)} fields and clicked submit",
                    "data_filled": data
                }
            else:
                logger.error(f"❌ Failed to fill form: {result.get('error')}")
                return result

        except Exception as e:
            logger.error(f"❌ Failed to fill form: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to fill form: {str(e)}"
            }

    async def fill_sheet_row(self, data: dict) -> dict:
        """
        Fill a Google Sheets row with data using optimized task instructions.
        Uses clear, action-focused commands that Claude Sonnet 4 executes well.

        Args:
            data: Dictionary with field names and values to fill

        Returns:
            dict with success status and result
        """
        try:
            # Create action-focused task description that forces Claude to ACT
            data_entries = []
            for field_name, field_value in data.items():
                data_entries.append(f"{field_name}: {field_value}")
            
            data_string = " | ".join(data_entries)
            
            # Use CLEAR, ACTION-FOCUSED instructions (based on successful test)
            task_description = f"""
You are currently viewing a Google Sheets document. CRITICAL: You MUST perform these EXACT actions. Do NOT navigate away or go to other sites.

MANDATORY ACTIONS TO FILL THE CURRENT GOOGLE SHEETS:
1. Find the first completely empty row in the current spreadsheet
2. Click on the first cell of that empty row  
3. Type: {list(data.values())[0]} 
4. Press Tab key to move to next column
5. Type: {list(data.values())[1] if len(data) > 1 else 'N/A'}
6. Press Tab key to move to next column  
7. Type: {list(data.values())[2] if len(data) > 2 else 'N/A'}
8. Press Tab key to move to next column
9. Type: {list(data.values())[3] if len(data) > 3 else 'N/A'}
10. Press Enter to confirm the row

Data to fill: {data_string}

YOU MUST WORK WITH THE CURRENT SPREADSHEET. DO NOT NAVIGATE TO OTHER SITES.
YOU MUST ACTUALLY CLICK AND TYPE. DO NOT JUST DESCRIBE WHAT YOU SEE.
PERFORM THE ACTIONS ABOVE STEP BY STEP ON THE LOADED SHEET.
"""

            logger.info(f"📝 Action-focused task for filling sheet with {len(data)} fields")
            logger.info(f"📊 Data to fill: {data_string}")

            # Execute with reduced steps for efficiency
            result = await self.run_task(task_description, retry_count=1)

            if result["success"]:
                logger.info(f"✅ Successfully filled sheet row with {len(data)} fields")
                return {
                    "success": True,
                    "result": result["result"],
                    "message": f"Successfully filled sheet with {len(data)} fields",
                    "data_filled": data
                }
            else:
                logger.error(f"❌ Failed to fill sheet row - trying simplified approach")
                
                # Fallback: Very simple single-field approach
                first_value = list(data.values())[0] if data else "Test Data"
                simple_task = f"""
SIMPLE TASK: 
1. Click on any empty cell in the Google Sheet
2. Type: {first_value}
3. Press Enter
4. Done.
"""
                
                logger.info(f"� Trying simplified approach with first value: {first_value}")
                fallback_result = await self.run_task(simple_task, retry_count=1)
                
                if fallback_result["success"]:
                    logger.info(f"✅ Fallback approach succeeded")
                    return {
                        "success": True,
                        "result": fallback_result["result"],
                        "message": "Successfully filled sheet with simplified approach",
                        "fallback_used": True,
                        "data_filled": {list(data.keys())[0]: first_value}
                    }
                else:
                    return result  # Return original error

        except Exception as e:
            logger.error(f"❌ Failed to fill sheet row: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to fill sheet: {str(e)}"
            }

    async def close(self):
        """Browser lifecycle managed by Agent - no manual close needed"""
        logger.info("🔒 Browser lifecycle managed by Agent automatically")

# Global instance
browser_agent = BrowserAgentHandler()
