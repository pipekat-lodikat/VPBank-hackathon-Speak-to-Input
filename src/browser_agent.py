"""
Browser Agent - Simplified version using browser-use official pattern
Now configured to use REAL CHROME browser profile (persist cookies/login).

Env vars (Windows examples):
  - BROWSER_EXECUTABLE_PATH=C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe
  - BROWSER_USER_DATA_DIR=%LOCALAPPDATA%\\Google\\Chrome\\User Data
  - BROWSER_PROFILE_DIR=Default
"""
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from browser_use import Agent, Browser
from langchain_aws import ChatBedrockConverse


load_dotenv(override=True)


def _get_real_browser_kwargs() -> dict:
    """Build kwargs for Browser() to attach a real Chrome profile if provided."""
    executable_path = os.getenv("BROWSER_EXECUTABLE_PATH", "").strip()
    user_data_dir = os.getenv("BROWSER_USER_DATA_DIR", "").strip()
    profile_directory = os.getenv("BROWSER_PROFILE_DIR", "").strip() or "Default"

    kwargs: dict = {}
    if executable_path:
        kwargs["executable_path"] = executable_path
    if user_data_dir:
        kwargs["user_data_dir"] = user_data_dir
    if profile_directory:
        kwargs["profile_directory"] = profile_directory

    if kwargs:
        logger.info(
            "🧩 Using REAL BROWSER profile: exec='{}', user_data='{}', profile='{}'".format(
                kwargs.get("executable_path", "(default)"),
                kwargs.get("user_data_dir", "(default)"),
                kwargs.get("profile_directory", "(default)")
            )
        )
    else:
        logger.warning("⚠️ Real browser paths not set. Running with default browser-use profile.")

    return kwargs


