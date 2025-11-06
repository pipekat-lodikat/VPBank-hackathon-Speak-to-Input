"""
Browser Agent - Migrated to new browser_use Agent with ChatOpenAI and BrowserProfile
Giữ nguyên API cho multi-agent tools: start_form_session, fill_field_incremental, submit_form_incremental, fill_form
"""
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from browser_use import Agent as BrowserUseAgent
from browser_use import Browser, BrowserProfile
from browser_use import sandbox
from browser_use import ChatBrowserUse


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
        self.browser: Browser | None = None
        self.live_url: str | None = None
        logger.info("🌐 BrowserAgentHandler (new) initialized")

    def _get_llm(self):
        """Ensure OPENAI_API_KEY is set; let browser-use auto-configure LLM internally."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY không được tìm thấy trong môi trường")
        # Prefer ChatBrowserUse to avoid provider mismatch
        return ChatBrowserUse()

    def _get_profile(self):
        if self.browser_profile is None:
            self.browser_profile = BrowserProfile(
                minimum_wait_page_load_time=0.2,
                wait_between_actions=0.2,
                headless=os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
            )
        return self.browser_profile

    def _on_browser_created(self, data):
        try:
            self.live_url = getattr(data, "live_url", None)
            if self.live_url:
                logger.info(f"👁️ Live URL: {self.live_url}")
        except Exception:
            pass

    async def _ensure_browser(self):
        """Start a persistent browser (keep_alive) and capture live_url."""
        if self.browser is None:
            headless = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

            @sandbox(on_browser_created=lambda data: self._on_browser_created(data), headless=headless, keep_browser_open=True)
            async def boot(browser: Browser):
                # sandbox sẽ khởi tạo Browser và truyền vào
                return browser

            self.browser = await boot()
            logger.info("🟢 Persistent browser started (keep_alive=True)")
        return self.browser

    async def start_form_session(self, form_url: str, form_type: str, session_id: str = "default") -> dict:
        try:
            logger.info(f"🚀 Starting form session: {form_type} (session_id: {session_id})")

            if session_id in self.sessions:
                logger.info(f"♻️  Reusing existing session for {session_id}")
                agent = self.sessions[session_id]["agent"]
                agent.add_new_task(f"Open {form_url} and wait for page to fully load.")
                await agent.run(max_steps=4)
                return {"success": True, "message": f"Reusing session for {form_type}", "session": self.sessions[session_id]["session_data"]}

            profile = self._get_profile()
            browser = await self._ensure_browser()

            initial_task = (
                f"Open {form_url} and wait for the form to fully load. Do not submit or fill yet."
            )
            agent = BrowserUseAgent(
                task=initial_task,
                flash_mode=True,
                browser_profile=profile,
                extend_system_message=SPEED_OPTIMIZATION_PROMPT,
                browser=browser,
                llm=self._get_llm(),
            )

            await agent.run(max_steps=4)

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
            agent.add_new_task(task)
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
            agent.add_new_task(task)
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
            agent.add_new_task(task)
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
            agent.add_new_task(task)
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
            agent.add_new_task(task)
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
            agent.add_new_task(task)
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
            browser = await self._ensure_browser()
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
                flash_mode=False,
                browser_profile=profile,
                extend_system_message=SPEED_OPTIMIZATION_PROMPT,
                browser=browser,
                llm=self._get_llm(),
            )
            try:
                result = await agent.run(max_steps=12)
            except Exception as e:
                msg = str(e)
                if "No result received from execution" in msg:
                    logger.warning("⚠️ agent.run() returned no result, treating as success (fill_form)")
                    return {"success": True, "message": "Form filled (no textual result)", "result": ""}
                raise
            if result is None or (isinstance(result, str) and not result.strip()):
                return {"success": True, "message": "Form filled (no textual result)", "result": ""}
            return {"success": True, "message": "Form filled successfully", "result": str(result)}
        except Exception as e:
            msg = str(e)
            if "No result received from execution" in msg:
                logger.warning("⚠️ outer: no result, treating as success (fill_form)")
                return {"success": True, "message": "Form filled (no textual result)", "result": ""}
            logger.error(f"❌ Error in one-shot fill: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def execute_freeform(self, user_message: str, session_id: str = "default") -> dict:
        """Thực thi dạng freeform theo cấu trúc @sandbox chuẩn của browser-use.

        - Bọc toàn bộ flow trong một hàm @sandbox(browser) để nhận browser từ cloud runtime
        - Khởi tạo Agent với browser được truyền vào và llm=ChatBrowserUse()
        - Chain: navigate -> fill -> submit -> summarize
        """
        try:
            loan_url = os.getenv("LOAN_FORM_URL", "https://vpbank-shared-form-fastdeploy.vercel.app/")
            crm_url = os.getenv("CRM_FORM_URL", "https://case2-ten.vercel.app/")
            hr_url = os.getenv("HR_FORM_URL", "https://case3-seven.vercel.app/")
            compliance_url = os.getenv("COMPLIANCE_FORM_URL", "https://case4-beta.vercel.app/")
            operations_url = os.getenv("OPERATIONS_FORM_URL", "https://case5-chi.vercel.app/")

            navigate_task = (
                "Decide the most relevant form among these URLs and NAVIGATE to it, then wait until fully loaded. "
                "Do not fill yet.\n"
                f"- loan: {loan_url}\n"
                f"- crm: {crm_url}\n"
                f"- hr: {hr_url}\n"
                f"- compliance: {compliance_url}\n"
                f"- operations: {operations_url}"
            )

            fill_task = (
                "From the user instruction below, extract relevant fields and fill ONLY those fields on the current page.\n"
                "Use multi-action sequences. Do not submit.\n\n"
                "USER INSTRUCTION:\n"
                f"{user_message}"
            )

            submit_task = (
                "If the user instruction clearly asks to submit, click submit and confirm if needed; otherwise skip."
            )
            summarize_task = (
                "Return ONLY a short plain text summary: fields filled and submit status."
            )

            llm_instance = self._get_llm()

            @sandbox(
                on_browser_created=self._on_browser_created,
            )
            async def run_flow(browser: Browser, *, nav: str, fill: str, submit: str, summarize: str, llm):
                agent = BrowserUseAgent(
                    task=nav,
                    flash_mode=False,
                    extend_system_message=SPEED_OPTIMIZATION_PROMPT,
                    browser=browser,
                    llm=llm,
                )

                # Step 1: Navigate
                try:
                    await agent.run(max_steps=8)
                except Exception as e:
                    if "No result received from execution" not in str(e):
                        raise

                # Step 2: Fill
                agent.add_new_task(fill)
                try:
                    await agent.run(max_steps=14)
                except Exception as e:
                    if "No result received from execution" not in str(e):
                        raise

                # Step 3: Submit (conditional)
                agent.add_new_task(submit)
                try:
                    await agent.run(max_steps=6)
                except Exception as e:
                    if "No result received from execution" not in str(e):
                        raise

                # Step 4: Summarize
                agent.add_new_task(summarize)
                return await agent.run(max_steps=4)

            try:
                result = await run_flow(nav=navigate_task, fill=fill_task, submit=submit_task, summarize=summarize_task, llm=llm_instance)
            except Exception as e:
                msg = str(e)
                if "No result received from execution" in msg:
                    logger.warning("⚠️ outer: no result, treating as success (freeform)")
                    return {"success": True, "message": "Executed (no textual result)", "result": ""}
                logger.error(f"❌ Error executing freeform: {e}", exc_info=True)
                return {"success": False, "error": str(e)}

            if result is None or (isinstance(result, str) and not result.strip()):
                return {"success": True, "message": "Executed (no textual result)", "result": ""}
            return {"success": True, "message": "Executed freeform instruction", "result": str(result)}
        except Exception as e:
            msg = str(e)
            if "No result received from execution" in msg:
                logger.warning("⚠️ outer: no result, treating as success (freeform)")
                return {"success": True, "message": "Executed (no textual result)", "result": ""}
            logger.error(f"❌ Error executing freeform: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _close_session(self, session_id: str):
        # Do not kill persistent browser; only forget agent memory for that session.
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global instance (single)
browser_agent = BrowserAgentHandler()

