# flow_form.py - Simplified flow for Google Sheets filling

import sys
import json
from typing import Optional
from loguru import logger
from pipecat_flows import FlowArgs, FlowResult, FlowsFunctionSchema, NodeConfig, FlowManager
from prompt_form import SYSTEM_PROMPT, TASK_PROMPT, WELCOME_MESSAGE

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

# Sheet data storage
sheet_data = {}

async def add_sheet_data(args: FlowArgs, flow_manager: FlowManager) -> dict:
    """
    Extract data fields from user speech and store them.
    This function is called by the LLM when user provides data to add to the sheet.
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
        "message": message
    }

async def fill_google_sheet(args: FlowArgs, flow_manager: FlowManager) -> dict:
    """
    Fill Google Sheets with the collected data using browser-use Agent.
    This function is called when user wants to save all data to sheet.
    """
    try:
        logger.info(f"🔥 fill_google_sheet called!")
        from browser_agent import browser_agent

        # Get all stored sheet data
        data_to_fill = sheet_data.copy()
        logger.info(f"📊 Data to fill: {data_to_fill}")

        if not data_to_fill:
            logger.warning("⚠️ No data to fill - sheet_data is empty")
            return {
                "success": False,
                "message": "Dạ chưa có dữ liệu nào để thêm vào sheet. Anh/chị vui lòng cung cấp thông tin trước ạ."
            }

        logger.info(f"🚀 Starting browser-use Agent to fill sheet with data: {data_to_fill}")

        # Fill the sheet row with collected data using browser-use Agent
        result = await browser_agent.fill_sheet_row(data_to_fill)

        if result["success"]:
            # Clear data after successful filling
            clear_sheet_data()

            logger.info("✅ Successfully filled Google Sheets with browser-use Agent")

            return {
                "success": True,
                "filled_data": data_to_fill,
                "message": f"Dạ em đã thêm thành công {len(data_to_fill)} thông tin vào Google Sheets. Anh/chị có muốn thêm dữ liệu mới không ạ?"
            }
        else:
            logger.error(f"❌ Browser-use Agent failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error"),
                "message": "Dạ em gặp lỗi khi thêm vào Google Sheets. Anh/chị thử lại được không ạ?"
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
            description="Execute browser automation to fill Google Sheets with all collected data. Call this when user wants to save/submit data to spreadsheet with phrases like 'thêm vào sheet', 'lưu vào bảng tính', 'save', 'submit', 'hoàn thành', 'điền vào sheet'.",
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

def get_stored_sheet_data() -> dict:
    """Get all stored sheet data"""
    return sheet_data.copy()

def clear_sheet_data():
    """Clear all stored sheet data"""
    global sheet_data
    sheet_data = {}
    logger.info("🗑️  Cleared sheet data")