class BrowserAgentHandler:
    """Browser agent with keep-alive session reuse and Agent.add_new_task() pattern."""

    def __init__(self):
        self.llm = None
        self.sessions: dict[str, dict] = {}
        logger.info("🌐 BrowserAgentHandler initialized (real browser enabled if env provided)")

    def _get_llm(self):
        if self.llm is None:
            model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
            self.llm = ChatBedrockConverse(
                model=model_id,
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                temperature=0.1,
                max_tokens=4096,
            )
            logger.info(f"✅ LLM initialized (model: {model_id})")
        return self.llm

    async def start_form_session(self, form_url: str, form_type: str, session_id: str = "default") -> dict:
        """Start or reuse a keep-alive browser session and navigate to form_url."""
        try:
            logger.info(f"🚀 Starting form session: {form_type} (session_id: {session_id})")

            # Reuse existing
            if session_id in self.sessions:
                session = self.sessions[session_id]
                browser = session.get("browser")
                agent = session.get("agent")

                if browser and agent:
                    logger.info(f"♻️  Reusing existing session for {session_id}")
                    nav_task = (
                        f"Navigate to {form_url} if not already there, wait for the page to load completely."
                    )
                    agent.add_new_task(nav_task)
                    await agent.run(max_steps=5)
                    return {
                        "success": True,
                        "message": f"Reusing session for {form_type}",
                        "session": session.get("session_data", {}),
                    }
                else:
                    logger.warning(
                        f"⚠️  Session {session_id} exists but browser/agent missing. Recreating session..."
                    )
                    if session_id in self.sessions:
                        del self.sessions[session_id]

            # Create NEW real browser (auto-starts when Agent uses it)
            browser_kwargs = _get_real_browser_kwargs()
            browser = Browser(**browser_kwargs)
            logger.info("✅ Browser created (keep-alive implied by reuse of Agent + Browser instance)")

            # Create Agent
            llm = self._get_llm()
            initial_task = (
                f"Navigate to {form_url} and wait for the form to load completely. Do NOT fill any fields yet."
            )
            agent = Agent(
                task=initial_task,
                browser=browser,
                llm=llm,
                use_vision=True,
                max_failures=5,
                max_actions_per_step=10,
            )

            logger.info(f"🧭 Navigating to {form_url}...")
            await agent.run(max_steps=10)
            logger.info("✅ Navigation completed - Browser should remain open")

            # Store session
            session_data = {
                "url": form_url,
                "type": form_type,
                "fields_filled": [],
                "start_time": asyncio.get_event_loop().time(),
                "session_id": session_id,
            }
            self.sessions[session_id] = {
                "browser": browser,
                "agent": agent,
                "session_data": session_data,
            }

            return {"success": True, "message": f"Form {form_type} opened successfully", "session": session_data}

        except Exception as e:
            logger.error(f"❌ Error starting session: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def fill_field_incremental(self, field_name: str, value: str, session_id: str = "default") -> dict:
        """Fill a single field using the existing agent/browser session."""
        try:
            if session_id not in self.sessions:
                return {
                    "success": False,
                    "error": f"No active session for {session_id}. Call start_form_session() first.",
                }

            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]

            # Skip if already same value
            if any(
                f.get("field") == field_name and f.get("value") == value
                for f in session_data["fields_filled"]
            ):
                logger.info(f"⚠️  Field {field_name} already filled with {value}, skipping...")
                return {
                    "success": True,
                    "field": field_name,
                    "value": value,
                    "skipped": True,
                    "message": f"Field {field_name} already has value {value}",
                }

            logger.info(f"📝 Filling field: {field_name} = {value}")
            filled_fields_info = ", ".join([f"{f['field']}={f['value']}" for f in session_data["fields_filled"]])

            task = f"""
                Fill the field with name="{field_name}" with value: {value}

                MEMORY CHECK - Fields already filled: {filled_fields_info if filled_fields_info else "None"}

                INSTRUCTIONS:
                1. FIRST, check if field name="{field_name}" is already filled:
                   - If already has value, VERIFY it matches: {value}
                   - If value is different, UPDATE it to: {value}
                   - If field is empty, fill it with: {value}

                2. Find the input/select/textarea element with name="{field_name}" on the page

                3. Check field state:
                   - If field is EMPTY or has placeholder → Fill with: {value}
                   - If field already has a VALUE:
                     * If value = "{value}" → Leave unchanged, report "already filled"
                     * If value ≠ "{value}" → Update to: {value}

                4. VERIFY after filling:
                   - Confirm the field now contains: {value}
                
                5. IMPORTANT:
                   - Do NOT fill any other fields (only {field_name})
                   - Do NOT click submit button
                   - Do NOT navigate away from form

                Field to fill: {field_name}
                Value to set: {value}
            """

            agent.add_new_task(task)
            result = await agent.run(max_steps=5)

            # Track filled field
            session_data["fields_filled"].append({"field": field_name, "value": value})

            return {
                "success": True,
                "field": field_name,
                "value": value,
                "fields_filled": len(session_data["fields_filled"]),
                "message": f"Filled {field_name} = {value}",
            }

        except Exception as e:
            logger.error(f"❌ Error filling field {field_name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def submit_form_incremental(self, session_id: str = "default") -> dict:
        """Submit the form and close the session after success."""
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}"}

            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            form_type = session_data.get("type", "loan")

            submit_buttons = {
                "loan": "Gửi Đơn",
                "crm": "Cập Nhật CRM",
                "hr": "Gửi Đơn",
                "compliance": "Gửi Báo Cáo",
                "operations": "Xác Nhận Kiểm Tra",
            }
            button_text = submit_buttons.get(form_type, "Gửi")

            filled_fields_list = [f['field'] for f in session_data["fields_filled"]]
            filled_fields_info = ", ".join([f"{f['field']}={f['value']}" for f in session_data["fields_filled"]])

            required_fields = {
                "loan": ["customerName", "customerId", "phoneNumber", "email", "loanAmount"],
                "crm": ["customerName", "customerId", "interactionType", "issueDescription"],
                "hr": ["employeeName", "employeeId", "leaveType", "startDate", "endDate"],
                "compliance": ["employeeName", "reportMonth", "violationCount"],
                "operations": ["transactionId", "amount", "customerName"],
            }

            required_for_type = required_fields.get(form_type, [])
            missing_fields = [f for f in required_for_type if f not in filled_fields_list]

            task = f"""
                Submit the form ONLY if all required fields are filled.

                MEMORY - Fields already filled ({len(filled_fields_list)}): {filled_fields_info}
                {'⚠️ MISSING REQUIRED FIELDS: ' + ', '.join(missing_fields) if missing_fields else '✅ All required fields are filled'}

                VERIFICATION BEFORE SUBMIT:
                1. CHECK all required fields are filled:
                   - Required fields: {', '.join(required_for_type) if required_for_type else 'None specified'}
                   - Filled fields: {', '.join(filled_fields_list) if filled_fields_list else 'None'}
                   {'⚠️ DO NOT SUBMIT - Missing fields: ' + ', '.join(missing_fields) if missing_fields else '✅ All required fields present'}

                2. If all required fields are filled:
                   - Click the submit button with text: '{button_text}'
                   - Wait for confirmation modal
                   - Click 'Xác Nhận' or 'OK' in the modal
                   - Wait for success message

                3. If required fields are missing:
                   - DO NOT click submit
                   - Report which fields are missing: {', '.join(missing_fields) if missing_fields else 'None'}

                Form Type: {form_type}
                Submit Button Text: {button_text}
            """

            agent.add_new_task(task)
            await agent.run(max_steps=10)
            await asyncio.sleep(2)
            await self._close_session(session_id)

            return {"success": True, "message": "Form submitted successfully", "fields_filled": len(session_data["fields_filled"]) }

        except Exception as e:
            logger.error(f"❌ Error submitting form: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def fill_form(self, form_url: str, form_data: dict, form_type: str = "loan") -> dict:
        """One-shot: open browser, fill all, then close."""
        try:
            logger.info(f"🚀 Starting ONE-SHOT form fill: {form_type}")

            # Real browser for one-shot as well
            browser_kwargs = _get_real_browser_kwargs()
            browser = Browser(**browser_kwargs)

            llm = self._get_llm()
            task = self._build_one_shot_task(form_url, form_data, form_type)

            agent = Agent(
                task=task,
                browser=browser,
                llm=llm,
                use_vision=True,
                max_failures=5,
                max_actions_per_step=15,
            )

            result = await agent.run(max_steps=50)

            try:
                await browser.kill()
                logger.info("🔒 Browser closed after one-shot fill")
            except Exception:
                pass

            return {"success": True, "message": "Form filled successfully", "result": str(result)}

        except Exception as e:
            logger.error(f"❌ Error in one-shot fill: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _build_one_shot_task(self, form_url: str, form_data: dict, form_type: str) -> str:
        fields_desc = "\n".join([f"- {k}: {v}" for k, v in form_data.items()])
        task = f"""
            Navigate to {form_url} and fill the form with the following information:

            {fields_desc}

            INSTRUCTIONS:
            1. Navigate to {form_url}
            2. Wait for the form to load completely
            3. Fill ALL fields with the provided values
            4. Do NOT submit the form (just fill all fields)
            5. Verify all fields are filled correctly

            Form Type: {form_type}
        """
        return task

    async def _close_session(self, session_id: str):
        try:
            if session_id not in self.sessions:
                return
            session = self.sessions[session_id]
            browser = session.get("browser")
            if browser:
                try:
                    await browser.kill()
                    logger.info(f"🔒 Browser killed for session {session_id}")
                except Exception as e:
                    logger.warning(f"Error killing browser: {e}")
            del self.sessions[session_id]
            logger.info(f"✅ Session {session_id} closed")
        except Exception as e:
            logger.warning(f"Error closing session {session_id}: {e}")
            if session_id in self.sessions:
                del self.sessions[session_id]


# Global instance
browser_agent = BrowserAgentHandler()

"""
Browser Agent - Simplified version based on browser-use official documentation
Simple pattern: Browser with keep_alive + Agent reuse + add_new_task + run
"""
import asyncio
from browser_use import Agent, Browser, BrowserConfig
from langchain_aws import ChatBedrockConverse
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv(override=True)


class BrowserAgentHandler:
    """
    Simplified Browser Agent Handler based on browser-use official pattern
    Pattern: Browser(keep_alive=True) -> Agent(browser=browser) -> add_new_task() -> run()
    """
    
    def __init__(self):
        """Initialize browser agent handler"""
        self.llm = None
        self.sessions: dict[str, dict] = {}  # session_id -> {browser, agent, session_data}
        logger.info("🌐 BrowserAgentHandler initialized (simplified pattern)")
    
    def _get_llm(self):
        """Lazy load LLM"""
        if self.llm is None:
            model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
            self.llm = ChatBedrockConverse(
                model=model_id,
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                temperature=0.1,
                max_tokens=4096
            )
            logger.info(f"✅ LLM initialized (model: {model_id})")
        return self.llm
    
    async def start_form_session(self, form_url: str, form_type: str, session_id: str = "default") -> dict:
        """
        Start form session - Simple pattern from browser-use docs
        Pattern: Browser(keep_alive=True) -> Agent(browser=browser) -> run()
        """
        try:
            logger.info(f"🚀 Starting form session: {form_type} (session_id: {session_id})")
            
            # REUSE existing session if available
            if session_id in self.sessions:
                session = self.sessions[session_id]
                browser = session.get("browser")
                agent = session.get("agent")
                
                if browser and agent:
                    logger.info(f"♻️  Reusing existing session for {session_id}")
                    logger.debug(f"   Browser object: {browser}, Agent object: {agent}")
                    
                    # Check if browser is still alive (for 0.1.40)
                    try:
                        # Try to get browser state to verify it's alive
                        if hasattr(browser, 'is_alive'):
                            if not browser.is_alive():
                                logger.warning(f"⚠️  Browser session {session_id} is dead, creating new one...")
                                # Remove dead session
                                del self.sessions[session_id]
                                # Continue to create new session below
                            else:
                                logger.debug(f"✅ Browser {session_id} is alive, reusing...")
                                # Ensure we're on correct URL by adding navigation task if needed
                                nav_task = f"Navigate to {form_url} if not already there, wait for page to load completely."
                                agent.add_new_task(nav_task)
                                await agent.run(max_steps=5)
                                
                                return {
                                    "success": True,
                                    "message": f"Reusing session for {form_type}",
                                    "session": session.get("session_data", {})
                                }
                    except Exception as e:
                        logger.warning(f"⚠️  Error checking browser state: {e}, creating new session...")
                        # Remove corrupted session
                        if session_id in self.sessions:
                            del self.sessions[session_id]
                        # Continue to create new session below
                else:
                    logger.warning(f"⚠️  Session {session_id} exists but browser/agent is None, creating new one...")
                    # Remove invalid session
                    del self.sessions[session_id]
            
            # Create NEW browser with keep_alive=True (official pattern for 0.1.40)
            # Note: Browser in 0.1.40 auto-starts when Agent uses it, no need for explicit start()
            browser_config = BrowserConfig(_force_keep_browser_alive=True)
            browser = Browser(config=browser_config)
            logger.info(f"✅ Browser created (keep_alive=True, will auto-start with Agent)")
            
            # Create Agent with browser parameter (official pattern)
            llm = self._get_llm()
            initial_task = f"Navigate to {form_url} and wait for the form to load completely. Do NOT fill any fields yet."
            
            agent = Agent(
                task=initial_task,
                browser=browser,  # Pass browser instance
                llm=llm,
                use_vision=True,
                max_failures=5,
                max_actions_per_step=10
            )
            
            # Run initial navigation (official pattern)
            logger.info(f"🧭 Navigating to {form_url}...")
            await agent.run(max_steps=10)
            logger.info(f"✅ Navigation completed - Browser should remain open")
            
            # Store session
            session_data = {
                "url": form_url,
                "type": form_type,
                "fields_filled": [],
                "start_time": asyncio.get_event_loop().time(),
                "session_id": session_id
            }
            
            self.sessions[session_id] = {
                "browser": browser,
                "agent": agent,
                "session_data": session_data
            }
            
            return {
                "success": True,
                "message": f"Form {form_type} opened successfully",
                "session": session_data
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting session: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def fill_field_incremental(self, field_name: str, value: str, session_id: str = "default") -> dict:
        """
        Fill single field - Simple pattern: add_new_task() -> run()
        Official pattern: agent.add_new_task(task) -> agent.run()
        """
        try:
            # Get session
            if session_id not in self.sessions:
                return {
                    "success": False,
                    "error": f"No active session for {session_id}. Call start_form_session() first."
                }
            
            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            form_url = session_data.get("url")
            
            # Check if already filled
            if any(f.get("field") == field_name and f.get("value") == value for f in session_data["fields_filled"]):
                logger.info(f"⚠️  Field {field_name} already filled with {value}, skipping...")
                return {
                    "success": True,
                    "field": field_name,
                    "value": value,
                    "skipped": True,
                    "message": f"Field {field_name} already has value {value}"
                }
            
            logger.info(f"📝 Filling field: {field_name} = {value}")
            
            # Get list of already filled fields for context
            filled_fields_info = ", ".join([f"{f['field']}={f['value']}" for f in session_data["fields_filled"]])
            filled_fields_list = [f['field'] for f in session_data["fields_filled"]]
            
            # Create task with memory check
            task = f"""
                Fill the field with name="{field_name}" with value: {value}
                
                MEMORY CHECK - Fields already filled: {filled_fields_info if filled_fields_info else "None"}
                
                INSTRUCTIONS:
                1. FIRST, check if field name="{field_name}" is already filled:
                   - If already has value, VERIFY it matches: {value}
                   - If value is different, UPDATE it to: {value}
                   - If field is empty, fill it with: {value}
                
                2. Find the input/select/textarea element with name="{field_name}" on the page
                
                3. Check field state:
                   - If field is EMPTY or has placeholder → Fill with: {value}
                   - If field already has a VALUE:
                     * If value = "{value}" → Leave unchanged, report "already filled"
                     * If value ≠ "{value}" → Update to: {value}
                
                4. VERIFY after filling:
                   - Confirm the field now contains: {value}
                   - Take screenshot/verify visually if needed
                
                5. IMPORTANT:
                   - Do NOT fill any other fields (only {field_name})
                   - Do NOT click submit button
                   - Do NOT navigate away from form
                
                Field to fill: {field_name}
                Value to set: {value}
                """
            
            # Verify browser is still alive before adding task
            browser = session.get("browser")
            if not browser:
                return {
                    "success": False,
                    "error": "Browser session lost. Please restart form session."
                }
            
            # Official pattern: add_new_task() -> run()
            # IMPORTANT: Reuse same agent and browser - do NOT create new ones
            agent.add_new_task(task)
            logger.debug(f"📝 Added task: Fill {field_name} (reusing browser session)")
            
            # Run agent (official pattern - reuse same agent and browser)
            # Browser should stay alive after run() completes (keep_alive=True)
            result = await agent.run(max_steps=5)
            logger.debug(f"✅ Agent completed fill task - Browser should still be open")
            
            # Track filled field
            session_data["fields_filled"].append({
                "field": field_name,
                "value": value
            })
            
            return {
                "success": True,
                "field": field_name,
                "value": value,
                "fields_filled": len(session_data["fields_filled"]),
                "message": f"Filled {field_name} = {value}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error filling field {field_name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def submit_form_incremental(self, session_id: str = "default") -> dict:
        """
        Submit form - Simple pattern: add_new_task() -> run() -> close()
        """
        try:
            if session_id not in self.sessions:
                return {
                    "success": False,
                    "error": f"No active session for {session_id}"
                }
            
            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            form_type = session_data.get("type", "loan")
            
            submit_buttons = {
                "loan": "Gửi Đơn",
                "crm": "Cập Nhật CRM",
                "hr": "Gửi Đơn",
                "compliance": "Gửi Báo Cáo",
                "operations": "Xác Nhận Kiểm Tra"
            }
            button_text = submit_buttons.get(form_type, "Gửi")
            
            # Get list of filled fields for verification
            filled_fields_list = [f['field'] for f in session_data["fields_filled"]]
            filled_fields_info = ", ".join([f"{f['field']}={f['value']}" for f in session_data["fields_filled"]])
            
            # Create submit task with field verification
            required_fields = {
                "loan": ["customerName", "customerId", "phoneNumber", "email", "loanAmount"],
                "crm": ["customerName", "customerId", "interactionType", "issueDescription"],
                "hr": ["employeeName", "employeeId", "leaveType", "startDate", "endDate"],
                "compliance": ["employeeName", "reportMonth", "violationCount"],
                "operations": ["transactionId", "amount", "customerName"]
            }
            
            required_for_type = required_fields.get(form_type, [])
            missing_fields = [f for f in required_for_type if f not in filled_fields_list]
            
            # Official pattern: add_new_task() -> run()
            task = f"""
                Submit the form ONLY if all required fields are filled.
                
                MEMORY - Fields already filled ({len(filled_fields_list)}): {filled_fields_info}
                {'⚠️ MISSING REQUIRED FIELDS: ' + ', '.join(missing_fields) if missing_fields else '✅ All required fields are filled'}
                
                VERIFICATION BEFORE SUBMIT:
                1. CHECK all required fields are filled:
                   - Required fields: {', '.join(required_for_type) if required_for_type else 'None specified'}
                   - Filled fields: {', '.join(filled_fields_list) if filled_fields_list else 'None'}
                   {'⚠️ DO NOT SUBMIT - Missing fields: ' + ', '.join(missing_fields) if missing_fields else '✅ All required fields present'}
                
                2. If all required fields are filled:
                   - Click the submit button with text: '{button_text}'
                   - Wait for confirmation modal
                   - Click 'Xác Nhận' or 'OK' in the modal
                   - Wait for success message
                
                3. If required fields are missing:
                   - DO NOT click submit
                   - Report which fields are missing: {', '.join(missing_fields) if missing_fields else 'None'}
                
                Form Type: {form_type}
                Submit Button Text: {button_text}
                """
            
            agent.add_new_task(task)
            
            logger.info(f"🚀 Submitting form... (filled: {len(filled_fields_list)}, missing: {len(missing_fields)})")
            await agent.run(max_steps=10)
            
            # Wait a bit for submit to complete
            await asyncio.sleep(2)
            
            # Close session after submit (only after successful submit)
            await self._close_session(session_id)
            
            return {
                "success": True,
                "message": "Form submitted successfully",
                "fields_filled": len(session_data["fields_filled"])
            }
            
        except Exception as e:
            logger.error(f"❌ Error submitting form: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def fill_form(self, form_url: str, form_data: dict, form_type: str = "loan") -> dict:
        """
        One-shot mode: Fill entire form at once (legacy)
        Pattern: Browser() -> Agent(browser=browser) -> run() -> kill()
        """
        try:
            logger.info(f"🚀 Starting ONE-SHOT form fill: {form_type}")
            
            # Create browser (one-shot, no keep_alive needed)
            browser_config = BrowserConfig()
            browser = Browser(config=browser_config)
            
            # Create task with all form data
            llm = self._get_llm()
            task = self._build_one_shot_task(form_url, form_data, form_type)
            
            # Create Agent
            agent = Agent(
                task=task,
                browser=browser,
                llm=llm,
                use_vision=True,
                max_failures=5,
                max_actions_per_step=15
            )
            
            # Run agent
            logger.info(f"🚀 Executing one-shot form fill...")
            result = await agent.run(max_steps=50)
            
            # Close browser after one-shot
            try:
                await browser.kill()
                logger.info(f"🔒 Browser closed after one-shot fill")
            except:
                pass
            
            return {
                "success": True,
                "message": "Form filled successfully",
                "result": str(result)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in one-shot fill: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _build_one_shot_task(self, form_url: str, form_data: dict, form_type: str) -> str:
        """Build task description for one-shot form filling"""
        fields_desc = "\n".join([f"- {k}: {v}" for k, v in form_data.items()])
        
        task = f"""
            Navigate to {form_url} and fill the form with the following information:

            {fields_desc}

            INSTRUCTIONS:
            1. Navigate to {form_url}
            2. Wait for the form to load completely
            3. Fill ALL fields with the provided values
            4. Do NOT submit the form (just fill all fields)
            5. Verify all fields are filled correctly

            Form Type: {form_type}
            """
        return task
    
    async def _close_session(self, session_id: str):
        """Close browser session"""
        try:
            if session_id not in self.sessions:
                return
            
            session = self.sessions[session_id]
            browser = session.get("browser")
            
            if browser:
                try:
                    await browser.kill()
                    logger.info(f"🔒 Browser killed for session {session_id}")
                except Exception as e:
                    logger.warning(f"Error killing browser: {e}")
            
            del self.sessions[session_id]
            logger.info(f"✅ Session {session_id} closed")
            
        except Exception as e:
            logger.warning(f"Error closing session {session_id}: {e}")
            if session_id in self.sessions:
                del self.sessions[session_id]


# Global instance
browser_agent = BrowserAgentHandler()

