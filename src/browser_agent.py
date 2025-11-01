"""
Browser Agent - VPBank Form Automation
Sử dụng browser-use với 2 modes:
1. One-shot: Điền tất cả fields cùng lúc (legacy)
2. Incremental: Điền từng field qua voice commands liên tục (NEW!)
"""
import asyncio
from browser_use import Agent
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
        
        # Incremental mode (NEW!)
        self.browser = None  # Persistent Browser instance
        self.incremental_agent = None  # Persistent Agent for session
        self.active_session = None  # Current session info
        
        logger.info("🌐 BrowserAgentHandler initialized (supports one-shot & incremental)")
    
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
    
    async def start_form_session(self, form_url: str, form_type: str) -> dict:
        """
        Bắt đầu session điền form incremental
        Mở browser và navigate to form, giữ browser mở
        
        Args:
            form_url: URL của form
            form_type: Loại form (loan/crm/hr/compliance/operations)
            
        Returns:
            Session info
        """
        try:
            logger.info(f"🚀 Starting INCREMENTAL form session: {form_type}")
            
            # Close any existing session
            if self.active_session:
                await self.end_session()
            
            # Create browser instance and navigate to form
            llm = self._get_llm()
            task = f"Navigate to {form_url} and wait for the form to load completely. Do NOT fill anything yet, just wait."
            
            # Create agent - it will create and manage its own browser
            self.incremental_agent = Agent(
                task=task,
                llm=llm,
                use_vision=True,
                max_failures=5,
                max_actions_per_step=10
            )
            
            # Run initial navigation
            await self.incremental_agent.run(max_steps=3)
            
            # Get browser from agent (if accessible)
            # Note: browser-use doesn't expose browser directly, so we'll reuse the agent
            self.browser = getattr(self.incremental_agent, 'browser', None)
            logger.info(f"✅ Form loaded at {form_url}")
            
            # Create session
            self.active_session = {
                "url": form_url,
                "type": form_type,
                "fields_filled": [],
                "start_time": asyncio.get_event_loop().time()
            }
            
            return {
                "success": True,
                "message": f"Đã mở form {form_type}. Bạn có thể bắt đầu điền từng field.",
                "session": self.active_session
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting session: {e}")
            return {"success": False, "error": str(e)}
    
    async def fill_field_incremental(self, field_name: str, value: str) -> dict:
        """
        Điền 1 field cụ thể trong session đang active
        
        Args:
            field_name: Tên field (HTML name attribute)
            value: Giá trị cần điền
            
        Returns:
            Result dict
        """
        try:
            if not self.active_session:
                return {
                    "success": False,
                    "error": "No active session. Call start_form_session() first."
                }
            
            logger.info(f"📝 Filling field incrementally: {field_name} = {value}")
            
            # Create task for this specific field
            task = f"""
                Fill ONLY the field with name="{field_name}" with value: {value}

                Instructions:
                1. Find the input/select/textarea element with name="{field_name}"
                2. Click on it
                3. Fill with value: {value}
                4. Tab away or click outside to confirm
                5. Do NOT fill any other fields
                6. Do NOT click submit

                IMPORTANT: Only fill this ONE field, nothing else!
                """
            
            # Add task to existing agent
            self.incremental_agent.add_new_task(task)
            await self.incremental_agent.run(max_steps=5)
            
            # Track filled field
            self.active_session["fields_filled"].append({
                "field": field_name,
                "value": value
            })
            
            logger.info(f"✅ Field {field_name} filled successfully")
            logger.info(f"📊 Progress: {len(self.active_session['fields_filled'])} fields filled")
            
            return {
                "success": True,
                "field": field_name,
                "value": value,
                "fields_filled": len(self.active_session['fields_filled']),
                "message": f"Đã điền {field_name}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error filling field {field_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def submit_form_incremental(self) -> dict:
        """
        Submit form trong session incremental
        
        Returns:
            Result dict
        """
        try:
            if not self.active_session:
                return {
                    "success": False,
                    "error": "No active session to submit"
                }
            
            logger.info(f"🚀 Submitting form in incremental mode...")
            
            form_type = self.active_session["type"]
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
            
            self.incremental_agent.add_new_task(task)
            await self.incremental_agent.run()
            
            logger.info(f"✅ Form submitted successfully!")
            
            # Wait for confirmation
            await asyncio.sleep(3)
            
            # End session
            result = {
                "success": True,
                "form_type": self.active_session["type"],
                "fields_filled": len(self.active_session["fields_filled"]),
                "message": "Form đã được submit thành công"
            }
            
            await self.end_session()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error submitting form: {e}")
            return {"success": False, "error": str(e)}
    
    async def end_session(self):
        """
        Kết thúc session và đóng browser
        """
        try:
            logger.info("🔒 Closing browser session...")
            
            # Close agent (which will close its browser)
            if self.incremental_agent:
                # Agent manages browser internally, so we just reset references
                self.incremental_agent = None
            
            # Reset session state
            self.browser = None
            self.active_session = None
            
            logger.info("✅ Session ended, browser closed")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
            # Reset anyway
            self.browser = None
            self.incremental_agent = None
            self.active_session = None


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
