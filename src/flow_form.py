# flow_form.py - Simplified flow for Google Sheets filling with action queue

import sys
import json
import asyncio
from typing import Optional, List, Dict, Any
from loguru import logger
from pipecat_flows import FlowArgs, FlowResult, FlowsFunctionSchema, NodeConfig, FlowManager
from prompt_form import SYSTEM_PROMPT, TASK_PROMPT, WELCOME_MESSAGE

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

# Sheet data storage
sheet_data = {}

# Action queue - stores actions to execute
action_queue: List[Dict[str, Any]] = []

def add_to_action_queue(action_type: str, data: Dict[str, Any]):
    """
    Add an action to the queue.

    Args:
        action_type: Type of action ('add_data', 'fill_sheet', etc.)
        data: Action data/parameters
    """
    action = {
        "type": action_type,
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    }
    action_queue.append(action)
    logger.info(f"📋 Added action to queue: {action_type}")
    logger.info(f"📊 Queue size: {len(action_queue)}")
    logger.info(f"📜 Current queue: {[a['type'] for a in action_queue]}")
    return action

def get_action_queue_status() -> Dict[str, Any]:
    """Get current status of action queue"""
    return {
        "total_actions": len(action_queue),
        "actions": [{"type": a["type"], "timestamp": a["timestamp"]} for a in action_queue],
        "data_count": len([a for a in action_queue if a["type"] == "add_data"]),
        "fill_count": len([a for a in action_queue if a["type"] == "fill_sheet"])
    }

async def add_sheet_data(args: FlowArgs, flow_manager: FlowManager) -> dict:
    """
    Extract data fields from user speech and store them.
    This function is called by the LLM when user provides data to add to the sheet.
    Actions are queued for later execution.
    """
    field_name = args.get("field_name", "")
    field_value = args.get("field_value", "")

    logger.info(f"🔥 add_sheet_data called with: field_name='{field_name}', field_value='{field_value}'")

    if not field_name or not field_value:
        logger.warning(f"⚠️ Missing data in add_sheet_data: field_name='{field_name}', field_value='{field_value}'")
        return {
            "success": False,
            "message": "Dạ em chưa hiểu rõ thông tin. Anh/chị vui lòng nói lại ạ."
        }

    # Queue the action
    add_to_action_queue("add_data", {
        "field_name": field_name,
        "field_value": field_value
    })

    # Store sheet data
    sheet_data[field_name] = field_value
    logger.info(f"📝 Successfully stored sheet data: {field_name} = {field_value}")
    logger.info(f"📊 Current sheet_data: {sheet_data}")

    # Store in flow manager state
    if flow_manager:
        if "sheet_data" not in flow_manager.state:
            flow_manager.state["sheet_data"] = {}
        flow_manager.state["sheet_data"][field_name] = field_value

    # Count how many fields we have
    total_fields = len(sheet_data)

    # Suggest filling sheet if user has provided several fields
    if total_fields >= 3:  # If user has provided 3+ fields
        message = f"Dạ em đã lưu {field_name}: {field_value}. Hiện tại em đã có {total_fields} thông tin. Anh/chị có muốn em thêm tất cả vào Google Sheets không ạ?"
    else:
        message = f"Dạ em đã lưu {field_name}: {field_value}. Anh/chị có muốn thêm thông tin nào khác không ạ?"

    return {
        "success": True,
        "field_name": field_name,
        "field_value": field_value,
        "total_fields": total_fields,
        "queued_actions": len(action_queue),
        "message": message
    }

async def execute_action_queue(google_sheets_url: str = None) -> dict:
    """
    Execute all queued actions sequentially using ONE browser session.
    This is called when user wants to execute all pending actions.

    Args:
        google_sheets_url: Optional Google Sheets URL to navigate to

    Returns:
        dict with execution results
    """
    global action_queue

    if not action_queue:
        logger.warning("⚠️ No actions in queue to execute")
        return {
            "success": False,
            "message": "Dạ chưa có hành động nào để thực hiện ạ."
        }

    logger.info(f"🚀 Executing {len(action_queue)} actions from queue")
    logger.info(f"📜 Queue before execution: {get_action_queue_status()}")

    from browser_agent import browser_agent

    executed_actions = []
    failed_actions = []

    try:
        # Ensure browser is initialized ONCE - reuse same session for all actions
        await browser_agent.ensure_initialized()
        logger.info("✅ Browser session ready - will reuse for all queued actions")

        # Navigate to Google Sheets if URL provided (only once)
        if google_sheets_url:
            await browser_agent.navigate_to_sheet(google_sheets_url)
            logger.info(f"✅ Navigated to Google Sheets - ready to execute {len(action_queue)} actions")

        # Process each action in queue using the SAME browser session
        for i, action in enumerate(action_queue):
            action_type = action["type"]
            action_data = action["data"]

            logger.info(f"⚙️ [{i + 1}/{len(action_queue)}] Executing: {action_type}")
            logger.info(f"📄 Action data: {action_data}")

            try:
                if action_type == "add_data":
                    # Already stored in sheet_data, just log
                    logger.info(f"✅ Data already stored: {action_data}")
                    executed_actions.append(action)

                elif action_type == "fill_sheet":
                    # Execute browser automation to fill sheet (reusing same browser session)
                    logger.info(f"🌐 Filling sheet using existing browser session")
                    result = await browser_agent.fill_sheet_row(action_data)
                    if result["success"]:
                        executed_actions.append(action)
                        logger.info(f"✅ Successfully filled sheet with {len(action_data)} fields")
                    else:
                        failed_actions.append({"action": action, "error": result.get("error")})
                        logger.error(f"❌ Failed to fill sheet: {result.get('error')}")

                else:
                    logger.warning(f"⚠️ Unknown action type: {action_type}")

            except Exception as e:
                logger.error(f"❌ Error executing action {i + 1}: {e}")
                failed_actions.append({"action": action, "error": str(e)})

        # Clear queue after execution
        logger.info(f"📜 Queue after execution - clearing {len(action_queue)} actions")
        action_queue = []
        logger.info("🗑️ Action queue cleared - browser session remains active for future use")

        # Return results
        if failed_actions:
            return {
                "success": False,
                "executed": len(executed_actions),
                "failed": len(failed_actions),
                "failed_actions": failed_actions,
                "message": f"Dạ em đã thực hiện {len(executed_actions)} hành động, nhưng có {len(failed_actions)} lỗi ạ."
            }
        else:
            return {
                "success": True,
                "executed": len(executed_actions),
                "message": f"Dạ em đã thực hiện thành công {len(executed_actions)} hành động ạ!"
            }

    except Exception as e:
        logger.error(f"❌ Failed to execute action queue: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Dạ em gặp lỗi khi thực hiện các hành động: {str(e)}"
        }

