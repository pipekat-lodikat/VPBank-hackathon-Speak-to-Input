"""
Browser Agent - VPBank Form Automation
Sử dụng browser-use với 2 modes:
1. One-shot: Điền tất cả fields cùng lúc (legacy)
2. Incremental: Điền từng field qua voice commands liên tục (NEW!)
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
    Handler cho browser automation với browser-use
    Supports both one-shot and incremental form filling
    """
    
    def __init__(self):
        """Initialize browser agent handler"""
        self.llm = None
        
        # One-shot mode (legacy)
        self.agent = None
        
        # Incremental mode - Session management per session_id
        self.sessions: dict[str, dict] = {}  # session_id -> {browser, agent, session_data}
        
        logger.info("🌐 BrowserAgentHandler initialized (supports one-shot & incremental with session management)")
    
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
            logger.info(f"✅ LLM initialized for browser agent (model: {model_id})")
        return self.llm
    
    async def fill_form(self, form_url: str, form_data: dict, form_type: str = "generic") -> dict:
        """
        Điền form tại URL với data được cung cấp
        
        Args:
            form_url: URL của form cần điền
            form_data: Dict chứa dữ liệu form {field_name: value}
            form_type: Loại form (loan, crm, hr, compliance, operations)
        
        Returns:
            Dict với kết quả execution
        """
        try:
            logger.info(f"🌐 Filling {form_type.upper()} form at: {form_url}")
            logger.info(f"📝 Form data: {form_data}")
            
            # Create task instruction
            task = self._create_task_instruction(form_url, form_data, form_type)
            
            # Initialize agent (browser-use 0.1.40 API)
            llm = self._get_llm()
            agent = Agent(
                task=task,
                llm=llm,
                use_vision=True,  # Use vision model để "nhìn" page tốt hơn
                max_failures=5,  # Retry nhiều hơn cho form phức tạp
                max_actions_per_step=15,  # Nhiều actions hơn per step
                include_attributes=[  # Attributes để extract elements
                    'title', 'type', 'name', 'id', 'role', 'aria-label', 
                    'placeholder', 'value', 'alt', 'data-date-format',
                    'required', 'class'
                ]
            )
            
            # Execute task
            logger.info("🚀 Executing browser task...")
            result = await agent.run()
            
            logger.info(f"✅ Browser agent finished! Result: {result}")
            
            # ⏱️ CRITICAL: Wait additional time to ensure form is submitted
            logger.info("⏳ Waiting 5 seconds to ensure form submission completes...")
            await asyncio.sleep(5)
            
            logger.info(f"✅ Form filling COMPLETE! All steps done.")
            
            return {
                "success": True,
                "form_type": form_type,
                "form_url": form_url,
                "result": str(result),
                "message": f"Form {form_type} đã được điền và submit thành công"
            }
            
        except Exception as e:
            logger.error(f"❌ Error filling form: {e}")
            return {
                "success": False,
                "form_type": form_type,
                "form_url": form_url,
                "error": str(e),
                "message": f"Lỗi khi điền form: {str(e)}"
            }
    
    def _create_task_instruction(self, form_url: str, form_data: dict, form_type: str) -> str:
        """
        Tạo instruction cho browser agent
        """
        # Convert form data to readable format
        data_lines = []
        for key, value in form_data.items():
            if value is not None and value != "":
                data_lines.append(f"  - {key}: {value}")
        
        data_text = "\n".join(data_lines)
        
        # Form-specific submit button hints
        submit_hints = {
            "loan": "Submit button: 'Gửi Đơn'",
            "crm": "Submit button: 'Cập Nhật CRM'",
            "hr": "Submit button: 'Gửi Đơn'",
            "compliance": "Submit button: 'Gửi Báo Cáo'",
            "operations": "Submit button: 'Xác Nhận Kiểm Tra'"
        }
        submit_hint = submit_hints.get(form_type, "Submit button: Look for type='submit'")
        
        task = f"""
Navigate to this form and fill it out accurately:

URL: {form_url}

Form Type: {form_type.upper()}
{submit_hint}

Data to fill:
{data_text}

CRITICAL INSTRUCTIONS FOR DROPDOWNS & DATE FIELDS:

            1. Navigate to URL and wait 3 seconds for page load

            2. For SELECT DROPDOWN fields (gender, loanTerm, loanPurpose, employmentStatus, collateralType):
            STEP 1: Find the <select> element by name attribute
            STEP 2: Click on it to open dropdown
            STEP 3: Wait 1 second
            STEP 4: Find the <option> element with matching value
            STEP 5: Click on that option
            STEP 6: Verify it's selected
            
            Example for gender="male":
            - Find: select[name="gender"]
            - Click to open
            - Find: option[value="male"]
            - Click on it

            3. For DATE field (dateOfBirth, applicationDate):
            ⭐ BEST METHOD - Direct value set (bypasses calendar):
            
            Step 1: Identify the date input field
            - Look for: <input type="date" name="dateOfBirth">
            
            Step 2: Set value directly using these actions in order:
            a) Click on the date field once
            b) Clear any existing value
            c) Type the date in format: YYYY-MM-DD (e.g., "2005-03-15")
            d) Press Tab or click outside to trigger change event
            
            Example: If dateOfBirth="2005-03-15"
            - Find input with name="dateOfBirth"
            - Click it
            - Type exactly: 2005-03-15
            - Tab away
            
            ⚠️ DO NOT try to open calendar picker! Just type the date directly.

            4. For TEXT INPUT fields (name, id, phone, email, address):
            - Click on field
            - Clear any existing value
            - Type the new value

            5. For NUMBER INPUT fields (loanAmount, monthlyIncome, collateralValue):
            - Enter numbers WITHOUT commas
            - Example: 50000000 (not 50,000,000)

            6. For TEXTAREA fields (address, workAddress, notes):
            - Click and type directly

            7. SUBMIT (CRITICAL - Must verify success!):
            STEP 1: Find submit button (multiple possible names):
            - "Gửi Đơn" (Loan form)
            - "Cập Nhật CRM" (CRM form)
            - "Gửi Báo Cáo" (Compliance form)
            - "Xác Nhận Kiểm Tra" (Operations form)
            - OR button with type="submit"
            - Scroll to button if needed
            
            STEP 2: Click the submit button
            - Click once only
            - Wait 2 seconds
            
            STEP 3: Handle confirmation modal (IMPORTANT!):
            - A modal will appear with "Xác Nhận" button
            - Find button with text "Xác Nhận" or class "btn-confirm"
            - Click the "Xác Nhận" button in modal
            - Wait 3 seconds for submission to complete
            
            STEP 4: Verify success:
            - Look for success message or alert
            - Confirm form has been submitted
            - Report completion

            ⚠️ DO NOT report success until:
            - Submit button clicked
            - Confirmation modal handled
            - Success message appears

            TROUBLESHOOTING:
            - If dropdown doesn't open: Click on the select element itself, not the label
            - If date not working: Use JavaScript method (more reliable)
            - If option not found: Check value matches exactly (case-sensitive)
            - If field not found: Try similar names or check HTML structure

            IMPORTANT: 
            - Use JavaScript for date fields to avoid calendar struggles
            - Wait 1-2 seconds between dropdown actions
            - Verify each field is filled before moving to next
            - Do NOT skip any fields with data
            """
        
        return task


    # ============================================
    # INCREMENTAL MODE METHODS (NEW!)
    # ============================================
    
    async def start_form_session(self, form_url: str, form_type: str, session_id: str = "default") -> dict:
        """
        Bắt đầu session điền form incremental
        Mở browser và navigate to form, giữ browser mở
        
        Args:
            form_url: URL của form
            form_type: Loại form (loan/crm/hr/compliance/operations)
            session_id: Session ID để quản lý multiple sessions
            
        Returns:
            Session info
        """
        try:
            logger.info(f"🚀 Starting INCREMENTAL form session: {form_type} (session_id: {session_id})")
            
            # REUSE session nếu đã có cho session_id này
            if session_id in self.sessions:
                existing_session = self.sessions[session_id]
                if existing_session.get("browser") and existing_session.get("agent"):
                    logger.info(f"♻️  Reusing existing session for {session_id}")
                    return {
                        "success": True,
                        "message": f"Đã có session cho {form_type}. Tiếp tục điền field.",
                        "session": existing_session["session_data"]
                    }
            
            # Close session cũ nếu có (same session_id)
            if session_id in self.sessions:
                await self._close_session(session_id)
            
            # Create persistent browser session
            browser_config = BrowserConfig(_force_keep_browser_alive=True)
            browser = Browser(config=browser_config)
            # Browser doesn't need explicit start() - it starts automatically when used
            logger.info(f"✅ Browser initialized (persistent mode) for session {session_id}")
            
            # Create agent với browser_session để giữ browser mở
            llm = self._get_llm()
            task = f"""
Navigate to {form_url} and wait for the form to load completely.

CRITICAL INSTRUCTIONS:
1. Navigate to the form URL
2. Wait for the form to load completely
3. Do NOT click on any fields
4. Do NOT fill any values
5. Do NOT interact with any form elements
6. Just wait and confirm the form is loaded

DO NOT TOUCH ANY FORM FIELDS OR INPUTS - JUST NAVIGATE AND WAIT!
"""
            
            # Lifecycle hook để pause/resume agent khi cần
            async def on_step_start_hook(agent):
                """Hook executed at the beginning of each step"""
                # Check if agent is paused (can be set from outside)
                # If paused, wait for resume signal
                if hasattr(agent, '_paused') and agent._paused:
                    logger.debug(f"Agent paused, waiting for resume...")
                    # Agent will stay paused until resume() is called
                    pass
            
            async def on_step_end_hook(agent):
                """Hook executed at the end of each step"""
                # Log step completion
                logger.debug(f"Step completed for session {session_id}")
                # Check for pending tasks
                if hasattr(agent, '_pending_tasks') and agent._pending_tasks:
                    logger.debug(f"Found {len(agent._pending_tasks)} pending tasks")
            
            incremental_agent = Agent(
                task=task,
                browser_session=browser,
                llm=llm,
                use_vision=True,
                max_failures=5,
                max_actions_per_step=10
            )
            
            # Initialize pause/resume flags
            incremental_agent._paused = False
            incremental_agent._pending_tasks = []
            
            # Run initial navigation với hooks - chỉ navigate, không fill gì
            await incremental_agent.run(
                max_steps=3,
                on_step_start=on_step_start_hook,
                on_step_end=on_step_end_hook
            )
            logger.info(f"✅ Form loaded at {form_url} for session {session_id}")
            
            # Create session data
            session_data = {
                "url": form_url,
                "type": form_type,
                "fields_filled": [],
                "start_time": asyncio.get_event_loop().time(),
                "session_id": session_id
            }
            
            # Store session với helper methods cho pause/resume
            session_obj = {
                "browser": browser,
                "agent": incremental_agent,
                "session_data": session_data
            }
            
            # Add helper methods to session for pause/resume control
            def pause_agent():
                """Pause agent execution"""
                incremental_agent._paused = True
                incremental_agent.pause()
                logger.info(f"⏸️  Agent paused for session {session_id}")
            
            def resume_agent():
                """Resume agent execution"""
                incremental_agent._paused = False
                incremental_agent.resume()
                logger.info(f"▶️  Agent resumed for session {session_id}")
            
            def add_task_to_agent(new_task: str):
                """Add new task to agent queue"""
                incremental_agent.add_new_task(new_task)
                if not hasattr(incremental_agent, '_pending_tasks'):
                    incremental_agent._pending_tasks = []
                incremental_agent._pending_tasks.append(new_task)
                logger.info(f"📝 Added new task to agent queue: {new_task[:50]}...")
            
            session_obj["pause_agent"] = pause_agent
            session_obj["resume_agent"] = resume_agent
            session_obj["add_task"] = add_task_to_agent
            
            self.sessions[session_id] = session_obj
            
            return {
                "success": True,
                "message": f"Đã mở form {form_type}. Bạn có thể bắt đầu điền từng field.",
                "session": session_data
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting session: {e}")
            return {"success": False, "error": str(e)}
    
    async def fill_field_incremental(self, field_name: str, value: str, session_id: str = "default") -> dict:
        """
        Điền 1 field cụ thể trong session
        Sử dụng lifecycle hooks để pause/resume agent khi cần
        
        Args:
            field_name: Tên field (HTML name attribute)
            value: Giá trị cần điền
            session_id: Session ID để lấy đúng session
            
        Returns:
            Result dict
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
            
            # Initialize pause/resume flags if not exists
            if not hasattr(agent, '_paused'):
                agent._paused = False
            if not hasattr(agent, '_pending_tasks'):
                agent._pending_tasks = []
            
            # Check if field already filled in session (avoid duplicate fill)
            already_filled_in_session = any(f["field"] == field_name for f in session_data["fields_filled"])
            
            # Nếu đã fill trong session và giá trị giống nhau → skip
            if already_filled_in_session:
                for f in session_data["fields_filled"]:
                    if f["field"] == field_name:
                        if f["value"] == value:
                            logger.info(f"⚠️  Field {field_name} already filled with same value ({value}), skipping...")
                            return {
                                "success": True,
                                "field": field_name,
                                "value": value,
                                "skipped": True,
                                "fields_filled": len(session_data['fields_filled']),
                                "message": f"Field {field_name} đã có giá trị {value}, không fill lại"
                            }
                        else:
                            logger.info(f"⚠️  Field {field_name} already filled with different value, will update...")
                            # Remove old entry để fill lại với giá trị mới
                            session_data["fields_filled"] = [f for f in session_data["fields_filled"] if f["field"] != field_name]
                            break
            
            logger.info(f"📝 Filling field incrementally: {field_name} = {value} (session: {session_id})")
            logger.debug(f"   Current filled fields: {[f['field'] for f in session_data['fields_filled']]}")
            
            # Create task for this specific field với check giá trị cũ
            task = f"""
Fill ONLY the field with name="{field_name}" with value: {value}

CRITICAL INSTRUCTIONS:
1. Find the input/select/textarea element with name="{field_name}"
2. Check the CURRENT VALUE in that field FIRST:
   - If the field already has a value (not empty):
     * DO NOT click on it
     * DO NOT fill anything
     * DO NOT overwrite the existing value
     * Just report that the field already has a value
   - If the field is EMPTY or has DEFAULT value (like "Nhập...", "Chọn...", placeholder text):
     * Click on the field to select it
     * Clear the field completely (select all and delete)
     * Fill with the new value: {value}
     * Tab away or click outside to confirm
3. Do NOT fill any other fields
4. Do NOT click submit
5. Do NOT interact with any other elements

IMPORTANT RULES:
- NEVER overwrite an existing user-filled value
- ONLY fill if field is empty or has placeholder/default text
- If field already has a value, leave it unchanged

Field to fill: {field_name}
Value to set: {value}
"""
            
            # Lifecycle hooks for field filling
            async def fill_field_step_start(agent):
                """Hook before each step when filling field"""
                # If agent is paused, keep it paused
                if hasattr(agent, '_paused') and agent._paused:
                    logger.debug(f"Agent paused during field fill, waiting...")
            
            async def fill_field_step_end(agent):
                """Hook after each step when filling field"""
                # Log progress
                logger.debug(f"Field fill step completed: {field_name}")
            
            # Pause agent before adding task (if needed for synchronization)
            # Agent will be automatically unpaused when run() is called
            
            # Add task to existing agent
            agent.add_new_task(task)
            
            # Run with hooks to enable pause/resume mechanism
            result = await agent.run(
                max_steps=5,
                on_step_start=fill_field_step_start,
                on_step_end=fill_field_step_end
            )
            
            # Check if agent reported that field already has value
            result_str = str(result).lower() if result else ""
            
            # Check if field was actually filled (not skipped due to existing value)
            was_skipped = any(keyword in result_str for keyword in [
                "already has", "already filled", "existing value", "not empty",
                "leave unchanged", "giá trị cũ", "đã có"
            ])
            
            if was_skipped:
                logger.info(f"⚠️  Field {field_name} already has value, skipped filling")
                return {
                    "success": True,
                    "field": field_name,
                    "value": value,
                    "skipped": True,
                    "fields_filled": len(session_data['fields_filled']),
                    "message": f"Field {field_name} đã có giá trị, không ghi đè"
                }
            
            # Track filled field (only if not already tracked in session)
            if not already_filled_in_session:
                session_data["fields_filled"].append({
                    "field": field_name,
                    "value": value
                })
            
            logger.info(f"✅ Field {field_name} filled successfully with value: {value}")
            logger.info(f"📊 Progress: {len(session_data['fields_filled'])} fields filled")
            
            return {
                "success": True,
                "field": field_name,
                "value": value,
                "fields_filled": len(session_data['fields_filled']),
                "message": f"Đã điền {field_name} = {value}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error filling field {field_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def submit_form_incremental(self, session_id: str = "default") -> dict:
        """
        Submit form trong session incremental và đóng browser sau khi xong
        
        Args:
            session_id: Session ID để lấy đúng session
            
        Returns:
            Result dict
        """
        try:
            if session_id not in self.sessions:
                return {
                    "success": False,
                    "error": f"No active session for {session_id} to submit"
                }
            
            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            
            logger.info(f"🚀 Submitting form in incremental mode... (session: {session_id})")
            
            form_type = session_data["type"]
            submit_buttons = {
                "loan": "Gửi Đơn",
                "crm": "Cập Nhật CRM",
                "hr": "Gửi Đơn",
                "compliance": "Gửi Báo Cáo",
                "operations": "Xác Nhận Kiểm Tra"
            }
            button_text = submit_buttons.get(form_type, "Gửi")
            
            task = f"""
Submit the form:
1. Scroll to bottom of page
2. Find button with text "{button_text}"
3. Click the button
4. Wait for modal to appear
5. Click "Xác Nhận" button in the modal
6. Wait 3 seconds for success message
7. Confirm submission completed
"""
            
            agent.add_new_task(task)
            await agent.run()
            
            logger.info(f"✅ Form submitted successfully!")
            
            # Wait for confirmation
            await asyncio.sleep(3)
            
            # Get result before closing
            result = {
                "success": True,
                "form_type": session_data["type"],
                "fields_filled": len(session_data["fields_filled"]),
                "message": "Form đã được submit thành công"
            }
            
            # Close session after submit
            await self._close_session(session_id)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error submitting form: {e}")
            return {"success": False, "error": str(e)}
    
    async def _close_session(self, session_id: str):
        """
        Đóng browser session cho session_id cụ thể
        """
        try:
            if session_id not in self.sessions:
                return
            
            logger.info(f"🔒 Closing browser session for {session_id}...")
            
            session = self.sessions[session_id]
            browser = session.get("browser")
            
            # Kill browser session
            if browser:
                try:
                    await browser.kill()
                except Exception as e:
                    logger.warning(f"Error killing browser: {e}")
            
            # Remove session
            del self.sessions[session_id]
            
            logger.info(f"✅ Session {session_id} ended, browser closed")
        except Exception as e:
            logger.warning(f"Error closing session {session_id}: {e}")
            # Remove anyway
            if session_id in self.sessions:
                del self.sessions[session_id]
    
    async def end_session(self, session_id: str = "default"):
        """
        Public method để đóng session (wrapper cho _close_session)
        """
        await self._close_session(session_id)
    
    def pause_agent(self, session_id: str = "default"):
        """
        Pause agent execution for a session
        
        Args:
            session_id: Session ID to pause
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if "pause_agent" in session:
                session["pause_agent"]()
            else:
                agent = session["agent"]
                agent._paused = True
                agent.pause()
                logger.info(f"⏸️  Agent paused for session {session_id}")
        else:
            logger.warning(f"Session {session_id} not found for pause")
    
    def resume_agent(self, session_id: str = "default"):
        """
        Resume agent execution for a session
        
        Args:
            session_id: Session ID to resume
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if "resume_agent" in session:
                session["resume_agent"]()
            else:
                agent = session["agent"]
                agent._paused = False
                agent.resume()
                logger.info(f"▶️  Agent resumed for session {session_id}")
        else:
            logger.warning(f"Session {session_id} not found for resume")
    
    def add_task_to_agent(self, session_id: str, new_task: str):
        """
        Add a new task to agent queue for a session
        
        Args:
            session_id: Session ID
            new_task: Task description to add
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if "add_task" in session:
                session["add_task"](new_task)
            else:
                agent = session["agent"]
                agent.add_new_task(new_task)
                logger.info(f"📝 Added new task to agent queue: {new_task[:50]}...")
        else:
            logger.warning(f"Session {session_id} not found for add_task")


# Global instance
browser_agent = BrowserAgentHandler()


# For backward compatibility
async def run_browser_task(task: str) -> dict:
    """
    Run a generic browser task
    
    Args:
        task: Task instruction for the browser
    
    Returns:
        Result dict
    """
    try:
        logger.info(f"🌐 Running browser task: {task[:100]}...")
        
        llm = browser_agent._get_llm()
        agent = Agent(
            task=task,
            llm=llm
        )
        
        result = await agent.run()
        
        return {
            "success": True,
            "result": str(result),
            "message": "Task completed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error running browser task: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Task failed: {str(e)}"
        }
