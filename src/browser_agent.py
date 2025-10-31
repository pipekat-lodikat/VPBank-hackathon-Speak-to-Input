"""
Browser Agent - VPBank Form Automation
Sử dụng browser-use để tự động điền form
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
    """
    
    def __init__(self):
        """Initialize browser agent handler"""
        self.llm = None
        self.agent = None
        logger.info("🌐 BrowserAgentHandler initialized")
    
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
            
            logger.info(f"✅ Form filled successfully! Result: {result}")
            
            return {
                "success": True,
                "form_type": form_type,
                "form_url": form_url,
                "result": str(result),
                "message": f"Form {form_type} đã được điền thành công"
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
        
        task = f"""
            Navigate to this form and fill it out accurately:

            URL: {form_url}

            Form Type: {form_type.upper()}

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

            7. SUBMIT (IMPORTANT - Multiple button names):
            - Scroll to bottom of page
            - Find submit button - Can have different text:
                * "Gửi Đơn" (Loan form)
                * "Cập Nhật CRM" (CRM form)
                * "Gửi Báo Cáo" (Compliance form)
                * "Xác Nhận Kiểm Tra" (Operations form)
                * OR any button with type="submit"
            - Click the submit button
            - Wait 3-5 seconds for confirmation/success message
            - Look for modal or alert confirming submission

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