async def fill_google_sheet(args: FlowArgs, flow_manager: FlowManager) -> dict:
    """
    Fill Google Sheets with the collected data using browser-use Agent.
    This function queues the fill action and executes the entire queue.

    IMPORTANT: This function checks if data exists. If not, returns error message.
    """
    try:
        logger.info(f"🔥 fill_google_sheet called!")

        # Get all stored sheet data
        data_to_fill = sheet_data.copy()
        logger.info(f"📊 Data to fill: {data_to_fill}")

        if not data_to_fill:
            logger.warning("⚠️ No data to fill - sheet_data is empty")

            # Return helpful message asking user to provide data first
            return {
                "success": False,
                "message": "Dạ em chưa có dữ liệu nào để thêm vào sheet. Anh/chị vui lòng cho em biết thông tin như tên, email, số điện thoại trước. Sau đó em sẽ mở Google Sheets và điền thông tin ạ."
            }

        # Queue the fill_sheet action
        add_to_action_queue("fill_sheet", data_to_fill)

        # Get Google Sheets URL from environment or args
        import os
        google_sheets_url = os.getenv("GOOGLE_SHEETS_URL")

        logger.info(f"🚀 Executing action queue to fill Google Sheets")

        # Execute the entire action queue (including all add_data + fill_sheet)
        result = await execute_action_queue(google_sheets_url)

        if result["success"]:
            # Clear data after successful execution
            clear_sheet_data()

            logger.info("✅ Successfully executed all queued actions and filled Google Sheets")

            return {
                "success": True,
                "filled_data": data_to_fill,
                "executed_actions": result.get("executed", 0),
                "message": f"Dạ em đã thêm thành công {len(data_to_fill)} thông tin vào Google Sheets. Anh/chị có muốn thêm dữ liệu mới không ạ?"
            }
        else:
            logger.error(f"❌ Queue execution failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error"),
                "message": result.get("message", "Dạ em gặp lỗi khi thêm vào Google Sheets. Anh/chị thử lại được không ạ?")
            }

    except Exception as e:
        logger.error(f"❌ Failed to fill Google Sheets: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Dạ em gặp lỗi khi thêm vào Google Sheets. Anh/chị thử lại được không ạ?"
        }

def create_sheet_filling_node() -> NodeConfig:
    """Create the main node for sheet filling conversation"""

    functions = [
        FlowsFunctionSchema(
            name="add_sheet_data",
            description="MANDATORY: Extract and store data fields from user's voice input. MUST be called IMMEDIATELY when user provides ANY information like name, email, phone, address, company, etc. Examples: 'tên hiếu nghị' -> call add_sheet_data('name', 'Hiếu Nghị'), 'email abc@gmail.com' -> call add_sheet_data('email', 'abc@gmail.com')",
            properties={
                "field_name": {
                    "type": "string",
                    "description": "The name/type of the data field: 'name' for tên, 'email' for email, 'phone' for số điện thoại, 'address' for địa chỉ, 'company' for công ty, etc."
                },
                "field_value": {
                    "type": "string", 
                    "description": "The actual value/data that user provided"
                }
            },
            required=["field_name", "field_value"],
            handler=add_sheet_data
        ),
        FlowsFunctionSchema(
            name="fill_google_sheet",
            description="CRITICAL: Execute browser automation to OPEN Google Sheets and FILL with all collected data. MUST call when user says: 'bật google sheet', 'mở sheet', 'vào sheet', 'mở google sheet', 'thêm vào sheet', 'lưu vào bảng tính', 'save', 'submit', 'hoàn thành', 'điền vào sheet', 'điền sheet', OR any phrase indicating they want to open/access/fill the spreadsheet NOW.",
            properties={},
            required=[],
            handler=fill_google_sheet
        )
    ]

    return {
        "name": "sheet_filling_node",
        "role_messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ],
        "task_messages": [
            {
                "role": "user",
                "content": TASK_PROMPT
            },
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE
            }
        ],
        "functions": functions
    }

def clear_sheet_data():
    """Clear all stored sheet data"""
    global sheet_data
    sheet_data = {}
    logger.info("🗑️  Cleared sheet data")
