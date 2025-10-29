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
                temperature=0.7,
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
                llm=llm
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

URL: {"http://host-form123.s3-website-us-west-2.amazonaws.com/"}

Form Type: {form_type.upper()}

Data to fill:
{data_text}

Instructions:
1. Go to the URL
2. Wait for the page to load completely
3. Find and fill each form field with the corresponding data
4. For date fields, use format dd/mm/yyyy
5. For number fields, enter numbers without commas
6. After filling all fields, click the Submit button
7. Wait for confirmation and report success

IMPORTANT: 
- Fill ALL fields that have data provided
- Do not skip any fields
- Make sure the submit button is clicked
- Verify the form was submitted successfully
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
