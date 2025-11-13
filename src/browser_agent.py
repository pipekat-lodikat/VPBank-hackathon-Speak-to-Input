# -*- coding: utf-8 -*-
"""
Browser Agent - Migrated to new browser_use Agent with ChatOpenAI and BrowserProfile
Giữ nguyên API cho multi-agent tools: start_form_session, fill_field_incremental, submit_form_incremental, fill_form

Copyright (c) 2025 Pipekat Lodikat Team
Licensed under the MIT License - see LICENSE file for details
"""
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger
from langsmith import traceable

from browser_use import Agent as BrowserUseAgent
from browser_use import Browser
from langchain_openai import ChatOpenAI
from playwright.async_api import async_playwright


load_dotenv(override=True)

# Enable LangSmith tracing
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "browser-agent")


SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps

CRITICAL SUBMISSION RULE:
- NEVER click submit/confirm/send buttons UNLESS the user explicitly requests it
- Only fill forms and verify fields, then STOP
- Submit ONLY when user message contains explicit keywords: 'submit', 'gửi', 'đăng ký', 'xác nhận', 'hoàn tất', 'nộp'
"""


class BrowserAgentHandler:
    """Wrapper tương thích multi-agent, dùng Agent(ChatOpenAI, BrowserProfile)."""

    def __init__(self):
        self.sessions: dict[str, dict] = {}
        self.llm = None
        self.browser: Browser | None = None
        logger.info("🌐 BrowserAgentHandler initialized")

    def _get_llm(self):
        """Get ChatOpenAI instance for browser-use Agent."""
        if self.llm is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        return self.llm

    async def _ensure_browser(self):
        """Start a persistent browser instance."""
        if self.browser is None:
            headless = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
            self.browser = Browser(
                config={
                    "headless": headless,
                    "disable_security": True,
                }
            )
            logger.info("🟢 Persistent browser started")
        return self.browser

    @traceable(name="start_form_session")
    async def start_form_session(self, form_url: str, form_type: str, session_id: str = "default") -> dict:
        try:
            logger.info(f"🚀 Starting form session: {form_type} (session_id: {session_id})")

            if session_id in self.sessions:
                logger.info(f"♻️  Reusing existing session for {session_id}")
                agent = self.sessions[session_id]["agent"]
                agent.add_new_task(f"Open {form_url} and wait for page to fully load.")
                await agent.run(max_steps=4)
                return {"success": True, "message": f"Reusing session for {form_type}", "session": self.sessions[session_id]["session_data"]}

            browser = await self._ensure_browser()
            llm = self._get_llm()
            
            initial_task = (
                f"Open {form_url} and wait for the form to fully load. Do not submit or fill yet."
            )
            agent = BrowserUseAgent(
                task=initial_task,
                llm=llm,
                browser=browser,
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

    @traceable(name="fill_field_incremental")
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

    async def fill_fields_parallel(self, fields: dict[str, str], session_id: str = "default") -> dict:
        """
        Fill multiple form fields in parallel for better performance

        Args:
            fields: Dictionary of {field_name: value}
            session_id: Session identifier

        Returns:
            dict with success status and results
        """
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}

            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]

            # Filter out already-filled fields with same values
            fields_to_fill = {
                k: v for k, v in fields.items()
                if not any(f.get("field") == k and f.get("value") == v for f in session_data["fields_filled"])
            }

            if not fields_to_fill:
                return {"success": True, "message": "All fields already filled with requested values", "skipped": True}

            # Build multi-field task for parallel execution
            fields_desc = "\n".join([f"- {k}: {v}" for k, v in fields_to_fill.items()])
            filled_fields_info = ", ".join([f"{f['field']}={f['value']}" for f in session_data["fields_filled"]])

            task = f"""
            On the current page, fill the following fields in a single pass (use multi-action sequences):
            {fields_desc}

            Memory (already filled): {filled_fields_info if filled_fields_info else 'None'}.

            Verify all fields show the exact values. Do not submit or navigate.
            """

            logger.info(f"🚀 Parallel filling {len(fields_to_fill)} fields: {list(fields_to_fill.keys())}")

            agent.add_new_task(task)
            await agent.run()

            # Update session data
            for field_name, value in fields_to_fill.items():
                session_data["fields_filled"].append({"field": field_name, "value": value})

            return {
                "success": True,
                "fields": fields_to_fill,
                "fields_count": len(fields_to_fill),
                "total_filled": len(session_data["fields_filled"]),
                "message": f"Filled {len(fields_to_fill)} fields in parallel"
            }
        except Exception as e:
            logger.error(f"❌ Error filling fields in parallel: {e}", exc_info=True)
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

    async def focus_field_incremental(self, field_name: str, session_id: str = "default") -> dict:
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}
            session = self.sessions[session_id]
            agent = session["agent"]
            task = f"""
            Scroll to and focus/highlight the field with HTML name or label matching "{field_name}".
            If inside a collapsed section, expand it first. Do not modify values.
            Acknowledge once the field is visible and focused.
            """
            agent.add_new_task(task)
            await agent.run(max_steps=3)
            return {"success": True, "field": field_name, "message": f"Focused field {field_name}"}
        except Exception as e:
            logger.error(f"❌ Error focusing field {field_name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def navigate_to_section(self, section_name: str, session_id: str = "default") -> dict:
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}
            session = self.sessions[session_id]
            agent = session["agent"]
            task = f"""
            Locate the section or accordion that corresponds to "{section_name}" (match heading, label, or aria-label ignoring accents).
            Expand or scroll to it so it is visible and ready for input. Do not submit or modify fields.
            Confirm the section is in view.
            """
            agent.add_new_task(task)
            await agent.run(max_steps=3)
            return {"success": True, "section": section_name, "message": f"Navigated to section {section_name}"}
        except Exception as e:
            logger.error(f"❌ Error navigating to section {section_name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def summarize_filled_fields(self, session_id: str = "default") -> dict:
        if session_id not in self.sessions:
            return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}

        session = self.sessions[session_id]
        fields = session["session_data"].get("fields_filled", [])

        if not fields:
            message = "Chưa có trường nào được điền."
        else:
            summary_lines = [
                f"- {item['field']}: {item['value']}" for item in fields
            ]
            message = "Tôi đã điền các trường sau:\n" + "\n".join(summary_lines)

        return {
            "success": True,
            "fields": list(fields),
            "message": message
        }

    async def read_field_value(self, field_name: str, session_id: str = "default") -> dict:
        if session_id not in self.sessions:
            return {"success": False, "error": f"No active session for {session_id}. Call start_form_session() first."}

        session = self.sessions[session_id]
        fields = session["session_data"].get("fields_filled", [])
        stored = next((f for f in fields if f.get("field") == field_name), None)

        if stored:
            message = f"Trường {field_name} hiện đang có giá trị: {stored['value']}"
            return {"success": True, "field": field_name, "value": stored["value"], "message": message}

        return {
            "success": False,
            "field": field_name,
            "message": f"Chưa có giá trị nào được lưu cho trường {field_name}"
        }

    def get_filled_fields(self, session_id: str = "default") -> dict:
        if session_id not in self.sessions:
            return {"success": False, "error": f"No active session for {session_id}"}
        session = self.sessions[session_id]
        return {"success": True, "fields": list(session["session_data"].get("fields_filled", []))}

    @traceable(name="submit_form_incremental")
    async def submit_form_incremental(self, session_id: str = "default") -> dict:
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": f"No active session for {session_id}"}
            session = self.sessions[session_id]
            agent = session["agent"]
            session_data = session["session_data"]
            form_type = session_data.get("type", "loan")
            task = """
            IMPORTANT: This is an EXPLICIT user request to submit the form.
            Click the submit/send/register button, confirm any modal if needed, and wait for success message.
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

    @traceable(name="fill_form")
    async def fill_form(self, form_url: str, form_data: dict, form_type: str = "loan") -> dict:
        try:
            profile = self._get_profile()
            browser = await self._ensure_browser()
            fields_desc = "\n".join([f"- {k}: {v}" for k, v in form_data.items()])
            task = f"""
            1. Open {form_url}
            2. Fill the form with the following information:\n{fields_desc}
            3. Verify formats (phone 10 digits, valid email, DOB DD/MM/YYYY or similar)
            4. STOP after filling. DO NOT click submit button unless explicitly requested.
            5. Return a short summary of filled fields.
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

    @traceable(name="execute_freeform")
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

            # Create a single comprehensive task to avoid session clearing between steps
            comprehensive_task = (
                "You need to complete a form filling workflow. Follow these steps in order:\n\n"
                "STEP 1 - NAVIGATE:\n"
                "⚠️ CRITICAL: If the USER INSTRUCTION mentions multiple forms, select the FIRST MENTIONED form (chronological order), NOT the last.\n"
                "Analyze the USER INSTRUCTION to identify which form type is requested:\n"
                f"- loan (Đơn vay vốn / KYC / vay tiền): {loan_url}\n"
                f"- crm (CRM / khách hàng / customer): {crm_url}\n"
                f"- hr (HR / nhân sự / nghỉ phép / leave request): {hr_url}\n"
                f"- compliance (Tuân thủ / AML / báo cáo / compliance): {compliance_url}\n"
                f"- operations (Giao dịch / transaction / kiểm tra): {operations_url}\n\n"
                "Keywords mapping:\n"
                "- 'CRM', 'khách hàng', 'customer' → crm\n"
                "- 'HR', 'nhân sự', 'nghỉ phép', 'đơn nghỉ' → hr\n"
                "- 'vay', 'loan', 'KYC' → loan\n"
                "- 'tuân thủ', 'AML', 'báo cáo' → compliance\n"
                "- 'giao dịch', 'transaction', 'kiểm tra' → operations\n\n"
                "Select the form URL that matches the FIRST form keyword found in the USER INSTRUCTION, then NAVIGATE to it and wait until fully loaded.\n\n"
                "STEP 2 - FILL FORM:\n"
                "From the USER INSTRUCTION below, extract only the fields relevant to the current page and FILL THEM.\n"
                "IMPORTANT form mapping guidelines (Vietnamese labels):\n"
                "- 'Họ và tên' -> full name\n"
                "- 'Số điện thoại' or 'Điện thoại' -> phone (10 digits, starts with 0 or 84)\n"
                "- 'Email' -> email\n"
                "- 'Ngày sinh' -> date of birth (accept DD/MM/YYYY)\n"
                "- 'CMND/CCCD' -> national id\n"
                "- 'Tỉnh/Thành phố' -> province/city (select)\n"
                "- 'Khoản vay' or 'Số tiền vay' -> loan amount (numbers only)\n"
                "- 'Kỳ hạn' or 'Thời hạn vay' -> term\n"
                "Filling strategy (use multi-action sequences):\n"
                "1) First try matching by <label> text (contains/equals ignoring accents and case).\n"
                "2) Fallback to placeholder text contains Vietnamese label.\n"
                "3) As last resort, match by input/select name/id containing normalized keywords (e.g., name, phone, email, dob, amount, term).\n"
                "4) Verify each field after filling (value or selection reflects the intended value).\n\n"
                "STEP 3 - SUBMIT CHECK:\n"
                "⚠️ CRITICAL RULE: ONLY click submit if the USER INSTRUCTION contains explicit keywords requesting submission.\n"
                "Examples of explicit submit requests: 'submit', 'gửi', 'đăng ký', 'xác nhận', 'hoàn tất', 'nộp'.\n"
                "If the user instruction ONLY asks to fill fields WITHOUT these keywords, DO NOT CLICK SUBMIT.\n"
                "Just STOP after filling and verifying.\n\n"
                "STEP 4 - SUMMARIZE:\n"
                "At the end, return ONLY a short plain text summary: fields filled and whether form was submitted.\n\n"
                "USER INSTRUCTION:\n"
                f"{user_message}\n\n"
                "IMPORTANT: Complete all steps in sequence. Do not stop after navigation. Fill the form fields based on the user instruction."
            )

            llm_instance = self._get_llm()
            browser = await self._ensure_browser()

            # Use a single agent with one comprehensive task
            agent = BrowserUseAgent(
                task=comprehensive_task,
                llm=llm_instance,
                browser=browser,
            )
            
            try:
                result = await agent.run(max_steps=40)
                if result is None or (isinstance(result, str) and not result.strip()):
                    return {"success": True, "message": "Executed (no textual result)", "result": ""}
                return {"success": True, "message": "Executed freeform instruction", "result": str(result)}
            except Exception as e:
                msg = str(e)
                if "No result received from execution" in msg or "BrowserStateRequestEvent" in msg:
                    logger.warning("⚠️ No result, treating as success (freeform)")
                    return {"success": True, "message": "Executed (no textual result)", "result": ""}
                logger.error(f"❌ Error executing freeform: {e}", exc_info=True)
                return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"❌ Outer error executing freeform: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _close_session(self, session_id: str):
        # Do not kill persistent browser; only forget agent memory for that session.
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global instance (single)
browser_agent = BrowserAgentHandler()

