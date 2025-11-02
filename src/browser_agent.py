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
                    # Ensure we're on correct URL by adding navigation task if needed
                    nav_task = f"Navigate to {form_url} if not already there, wait for page to load completely."
                    agent.add_new_task(nav_task)
                    await agent.run(max_steps=5)
                    
                    return {
                        "success": True,
                        "message": f"Reusing session for {form_type}",
                        "session": session.get("session_data", {})
                    }
            
            # Create NEW browser with keep_alive=True (official pattern)
            browser_config = BrowserConfig(_force_keep_browser_alive=True)
            browser = Browser(config=browser_config)
            logger.info(f"✅ Browser created (keep_alive=True)")
            
            # Create Agent with browser parameter (official pattern)
            llm = self._get_llm()
            initial_task = f"Navigate to {form_url} and wait for the form to load completely. Do NOT fill any fields yet."
            
            agent = Agent(
                task=initial_task,
                browser=browser,  # Official parameter name
                llm=llm,
                use_vision=True,
                max_failures=5,
                max_actions_per_step=10
            )
            
            # Run initial navigation (official pattern)
            logger.info(f"🧭 Navigating to {form_url}...")
            await agent.run(max_steps=10)
            logger.info(f"✅ Navigation completed")
            
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
            
            # Create task (official pattern)
            task = f"""
                Fill the field with name="{field_name}" with value: {value}

                INSTRUCTIONS:
                1. Find the input/select/textarea element with name="{field_name}"
                2. If field is empty or has placeholder text, fill it with: {value}
                3. If field already has a value, leave it unchanged and report that
                4. Do NOT fill any other fields
                5. Do NOT click submit
                """
            
            # Official pattern: add_new_task() -> run()
            agent.add_new_task(task)
            logger.debug(f"📝 Added task: Fill {field_name}")
            
            # Run agent (official pattern - reuse same agent and browser)
            result = await agent.run(max_steps=5)
            logger.debug(f"✅ Agent completed fill task")
            
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
            
            # Official pattern: add_new_task() -> run()
            task = f"Submit the form by clicking the button with text '{button_text}', then click 'Xác Nhận' in the modal."
            agent.add_new_task(task)
            
            logger.info(f"🚀 Submitting form...")
            await agent.run(max_steps=10)
            
            # Close session after submit
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

