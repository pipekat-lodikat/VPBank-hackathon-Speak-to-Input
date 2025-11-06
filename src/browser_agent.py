"""
Browser Agent - Migrated to new browser_use Agent with ChatOpenAI and BrowserProfile
Giữ nguyên API cho multi-agent tools: start_form_session, fill_field_incremental, submit_form_incremental, fill_form
"""
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from browser_use import Agent as BrowserUseAgent
from browser_use import BrowserProfile


load_dotenv(override=True)


SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
"""


class BrowserAgentHandler:
    """Wrapper tương thích multi-agent, dùng Agent(ChatOpenAI, BrowserProfile)."""

    def __init__(self):
        self.sessions: dict[str, dict] = {}
        self.llm = None
        self.browser_profile = None
        logger.info("🌐 BrowserAgentHandler (new) initialized")

    def _get_llm(self):
        """Ensure OPENAI_API_KEY is set; let browser-use auto-configure LLM internally."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY không được tìm thấy trong môi trường")
        # Return None to let BrowserUseAgent pick provider/model from env
        return None

    def _get_profile(self):
        if self.browser_profile is None:
            self.browser_profile = BrowserProfile(
                minimum_wait_page_load_time=0.1,
                wait_between_actions=0.1,
                headless=os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
            )
        return self.browser_profile

    async def start_form_session(self, form_url: str, form_type: str, session_id: str = "default") -> dict:
        try:
            logger.info(f"🚀 Starting form session: {form_type} (session_id: {session_id})")

            if session_id in self.sessions:
                logger.info(f"♻️  Reusing existing session for {session_id}")
                agent = self.sessions[session_id]["agent"]
                agent.add_task(f"Open {form_url} and wait for page to fully load.")
                await agent.run()
                return {"success": True, "message": f"Reusing session for {form_type}", "session": self.sessions[session_id]["session_data"]}

            profile = self._get_profile()

            initial_task = (
                f"Open {form_url} and wait for the form to fully load. Do not submit or fill yet."
            )
            agent = BrowserUseAgent(
                task=initial_task,
                flash_mode=True,
                browser_profile=profile,
                extend_system_message=SPEED_OPTIMIZATION_PROMPT,
            )

            await agent.run()

            session_data = {
                "url": form_url,
                "type": form_type,
                "fields_filled": [],
                "start_time": asyncio.get_event_loop().time(),
                "session_id": session_id,
            }
            self.sessions[session_id] = {"agent": agent, "session_data": session_data}
            return {"success": True, "message": f"Form {form_type} opened successfully", "session": session_data}
        except Exception as e:
            logger.error(f"❌ Error starting session: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def fill_field_incremental(self, field_name: str, value: str, session_id: str = "default") -> dict:
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}

            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]

            if any(f.get("field") == field_name and f.get("value") == value for f in session_data["fields_filled"]):
                return {"success": True, "field": field_name, "value": value, "skipped": True, "message": f"Field {field_name} already has value {value}"}

            filled_fields_info = ", ".join([f"{f['field']}={f['value']}" for f in session_data["fields_filled"]])
            task = f"""
            On the current page, fill only the field with HTML name="{field_name}" with value: {value}.
            Memory: {filled_fields_info if filled_fields_info else 'None'}.
            Verify the field now shows the exact value. Do not submit or navigate.
            """
            agent.add_task(task)
            await agent.run()

            session_data["fields_filled"].append({"field": field_name, "value": value})
            return {"success": True, "field": field_name, "value": value, "fields_filled": len(session_data["fields_filled"]), "message": f"Filled {field_name} = {value}"}
        except Exception as e:
            logger.error(f"❌ Error filling field {field_name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def upsert_field_incremental(self, field_name: str, value: str, session_id: str = "default") -> dict:
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}
            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            task = f"""
            Locate HTML field name="{field_name}" and set/replace its content with: {value}. Verify final value.
            Only modify this field.
            """
            agent.add_task(task)
            await agent.run()
            # upsert memory
            updated = False
            for f in session_data["fields_filled"]:
                if f.get("field") == field_name:
                    f["value"] = value
                    updated = True
                    break
            if not updated:
                session_data["fields_filled"].append({"field": field_name, "value": value})
            return {"success": True, "field": field_name, "value": value, "message": "Field upserted"}
        except Exception as e:
            logger.error(f"❌ Error upserting field {field_name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def remove_field_incremental(self, field_name: str, session_id: str = "default") -> dict:
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}
            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            task = f"""
            Clear the field with HTML name="{field_name}" (empty the input or reset select to placeholder). Verify cleared.
            """
            agent.add_task(task)
            await agent.run()
            session_data["fields_filled"] = [f for f in session_data["fields_filled"] if f.get("field") != field_name]
            return {"success": True, "field": field_name, "message": "Field cleared and removed from memory"}
        except Exception as e:
            logger.error(f"❌ Error removing field {field_name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def remove_fields_incremental(self, field_names: list[str], session_id: str = "default") -> dict:
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}
            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            fields_str = ", ".join(field_names)
            task = f"""
            Clear the following fields by HTML name: {fields_str}. Verify each is empty or reset to placeholder.
            """
            agent.add_task(task)
            await agent.run()
            session_data["fields_filled"] = [f for f in session_data["fields_filled"] if f.get("field") not in set(field_names)]
            return {"success": True, "fields": list(field_names), "message": "Fields cleared and removed from memory"}
        except Exception as e:
            logger.error(f"❌ Error removing fields {field_names}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def clear_all_fields_incremental(self, session_id: str = "default") -> dict:
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}
            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            task = """
            Try clicking a 'Reset/Clear' button to reset the entire form. If not found, clear all visible inputs/selects to default.
            Verify the form is cleared.
            """
            agent.add_task(task)
            await agent.run()
            session_data["fields_filled"] = []
            return {"success": True, "message": "All fields cleared and memory reset"}
        except Exception as e:
            logger.error(f"❌ Error clearing all fields: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def get_filled_fields(self, session_id: str = "default") -> dict:
        if session_id not in self.sessions:
            return {"success": False, "error": f"No active session for {session_id}"}
        session = self.sessions[session_id]
        return {"success": True, "fields": list(session["session_data"].get("fields_filled", []))}

    async def submit_form_incremental(self, session_id: str = "default") -> dict:
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}"}
            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            form_type = session_data.get("type", "loan")
            task = """
            If a submit/send/register button exists, click it, confirm modal if needed, and wait for success. Otherwise stop after filling.
            Provide a short summary of fields filled and submit status.
            """
            agent.add_task(task)
            await agent.run()
            await asyncio.sleep(1)
            await self._close_session(session_id)
            return {"success": True, "message": "Form submitted (or finalized)"}
        except Exception as e:
            logger.error(f"❌ Error submitting form: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def fill_form(self, form_url: str, form_data: dict, form_type: str = "loan") -> dict:
        try:
            profile = self._get_profile()
            fields_desc = "\n".join([f"- {k}: {v}" for k, v in form_data.items()])
            task = f"""
            1. Open {form_url}
            2. Fill the form with the following information:\n{fields_desc}
            3. Verify formats (phone 10 digits, valid email, DOB DD/MM/YYYY or similar)
            4. If a submit button exists, click it; otherwise stop after filling.
            5. Return a short summary of filled fields and submit status.
            """
            agent = BrowserUseAgent(
                task=task,
                flash_mode=True,
                browser_profile=profile,
                extend_system_message=SPEED_OPTIMIZATION_PROMPT,
            )
            result = await agent.run()
            try:
                await agent.browser.close()
            except Exception:
                pass
            return {"success": True, "message": "Form filled successfully", "result": str(result)}
        except Exception as e:
            logger.error(f"❌ Error in one-shot fill: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


    async def execute_freeform(self, user_message: str, session_id: str = "default") -> dict:
        """Nhận một câu lệnh tự do, tự chọn form URL phù hợp, điền và (nếu có) submit.

        Cách tiếp cận: nhét tất cả logic vào 1 task cho Agent (flash_mode) để tối ưu tốc độ.
        """
        try:
            profile = self._get_profile()

            loan_url = os.getenv("LOAN_FORM_URL", "https://vpbank-shared-form-fastdeploy.vercel.app/")
            crm_url = os.getenv("CRM_FORM_URL", "https://case2-ten.vercel.app/")
            hr_url = os.getenv("HR_FORM_URL", "https://case3-seven.vercel.app/")
            compliance_url = os.getenv("COMPLIANCE_FORM_URL", "https://case4-beta.vercel.app/")
            operations_url = os.getenv("OPERATIONS_FORM_URL", "https://case5-chi.vercel.app/")

            task = f"""
            You are a fast web form agent. Follow these rules with maximum speed:
            - Choose the most relevant form URL among:
              - loan: {loan_url}
              - crm: {crm_url}
              - hr: {hr_url}
              - compliance: {compliance_url}
              - operations: {operations_url}
            - Open the chosen URL and wait until form is fully loaded.
            - From the user instruction below, extract the relevant fields and map to HTML field names on page.
            - Fill ONLY the relevant fields. Prefer multi-action sequences.
            - If the instruction clearly asks to submit, click the submit button and confirm if needed; else stop after filling.
            - Return a very short summary of fields filled and submit status.

            USER INSTRUCTION:
            {user_message}
            """

            agent = BrowserUseAgent(
                task=task,
                flash_mode=True,
                browser_profile=profile,
                extend_system_message=SPEED_OPTIMIZATION_PROMPT,
            )

            result = await agent.run()
            try:
                await agent.browser.close()
            except Exception:
                pass
            return {"success": True, "message": "Executed freeform instruction", "result": str(result)}
        except Exception as e:
            logger.error(f"❌ Error executing freeform: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    

# Global instance (single)
browser_agent = BrowserAgentHandler()

