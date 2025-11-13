"""
LangGraph Multi-Agent Workflow - Supervisor Pattern
Sử dụng Supervisor Agent với tools để điều phối 5 use cases
"""
from typing import Annotated, Literal
from datetime import datetime
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from loguru import logger

from .state import MultiAgentState

# Import browser_agent from src
from src.browser_agent import browser_agent

# Import utility modules
from src.utils.date_parser import parse_vietnamese_date
from src.utils.field_mapper import map_vietnamese_to_english, FieldMapper
from src.utils.pronoun_resolver import resolve_pronouns, update_person_context, update_field_context, get_resolver


# ============================================
# BROWSER TOOLS - Các tools để điền form
# ============================================

# ============================================
# INCREMENTAL MODE TOOLS (NEW!)
# ============================================

# Store current session_id from state (accessed via closure)
_current_session_id = "default"

def set_session_id(session_id: str):
    """Set current session_id for tools"""
    global _current_session_id
    _current_session_id = session_id

@tool
async def start_incremental_form(form_type: str) -> str:
    """
    Bắt đầu session điền form incremental - Mở browser và giữ mở.
    Reuses existing session if available for this session_id.
    
    Args:
        form_type: Loại form (loan/crm/hr/compliance/operations)
        
    Returns:
        Kết quả mở form
    """
    import os
    global _current_session_id
    
    # Get form URL
    urls = {
        "loan": os.getenv("LOAN_FORM_URL", "https://vpbank-shared-form-fastdeploy.vercel.app/"),
        "crm": os.getenv("CRM_FORM_URL", "https://case2-ten.vercel.app/"),
        "hr": os.getenv("HR_FORM_URL", "https://case3-seven.vercel.app/"),
        "compliance": os.getenv("COMPLIANCE_FORM_URL", "https://case4-beta.vercel.app/"),
        "operations": os.getenv("OPERATIONS_FORM_URL", "https://case5-chi.vercel.app/")
    }
    
    form_url = urls.get(form_type)
    if not form_url:
        return f"❌ Invalid form type: {form_type}"
    
    logger.info(f"🚀 Starting incremental form: {form_type} (session_id: {_current_session_id})")
    
    result = await browser_agent.start_form_session(form_url, form_type, _current_session_id)
    
    if result.get("success"):
        return f"✅ Đã mở form {form_type}. Bạn có thể bắt đầu điền từng field bằng cách nói: 'Điền tên là X', 'Điền SĐT là Y'..."
    else:
        return f"❌ Lỗi mở form: {result.get('error')}"


@tool
async def go_to_next_step() -> str:
    """
    Nhấn nút "Tiếp tục" để chuyển sang bước tiếp theo trong wizard (Use case 1).
    - Giữ nguyên browser/session đang mở.
    - Chỉ thực hiện thao tác click và chờ trang chuyển bước.
    """
    global _current_session_id
    logger.info(f"➡️  Go to next step (session_id: {_current_session_id})")

    # Check session exists
    if _current_session_id not in browser_agent.sessions:
        return "❌ Không có active session. Hãy start_incremental_form trước."

    session = browser_agent.sessions[_current_session_id]
    agent = session["agent"]

    task = (
        "Click nút có text 'Tiếp tục' ở cuối trang để chuyển sang bước tiếp theo. "
        "Sau khi click, chờ trang tải xong (đợi tiêu đề phần kế tiếp xuất hiện), "
        "tuyệt đối không đóng trình duyệt."
    )

    agent.add_new_task(task)
    await agent.run(max_steps=8)

    return "✅ Đã chuyển sang bước tiếp theo"


@tool
async def fill_multiple_fields(fields_json: str) -> str:
    """
    Điền NHIỀU fields cùng lúc từ conversation history.
    Sử dụng khi supervisor extract được nhiều fields từ conversation.
    
    Args:
        fields_json: JSON string chứa dict các fields cần điền
                    VD: '{"customerName": "Hiếu Nghị", "customerId": "012345678901", "phoneNumber": "0963023600"}'
    
    Returns:
        Kết quả điền fields
    """
    import json
    import os
    global _current_session_id
    
    try:
        fields_dict = json.loads(fields_json)
        logger.info(f"📝 Filling multiple fields: {list(fields_dict.keys())} (session_id: {_current_session_id})")
        
        results = []
        for field_name, field_value in fields_dict.items():
            # Auto-start session nếu chưa có
            if _current_session_id not in browser_agent.sessions:
                logger.info(f"⚠️  No active session, auto-starting...")
                form_url = os.getenv("LOAN_FORM_URL", "https://vpbank-shared-form-fastdeploy.vercel.app/")
                start_result = await browser_agent.start_form_session(form_url, "loan", _current_session_id)
                if not start_result.get("success"):
                    return f"❌ Không thể mở form: {start_result.get('error')}"
            
            # Fill từng field
            result = await browser_agent.fill_field_incremental(field_name, str(field_value), _current_session_id)
            if result.get("success"):
                results.append(f"{field_name}={field_value}")
            else:
                results.append(f"{field_name}=ERROR: {result.get('error')}")
        
        return f"✅ Đã điền {len(results)} fields: {', '.join(results)}"
    except json.JSONDecodeError as e:
        return f"❌ Lỗi parse JSON: {e}"
    except Exception as e:
        logger.error(f"Error in fill_multiple_fields: {e}", exc_info=True)
        return f"❌ Lỗi: {str(e)}"


@tool
async def remove_single_field(field_name: str) -> str:
    """
    Xóa/clear 1 field cụ thể trong form đang mở (incremental mode).
    Dùng khi user nói: "xóa CCCD", "xoá số căn cước", "clear customerId"...
    """
    global _current_session_id
    logger.info(f"🧽 Remove single field: {field_name} (session_id: {_current_session_id})")

    if _current_session_id not in browser_agent.sessions:
        return "❌ Không có active session. Hãy start_incremental_form trước."

    result = await browser_agent.remove_field_incremental(field_name, _current_session_id)
    if result.get("success"):
        return f"✅ Đã xóa nội dung field {field_name}."
    return f"❌ Lỗi khi xóa field {field_name}: {result.get('error', 'Unknown error')}"

@tool
async def fill_single_field(field_name: str, field_value: str) -> str:
    """
    Điền 1 field cụ thể trong form đang mở (incremental mode).
    Reuses existing session for this session_id.
    
    Args:
        field_name: Tên field HTML (customerName, phoneNumber, email, loanAmount, etc.)
        field_value: Giá trị cần điền
        
    Returns:
        Kết quả điền field
    """
    import os
    global _current_session_id
    logger.info(f"📝 Incremental fill: {field_name} = {field_value} (session_id: {_current_session_id})")
    
    # AUTO-START SESSION nếu chưa có active session cho session_id này
    if _current_session_id not in browser_agent.sessions:
        logger.info(f"⚠️  No active session for {_current_session_id}, auto-starting session...")
        
        # Detect form type từ field_name hoặc context
        form_type = "loan"  # Default
        
        # Auto-start session
        form_url = os.getenv("LOAN_FORM_URL", "https://vpbank-shared-form-fastdeploy.vercel.app/")
        start_result = await browser_agent.start_form_session(form_url, form_type, _current_session_id)
        
        if not start_result.get("success"):
            return f"❌ Không thể mở form: {start_result.get('error')}. Vui lòng thử lại."
        
        logger.info(f"✅ Auto-started session for {form_type} form (session_id: {_current_session_id})")
    
    # Now fill the field
    result = await browser_agent.fill_field_incremental(field_name, field_value, _current_session_id)
    
    if result.get("success"):
        fields_count = result.get("fields_filled", 0)
        skipped = result.get("skipped", False)
        
        if skipped:
            return f"✅ Field {field_name} đã có giá trị, không ghi đè. Tổng đã điền: {fields_count} fields."
        else:
            return f"✅ Đã điền {field_name} = {field_value}. Tổng đã điền: {fields_count} fields. Tiếp tục điền hoặc nói 'Submit' để gửi."
    else:
        return f"❌ Lỗi điền field: {result.get('error')}"


@tool
async def submit_incremental_form() -> str:
    """
    Submit form đang được điền incremental và đóng browser sau khi xong.
    
    TRƯỚC KHI SUBMIT: Agent sẽ tự động check xem đã đủ required fields chưa.
    Nếu thiếu fields, sẽ báo lỗi và KHÔNG submit.
    
    Returns:
        Kết quả submit hoặc thông báo fields còn thiếu
    """
    global _current_session_id
    logger.info(f"🚀 Submitting incremental form... (session_id: {_current_session_id})")
    
    # Check session exists
    if _current_session_id not in browser_agent.sessions:
        return f"❌ Không có active session. Vui lòng bắt đầu form trước khi submit."
    
    # Get filled fields count
    session = browser_agent.sessions[_current_session_id]
    fields_filled = session["session_data"].get("fields_filled", [])
    fields_count = len(fields_filled)
    
    logger.info(f"📋 Checking form completion: {fields_count} fields filled")
    
    result = await browser_agent.submit_form_incremental(_current_session_id)
    
    if result.get("success"):
        return f"✅ Form đã được submit thành công! Đã điền {fields_count} fields. Browser đã đóng."
    else:
        error_msg = result.get("error", "Unknown error")
        # Check if error is about missing fields
        if "missing" in error_msg.lower() or "required" in error_msg.lower():
            return f"⚠️ {error_msg} Vui lòng điền đầy đủ thông tin trước khi submit."
        return f"❌ Lỗi submit form: {error_msg}"


# ============================================
# NEW REQUIRED TOOLS (BTC Requirements)
# ============================================

@tool
async def upload_file_to_field(field_name: str, file_description: str = "") -> str:
    """
    Upload file vào field cụ thể (CCCD scan, hợp đồng, chứng từ).
    User sẽ chọn file từ UI, tool này trigger file picker.
    
    Args:
        field_name: Tên field upload (e.g., "idCardImage", "contractFile", "attachments")
        file_description: Mô tả file (optional, e.g., "Ảnh căn cước công dân")
    
    Returns:
        Kết quả upload
    
    Example:
        User: "Upload ảnh CCCD"
        → upload_file_to_field("idCardImage", "Ảnh căn cước công dân")
    """
    global _current_session_id
    logger.info(f"📎 Upload file to field: {field_name} (session_id: {_current_session_id})")
    
    if _current_session_id not in browser_agent.sessions:
        return "❌ Không có active session. Hãy start form trước."
    
    # Call browser agent's upload method
    result = await browser_agent.upload_file_to_field(field_name, file_description, _current_session_id)
    
    if result.get("success"):
        return f"✅ Đã upload file vào field {field_name}. File: {result.get('filename', 'unknown')}"
    else:
        return f"❌ Lỗi upload file: {result.get('error', 'Unknown error')}"


@tool
async def search_field_on_form(search_query: str) -> str:
    """
    Tìm kiếm field trên form theo tên hoặc label (tiếng Việt hoặc tiếng Anh).
    Sau khi tìm thấy, tự động focus vào field đó.
    
    Args:
        search_query: Từ khóa tìm kiếm (e.g., "số điện thoại", "email", "địa chỉ", "phone")
    
    Returns:
        Danh sách fields tìm thấy và field được focus
    
    Example:
        User: "Tìm field số điện thoại"
        → search_field_on_form("số điện thoại")
        → Focus vào field phoneNumber
    """
    global _current_session_id
    logger.info(f"🔍 Search field: {search_query} (session_id: {_current_session_id})")
    
    if _current_session_id not in browser_agent.sessions:
        return "❌ Không có active session. Hãy start form trước."
    
    # Call browser agent's search method
    result = await browser_agent.search_and_focus_field(search_query, _current_session_id)
    
    if result.get("success"):
        fields_found = result.get("fields_found", [])
        focused_field = result.get("focused_field", "")
        
        if len(fields_found) == 0:
            return f"❌ Không tìm thấy field nào với từ khóa '{search_query}'"
        elif len(fields_found) == 1:
            return f"✅ Tìm thấy và focus vào field: {focused_field}"
        else:
            return f"✅ Tìm thấy {len(fields_found)} fields: {', '.join(fields_found)}. Đã focus vào: {focused_field}"
    else:
        return f"❌ Lỗi tìm kiếm: {result.get('error', 'Unknown error')}"


@tool
async def save_form_draft(draft_name: str = None) -> str:
    """
    Lưu nháp form hiện tại để tiếp tục sau.
    Lưu tất cả fields đã điền vào DynamoDB với status="draft".
    
    Args:
        draft_name: Tên bản nháp (optional, auto-generate nếu không có)
    
    Returns:
        Kết quả lưu nháp
    
    Example:
        User: "Lưu nháp tên là 'Đơn vay An'"
        → save_form_draft("Đơn vay An")
    """
    global _current_session_id
    logger.info(f"💾 Save draft: {draft_name} (session_id: {_current_session_id})")
    
    if _current_session_id not in browser_agent.sessions:
        return "❌ Không có active session. Hãy start form trước."
    
    # Auto-generate draft name if not provided
    if not draft_name:
        from datetime import datetime
        draft_name = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Call browser agent's save draft method
    result = await browser_agent.save_form_draft(draft_name, _current_session_id)
    
    if result.get("success"):
        fields_count = result.get("fields_count", 0)
        return f"✅ Đã lưu nháp '{draft_name}' với {fields_count} fields. Bạn có thể load lại sau bằng: 'Load nháp {draft_name}'"
    else:
        return f"❌ Lỗi lưu nháp: {result.get('error', 'Unknown error')}"


@tool
async def load_form_draft(draft_name: str) -> str:
    """
    Load lại bản nháp đã lưu và điền vào form.
    
    Args:
        draft_name: Tên bản nháp cần load
    
    Returns:
        Kết quả load nháp
    
    Example:
        User: "Load nháp 'Đơn vay An'"
        → load_form_draft("Đơn vay An")
    """
    global _current_session_id
    logger.info(f"📂 Load draft: {draft_name} (session_id: {_current_session_id})")
    
    if _current_session_id not in browser_agent.sessions:
        return "❌ Không có active session. Hãy start form trước."
    
    # Call browser agent's load draft method
    result = await browser_agent.load_form_draft(draft_name, _current_session_id)
    
    if result.get("success"):
        fields_count = result.get("fields_count", 0)
        fields_loaded = result.get("fields_loaded", [])
        return f"✅ Đã load nháp '{draft_name}' với {fields_count} fields: {', '.join(fields_loaded)}"
    else:
        return f"❌ Lỗi load nháp: {result.get('error', 'Unknown error')}"


# ============================================
# ENHANCED TOOLS - With pronoun resolution, date parsing, field mapping
# ============================================

@tool
async def fill_field_smart(field_description: str, field_value: str) -> str:
    """
    Điền field thông minh với:
    - Tự động map tên field Việt → Anh (họ tên → fullName)
    - Parse ngày tháng tiếng Việt (15 tháng 3 năm 1990 → 1990-03-15)
    - Resolve đại từ (anh ấy, cô ấy, nó)
    
    Args:
        field_description: Mô tả field bằng tiếng Việt hoặc Anh
        field_value: Giá trị cần điền
    
    Returns:
        Kết quả điền field
    
    Examples:
        fill_field_smart("họ và tên", "Nguyễn Văn An")
        fill_field_smart("ngày sinh", "15 tháng 3 năm 1990")
        fill_field_smart("số điện thoại", "0901234567")
    """
    import os
    global _current_session_id
    
    # Resolve pronouns in value
    resolved_value = resolve_pronouns(field_value)
    
    # Try to parse date if it looks like a date
    if any(keyword in field_description.lower() for keyword in ["ngày", "date", "sinh", "birth", "cấp", "issue", "hạn", "expiry"]):
        parsed_date = parse_vietnamese_date(resolved_value)
        if parsed_date:
            resolved_value = parsed_date
            logger.info(f"📅 Parsed date: {field_value} → {parsed_date}")
    
    # Map Vietnamese field name to English
    english_fields = map_vietnamese_to_english(field_description.lower())
    if english_fields:
        field_name = english_fields[0]  # Use first match
        logger.info(f"🗺️  Mapped field: {field_description} → {field_name}")
    else:
        # Use as-is if no mapping found
        field_name = field_description
    
    # Update context for pronoun resolution
    update_field_context(field_name, resolved_value)
    
    # Auto-start session if needed
    if _current_session_id not in browser_agent.sessions:
        logger.info(f"⚠️  No active session, auto-starting...")
        form_url = os.getenv("LOAN_FORM_URL", "https://vpbank-shared-form-fastdeploy.vercel.app/")
        start_result = await browser_agent.start_form_session(form_url, "loan", _current_session_id)
        if not start_result.get("success"):
            return f"❌ Không thể mở form: {start_result.get('error')}"
    
    # Fill field
    result = await browser_agent.fill_field_incremental(field_name, resolved_value, _current_session_id)
    
    if result.get("success"):
        return f"✅ Đã điền {field_description} ({field_name}) = {resolved_value}"
    else:
        return f"❌ Lỗi điền field {field_description}: {result.get('error')}"


@tool
async def process_user_input_smart(user_text: str) -> str:
    """
    Xử lý input của user thông minh:
    - Extract tên người và cập nhật context
    - Resolve đại từ
    - Trả về text đã xử lý
    
    Args:
        user_text: Text từ user
    
    Returns:
        Text đã được xử lý
    
    Examples:
        "Tên là Nguyễn Văn An" → Update context với person="Nguyễn Văn An"
        "Anh ấy sinh năm 1990" → "Nguyễn Văn An sinh năm 1990"
    """
    resolver = get_resolver()
    
    # Extract entities and resolve pronouns
    processed_text = resolver.extract_and_update(user_text)
    
    logger.info(f"🧠 Processed: '{user_text}' → '{processed_text}'")
    
    return processed_text


# ============================================
# ONE-SHOT MODE TOOLS (Legacy)
# ============================================

@tool
def fill_loan_form(
    customer_name: str,
    customer_id: str,
    date_of_birth: str,
    address: str,
    phone_number: str,
    email: str,
    loan_amount: int,
    loan_purpose: str,
    loan_term: int,
    employment_status: str,
    company_name: str,
    monthly_income: int,
    gender: str = "male",
    application_date: str = None,
    work_address: str = "",
    collateral_type: str = "none",
    collateral_value: int = 0,
    collateral_description: str = "",
    relationship_manager: str = "",
    additional_notes: str = ""
) -> str:
    """
    Điền form đơn vay vốn & KYC (Use Case 1).
    
    Args:
        customer_name: Họ tên khách hàng
        customer_id: Số CCCD/CMND (12 chữ số)
        date_of_birth: Ngày sinh (YYYY-MM-DD)
        address: Địa chỉ thường trú
        phone_number: Số điện thoại (10 chữ số)
        email: Email
        loan_amount: Số tiền vay (VNĐ)
        loan_purpose: Mục đích vay (personal/business/education/home/vehicle/renovation/other)
        loan_term: Kỳ hạn (6/12/18/24/36/48/60 tháng)
        employment_status: Tình trạng việc làm (employed/self-employed/unemployed/retired)
        company_name: Tên công ty/nơi làm việc
        monthly_income: Thu nhập hàng tháng (VNĐ)
        gender: Giới tính (male/female/other)
        
    Returns:
        Kết quả điền form
    """
    logger.info(f"🏦 [TOOL CALLED] fill_loan_form for: {customer_name}")
    
    # Auto-fill application date if not provided
    if not application_date:
        application_date = datetime.now().strftime("%Y-%m-%d")
    
    # Map field names to match HTML form
    form_data = {
        "customerName": customer_name,
        "customerId": customer_id,
        "dateOfBirth": date_of_birth,
        "address": address,
        "phoneNumber": phone_number,
        "email": email,
        "gender": gender,
        "loanAmount": str(loan_amount),
        "loanPurpose": loan_purpose,
        "loanTerm": str(loan_term),
        "applicationDate": application_date,
        "employmentStatus": employment_status,
        "companyName": company_name,
        "monthlyIncome": str(monthly_income),
        "workAddress": work_address,
        "collateralType": collateral_type,
        "collateralValue": str(collateral_value),
        "collateralDescription": collateral_description,
        "relationshipManager": relationship_manager,
        "additionalNotes": additional_notes
    }
    
    logger.info(f"   📋 Form data prepared: {len(form_data)} fields")
    
    try:
        # Execute browser task
        import asyncio
        import os
        
        # Get form URL from environment
        form_url = os.getenv("LOAN_FORM_URL", "https://vpbank-shared-form-fastdeploy.vercel.app/")
        
        # Use asyncio.run() safely
        try:
            # Check if event loop is already running
            loop = asyncio.get_running_loop()
            # If we're here, loop is running - this shouldn't happen in sync tool
            logger.warning("Event loop already running, using run_coroutine_threadsafe")
            import concurrent.futures
            future = asyncio.run_coroutine_threadsafe(
                browser_agent.fill_form(form_url, form_data, "loan"),
                loop
            )
            result = future.result(timeout=60)
        except RuntimeError:
            # No event loop running, safe to use asyncio.run()
            result = asyncio.run(browser_agent.fill_form(form_url, form_data, "loan"))
        
        if result.get("success"):
            return f"✅ Đã điền form đơn vay thành công cho khách hàng {customer_name}"
        else:
            return f"❌ Lỗi khi điền form: {result.get('error', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error filling loan form: {e}")
        return f"❌ Lỗi khi điền form: {str(e)}"


@tool
def fill_crm_form(
    customer_name: str,
    customer_id: str,
    interaction_type: str,
    issue_description: str,
    agent_name: str,
    phone_number: str = "0000000000",
    email: str = "temp@vpbank.com",
    address: str = "Chưa cập nhật",
    interaction_date: str = None,
    interaction_time: str = "09:00",
    duration: int = 10,
    issue_category: str = "other",
    resolution_status: str = "resolved",
    resolution_details: str = "Đã xử lý",
    satisfaction_rating: str = "good",
    follow_up_required: str = "no",
    follow_up_date: str = None,
    notes: str = "Cập nhật qua voice bot",
    tags: str = ""
) -> str:
    """
    Cập nhật thông tin CRM (Use Case 2) - FULL MODE.
    
    Chỉ cần 4-5 fields chính từ user:
    - customer_name, customer_id
    - interaction_type (call/email/visit)
    - issue_description
    - agent_name
    
    Các fields khác có defaults!
    """
    from datetime import datetime
    
    logger.info(f"📞 [TOOL CALLED] fill_crm_form for: {customer_name}")
    logger.info(f"   Data: {form_data}")
    
    # Auto-fill dates
    if not interaction_date:
        interaction_date = datetime.now().strftime("%Y-%m-%d")
    if not follow_up_date:
        follow_up_date = datetime.now().strftime("%Y-%m-%d")
    
    # Map to HTML form fields (theo vpbank-forms/use-case-2-crm-update)
    form_data = {
        # Customer info
        "customerName": customer_name,
        "customerId": customer_id,
        "phoneNumber": phone_number,
        "email": email,
        "address": address,
        
        # Interaction details
        "interactionType": interaction_type,
        "interactionDate": interaction_date,
        "interactionTime": interaction_time,
        "duration": str(duration),
        "agentName": agent_name,
        
        # Issue
        "issueCategory": issue_category,
        "issueDescription": issue_description,
        
        # Resolution
        "resolutionStatus": resolution_status,
        "resolutionDetails": resolution_details,
        
        # Feedback
        "satisfactionRating": satisfaction_rating,
        "followUpRequired": follow_up_required,
        "followUpDate": follow_up_date,
        
        # Notes
        "notes": notes,
        "tags": tags
    }
    
    try:
        import asyncio
        import os
        
        # Get form URL from environment
        form_url = os.getenv("CRM_FORM_URL", "https://case2-ten.vercel.app/")
        
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            future = asyncio.run_coroutine_threadsafe(
                browser_agent.fill_form(form_url, form_data, "crm"),
                loop
            )
            result = future.result(timeout=60)
        except RuntimeError:
            result = asyncio.run(browser_agent.fill_form(form_url, form_data, "crm"))
        
        if result.get("success"):
            return f"✅ Đã cập nhật CRM thành công cho khách hàng {customer_name}"
        else:
            return f"❌ Lỗi khi cập nhật CRM: {result.get('error', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error filling CRM form: {e}")
        return f"❌ Lỗi khi cập nhật CRM: {str(e)}"


@tool
def fill_hr_form(
    employee_name: str,
    employee_id: str,
    request_type: str,
    start_date: str,
    end_date: str,
    reason: str,
    manager_name: str,
    department: str = "Operations",
    position: str = "Nhân viên",
    email: str = "employee@vpbank.com",
    phone_number: str = "0000000000",
    leave_type: str = "annual",
    duration: int = 1,
    manager_email: str = "manager@vpbank.com",
    approval_status: str = "pending",
    rejection_reason: str = "",
    submission_date: str = None,
    contact_during_absence: str = "",
    work_handover: str = "",
    notes: str = "Đơn tạo qua voice bot"
) -> str:
    """
    Điền form HR workflow (Use Case 3) - MEDIUM MODE.
    
    Chỉ cần 6-7 fields chính từ user:
    - employee_name, employee_id
    - request_type, start_date, end_date
    - reason, manager_name
    
    Các fields khác có defaults!
    """
    from datetime import datetime
    
    logger.info(f"👤 Filling HR form for: {employee_name}")
    
    # Auto-fill submission date
    if not submission_date:
        submission_date = datetime.now().strftime("%Y-%m-%d")
    
    # Map to HTML form fields (theo vpbank-forms/use-case-3-hr-workflow)
    form_data = {
        # Employee info
        "employeeName": employee_name,
        "employeeId": employee_id,
        "department": department,
        "position": position,
        "email": email,
        "phoneNumber": phone_number,
        
        # Request details
        "requestType": request_type,
        "leaveType": leave_type,
        "startDate": start_date,
        "endDate": end_date,
        "duration": str(duration),
        "reason": reason,
        
        # Approval
        "managerName": manager_name,
        "managerEmail": manager_email,
        "approvalStatus": approval_status,
        "rejectionReason": rejection_reason,
        
        # Additional
        "submissionDate": submission_date,
        "contactDuringAbsence": contact_during_absence,
        "workHandover": work_handover,
        "notes": notes
    }
    
    try:
        import asyncio
        import os
        
        # Get form URL from environment
        form_url = os.getenv("HR_FORM_URL", "https://case3-seven.vercel.app/")
        
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            future = asyncio.run_coroutine_threadsafe(
                browser_agent.fill_form(form_url, form_data, "hr"),
                loop
            )
            result = future.result(timeout=60)
        except RuntimeError:
            result = asyncio.run(browser_agent.fill_form(form_url, form_data, "hr"))
        
        if result.get("success"):
            return f"✅ Đã điền form HR thành công cho nhân viên {employee_name}"
        else:
            return f"❌ Lỗi khi điền form HR: {result.get('error', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error filling HR form: {e}")
        return f"❌ Lỗi khi điền form HR: {str(e)}"


@tool
def fill_compliance_form(
    report_type: str,
    compliance_officer: str,
    report_id: str = "BC-AUTO-001",
    reporting_period: str = None,
    submission_date: str = None,
    report_title: str = "Báo cáo tự động qua voice bot",
    officer_email: str = "compliance@vpbank.com",
    officer_position: str = "Nhân viên tuân thủ",
    department: str = "Risk & Compliance",
    status: str = "in-progress",
    cases_reviewed: int = 0,
    high_risk_cases: int = 0,
    violations_found: str = "none",
    violation_details: str = "",
    actions_taken: str = "Đang thực hiện kiểm tra",
    preventive_measures: str = "Theo dõi định kỳ",
    follow_up_required: str = "no",
    overall_risk: str = "low",
    risk_analysis: str = "Không phát hiện rủi ro",
    executive_summary: str = "Báo cáo tự động",
    additional_notes: str = "Được tạo tự động qua voice bot",
    recommendations: str = "Tiếp tục theo dõi"
) -> str:
    """
    Điền form báo cáo tuân thủ (Use Case 4) - MEDIUM MODE.
    
    Chỉ cần 2-3 fields chính từ user:
    - report_type (AML/KYC/audit/etc.)
    - compliance_officer (tên người nộp)
    
    Các fields khác có defaults!
    """
    from datetime import datetime
    
    logger.info(f"📋 Filling COMPLIANCE form: {report_type}")
    
    # Auto-fill dates
    if not reporting_period:
        reporting_period = datetime.now().strftime("%Y-%m")
    if not submission_date:
        submission_date = datetime.now().strftime("%Y-%m-%d")
    
    # Map to HTML form fields (theo vpbank-forms/use-case-4-compliance-reporting)
    form_data = {
        # Report info
        "reportId": report_id,
        "reportType": report_type,
        "reportingPeriod": reporting_period,
        "submissionDate": submission_date,
        "reportTitle": report_title,
        
        # Officer info
        "complianceOfficer": compliance_officer,
        "officerEmail": officer_email,
        "officerPosition": officer_position,
        "department": department,
        
        # Status & Statistics
        "status": status,
        "casesReviewed": str(cases_reviewed),
        "highRiskCases": str(high_risk_cases),
        "violationsFound": violations_found,
        "violationDetails": violation_details,
        
        # Actions
        "actionsTaken": actions_taken,
        "preventiveMeasures": preventive_measures,
        "followUpRequired": follow_up_required,
        
        # Risk assessment
        "overallRisk": overall_risk,
        "riskAnalysis": risk_analysis,
        
        # Notes
        "executiveSummary": executive_summary,
        "additionalNotes": additional_notes,
        "recommendations": recommendations
    }
    
    try:
        import asyncio
        import os
        
        # Get form URL from environment
        form_url = os.getenv("COMPLIANCE_FORM_URL", "https://case4-beta.vercel.app/")
        
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            future = asyncio.run_coroutine_threadsafe(
                browser_agent.fill_form(form_url, form_data, "compliance"),
                loop
            )
            result = future.result(timeout=60)
        except RuntimeError:
            result = asyncio.run(browser_agent.fill_form(form_url, form_data, "compliance"))
        
        if result.get("success"):
            return f"✅ Đã điền form compliance thành công: {report_type}"
        else:
            return f"❌ Lỗi khi điền form compliance: {result.get('error', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error filling compliance form: {e}")
        return f"❌ Lỗi khi điền form compliance: {str(e)}"


@tool
def fill_operations_form(
    transaction_id: str,
    customer_name: str,
    transaction_amount: int,
    customer_id: str = "CUS00000",
    account_number: str = "0000000000",
    phone_number: str = "0000000000",
    transaction_date: str = None,
    transaction_time: str = "09:00",
    transaction_type: str = "transfer",
    channel: str = "online",
    processing_system: str = "core-banking",
    transaction_description: str = "Kiểm tra tự động qua voice bot",
    beneficiary_name: str = "Chưa rõ",
    beneficiary_account: str = "0000000000",
    beneficiary_bank: str = "VPBank",
    status: str = "completed",
    validation_result: str = "valid",
    reviewer_name: str = "Hệ thống Voice Bot",
    review_date: str = None,
    balance_before: int = 0,
    balance_after: int = 0,
    balance_status: str = "matched",
    fraud_score: int = 0,
    fraud_indicators: str = "none",
    notes: str = "Kiểm tra tự động",
    action_required: str = "Không có"
) -> str:
    """
    Điền form kiểm tra giao dịch (Use Case 5) - ONE-SHOT MODE.
    
    Chỉ cần 3 fields bắt buộc từ user:
    - transaction_id
    - customer_name  
    - transaction_amount
    
    Tất cả fields khác có default values!
    """
    from datetime import datetime
    
    logger.info(f"💳 Filling OPERATIONS form (ONE-SHOT): {transaction_id}")
    
    # Auto-fill dates nếu không có
    if not transaction_date:
        transaction_date = datetime.now().strftime("%Y-%m-%d")
    if not review_date:
        review_date = datetime.now().strftime("%Y-%m-%d")
    
    # Map to HTML form fields (theo vpbank-forms/use-case-5-operations-validation)
    form_data = {
        # Customer info
        "customerName": customer_name,
        "customerId": customer_id,
        "accountNumber": account_number,
        "phoneNumber": phone_number,
        
        # Transaction info
        "transactionId": transaction_id,
        "transactionDate": transaction_date,
        "transactionTime": transaction_time,
        "transactionAmount": str(transaction_amount),
        "transactionType": transaction_type,
        "channel": channel,
        "transactionDescription": transaction_description,
        
        # Beneficiary (for transfers)
        "beneficiaryName": beneficiary_name,
        "beneficiaryAccount": beneficiary_account,
        "beneficiaryBank": beneficiary_bank,
        
        # Status
        "status": status,
        "processingSystem": processing_system,
        
        # Validation
        "validationResult": validation_result,
        "reviewerName": reviewer_name,
        "reviewDate": review_date,
        
        # Balance
        "balanceBefore": str(balance_before),
        "balanceAfter": str(balance_after),
        "balanceStatus": balance_status,
        
        # Fraud
        "fraudScore": str(fraud_score),
        "fraudIndicators": fraud_indicators,
        
        # Notes
        "notes": notes,
        "actionRequired": action_required
    }
    
    try:
        import asyncio
        import os
        
        # Get form URL from environment
        form_url = os.getenv("OPERATIONS_FORM_URL", "https://case5-chi.vercel.app/")
        
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            future = asyncio.run_coroutine_threadsafe(
                browser_agent.fill_form(form_url, form_data, "operations"),
                loop
            )
            result = future.result(timeout=60)
        except RuntimeError:
            result = asyncio.run(browser_agent.fill_form(form_url, form_data, "operations"))
        
        if result.get("success"):
            return f"✅ Đã điền form operations thành công: {transaction_id}"
        else:
            return f"❌ Lỗi khi điền form operations: {result.get('error', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error filling operations form: {e}")
        return f"❌ Lỗi khi điền form operations: {str(e)}"


# ============================================
# BUILD WORKFLOW - Supervisor + Worker Tools
# ============================================

def build_supervisor_workflow(llm):
    """
    Build LangGraph workflow với Supervisor pattern.
    
    Architecture:
    - Supervisor Agent: Phân tích user request và gọi appropriate tools
    - 5 Worker Tools: Mỗi tool tương ứng với 1 use case và điền form
    
    Flow:
    User Input → Supervisor (LLM với tools) → Tool execution → Response
    
    Args:
        llm: AWS Bedrock LLM instance
        
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("🔨 Building multi-agent workflow with Supervisor pattern...")
    
    # ============================================
    # Tạo Supervisor Agent với ALL tools
    # ============================================
    
    tools = [
        # One-shot mode (5 tools - legacy)
        fill_loan_form,
        fill_crm_form,
        fill_hr_form,
        fill_compliance_form,
        fill_operations_form,
        
        # Incremental mode (6 tools - ƯU TIÊN DÙNG)
        start_incremental_form,
        go_to_next_step,
        fill_single_field,
        fill_multiple_fields,  # Fill nhiều fields cùng lúc
        remove_single_field,   # Xóa 1 field cụ thể
        submit_incremental_form,
        
        # Required features (4 tools - BTC Requirements)
        upload_file_to_field,  # Upload file (CCCD, contracts)
        search_field_on_form,  # Search and focus field
        save_form_draft,       # Save draft to continue later
        load_form_draft,       # Load saved draft
        
        # Enhanced tools (2 tools - Advanced features)
        fill_field_smart,      # Smart field filling with date parsing, field mapping, pronoun resolution
        process_user_input_smart,  # Process user input with pronoun resolution
    ]
    
    supervisor_system_prompt = """Bạn là SUPERVISOR AGENT - Phân tích message và GỌI TOOL phù hợp!

        BẠN TUYỆT ĐỐI KHÔNG TRẢ LỜI TEXT - PHẢI GỌI TOOL!

        QUAN TRỌNG - INCREMENTAL MODE FIRST:
        - ƯU TIÊN phân tích message CUỐI CÙNG từ user
        - Nếu message chứa 1 field (tên, SĐT, CCCD, email, số tiền) → GỌI fill_single_field() NGAY
        - Nếu message chứa nhiều fields (5+) → Có thể dùng fill_loan_form() hoặc gọi fill_single_field() nhiều lần
        - KHÔNG dùng fill_loan_form() nếu chỉ có 1-2 fields

        VÍ DỤ PHÂN TÍCH MESSAGE:
        - User: "Tôi muốn vay 500 triệu" → Extract: field="loanAmount", value="500000000" → GỌI fill_single_field("loanAmount", "500000000")
        - User: "Tên là Hiếu Nghị" → Extract: field="customerName", value="Hiếu Nghị" → GỌI fill_single_field("customerName", "Hiếu Nghị")
        - User: "SĐT 0963023600" → Extract: field="phoneNumber", value="0963023600" → GỌI fill_single_field("phoneNumber", "0963023600")
        - User: "CCCD 123456789012" → Extract: field="customerId", value="123456789012" → GỌI fill_single_field("customerId", "123456789012")

        BẠN CÓ 10 TOOLS (2 MODES):

        ONE-SHOT MODE (5 tools - khi có ĐẦY ĐỦ thông tin trong 1 message):
        1. fill_loan_form - Điền TẤT CẢ fields đơn vay cùng lúc (dùng khi user nói tất cả thông tin)
        2. fill_crm_form - Điền TẤT CẢ fields CRM cùng lúc
        3. fill_hr_form - Điền TẤT CẢ fields HR cùng lúc
        4. fill_compliance_form - Điền TẤT CẢ fields compliance cùng lúc
        5. fill_operations_form - Điền TẤT CẢ fields operations cùng lúc

        INCREMENTAL MODE (các tools ưu tiên - khi điền TỪNG FIELD real-time):
        6. start_incremental_form(form_type) - Mở browser, navigate to form, GIỮ MỞ (gọi đầu tiên nếu chưa có session)
        7. go_to_next_step() - Nhấn nút "Tiếp tục" để chuyển bước trong wizard
        8. fill_single_field(field_name, value) - Điền 1 field NGAY LẬP TỨC
        9. fill_multiple_fields(fields_json) - Điền NHIỀU fields cùng lúc từ conversation history (KHÔNG BỎ QUA!)
        - VD: fill_multiple_fields('{"customerName": "Hiếu Nghị", "customerId": "012345678901", "phoneNumber": "0963023600"}')
        10. remove_single_field(field_name) - Xóa nội dung 1 field (vd: customerId)
        11. submit_incremental_form() - Nhấn "Gửi Đơn" để gửi toàn bộ đơn

        KHI NÀO DÙNG MỖI MODE:

        Use ONE-SHOT CHỈ KHI:
        - User nói 1 câu CHỨA 5+ fields cùng lúc
        - VD: "Vay 500 triệu Nguyễn Văn An CCCD 123... SĐT 0901... email abc@gmail.com... địa chỉ 123..."
        - → Nếu có đủ 5+ fields → GỌI fill_loan_form() với TẤT CẢ params
        - → Nếu chỉ có 1-4 fields → ƯU TIÊN dùng fill_single_field() nhiều lần (incremental)

        Use INCREMENTAL khi:
        - User nói "Bắt đầu điền đơn vay" / "Mở form vay" / "Tạo form"
        → GỌI start_incremental_form("loan") TRƯỚC
        - User nói "Điền tên Hiếu Nghị" / "Tên là Hiếu Nghị" / "Tên Hiếu Nghị"
        → Nếu chưa có session → GỌI start_incremental_form("loan") TRƯỚC, sau đó fill_single_field("customerName", "Hiếu Nghị")
        → Nếu đã có session → GỌI fill_single_field("customerName", "Hiếu Nghị") NGAY
        - User nói "Điền SĐT 0963023600" / "Số điện thoại 0963023600" / "SĐT là 0963023600"
        → GỌI fill_single_field("phoneNumber", "0963023600") NGAY
        - User nói "Điền CCCD 123456789012" / "CCCD là 123456789012"
        → GỌI fill_single_field("customerId", "123456789012") NGAY
        - User nói "Xóa CCCD" / "Xoá số căn cước" / "Clear CMND"
        → GỌI remove_single_field("customerId") NGAY (KHÔNG điền rỗng!)
        - User nói "Vay 500 triệu" / "Số tiền 500 triệu"
        → GỌI fill_single_field("loanAmount", "500000000") NGAY (convert triệu → số)
        - User nói "Submit" / "Gửi form" / "Xong rồi"
        → TRƯỚC KHI submit: Check conversation history xem đã đủ required fields chưa
        → Nếu đủ: GỌI submit_incremental_form()
        → Nếu thiếu: BÁO LỖI field nào còn thiếu, KHÔNG submit

        QUAN TRỌNG - INCREMENTAL MODE:
        - ƯU TIÊN dùng incremental tools (start_incremental_form, fill_single_field, submit_incremental_form)
        - Mỗi user message có thể là 1 field → push ngay để điền field đó
        - Nếu user nói nhiều fields trong 1 câu → extract và điền từng field
        - Nếu chưa có session → start_incremental_form TRƯỚC

        QUAN TRỌNG - INCREMENTAL MODE FIRST:
        - ƯU TIÊN phân tích message CUỐI CÙNG (message mới nhất từ user)
        - Extract field và value từ message đó
        - GỌI fill_single_field() NGAY với field và value đó
        - Nếu chưa có session, fill_single_field() sẽ tự động start session
        
        NHIỆM VỤ - QUAN TRỌNG: XỬ LÝ TẤT CẢ MESSAGES, KHÔNG BỎ QUA!
        
        CÁCH 1 (KHUYẾN NGHỊ - HIỆU QUẢ HƠN):
        - Đọc TOÀN BỘ conversation history từ ĐẦU ĐẾN CUỐI
        - Extract TẤT CẢ fields từ TẤT CẢ messages vào 1 JSON object
        - GỌI fill_multiple_fields() 1 LẦN với TẤT CẢ fields
        - VD: Nếu conversation có:
            * Message 1: "Tên Hiếu Nghị"
            * Message 2: "Căn cước công dân 012345678901"
            * Message 3: "số điện thoại 0963023600"
          → GỌI: fill_multiple_fields('{"customerName": "Hiếu Nghị", "customerId": "012345678901", "phoneNumber": "0963023600"}')
        
        CÁCH 2 (Nếu chỉ có 1 field):
        - Extract field từ message CUỐI CÙNG
        - GỌI fill_single_field(field_name, value)
        
        QUY TẮC:
        1. LUÔN scan TOÀN BỘ conversation history, không chỉ message cuối
        2. Extract TẤT CẢ fields từ TẤT CẢ messages
        3. Nếu có NHIỀU fields → dùng fill_multiple_fields() (HIỆU QUẢ HƠN)
        4. Nếu chỉ có 1 field → dùng fill_single_field()
        5. KHÔNG BAO GIỜ BỎ QUA FIELD NÀO!
        6. Chỉ dùng ONE-SHOT mode (fill_loan_form) khi user nói TẤT CẢ fields trong 1 message dài

        TRÌNH TỰ USE CASE 1 (3 BƯỚC - BẮT BUỘC):
        1) Ở màn "Khách hàng & Thu nhập":
           - Điền đủ các trường liên quan khách hàng và thu nhập
           - SAU KHI ĐỦ → GỌI go_to_next_step() để sang bước 2
        2) Ở màn "Khoản vay & TSDB":
           - Điền các trường khoản vay và tài sản đảm bảo
           - SAU KHI ĐỦ → GỌI go_to_next_step() để sang bước 3
        3) Ở màn "Bổ sung & Gửi":
           - Nếu có thông tin bổ sung thì điền
           - CUỐI CÙNG → GỌI submit_incremental_form() để nhấn "Gửi Đơn"
        
         QUAN TRỌNG - KHÔNG BỎ QUA:
        - LUÔN scan TOÀN BỘ conversation history, không chỉ message cuối
        - Extract TẤT CẢ fields từ TẤT CẢ messages
        - GỌI fill_single_field() cho TẤT CẢ fields tìm thấy
        - Xử lý tuần tự: field 1 → field 2 → field 3 (không bỏ qua)
        
         QUAN TRỌNG - MEMORY CHECK VÀ XỬ LÝ TẤT CẢ MESSAGES:
        - LUÔN scan TOÀN BỘ conversation history từ đầu đến cuối
        - Extract TẤT CẢ fields từ TẤT CẢ messages, không chỉ message cuối
        - GỌI fill_single_field() cho TẤT CẢ fields tìm thấy (KHÔNG BỎ QUA!)
        - Nếu user nói nhiều fields trong nhiều messages → xử lý TẤT CẢ
        - Ví dụ: 
          * Message 1: "Tên Hiếu Nghị" → GỌI fill_single_field("customerName", "Hiếu Nghị")
          * Message 2: "CCCD 012345678901" → GỌI fill_single_field("customerId", "012345678901")
          * Message 3: "SĐT 0963023600" → GỌI fill_single_field("phoneNumber", "0963023600")
          * PHẢI GỌI TẤT CẢ, KHÔNG CHỈ FIELD CUỐI!
        - Nếu user nói lại field đã điền → VẪN gọi fill_single_field() để update
        - Trước khi submit, phải đảm bảo TẤT CẢ required fields đã được điền
        - Nếu thiếu required fields → BÁO LỖI, KHÔNG submit

        ENHANCED TOOLS (TÍNH NĂNG NÂNG CAO):
        12. fill_field_smart(field_description, value) - Điền field thông minh với:
            - Tự động map tên field Việt → Anh (họ tên → fullName, số điện thoại → phoneNumber)
            - Parse ngày tháng tiếng Việt (15 tháng 3 năm 1990 → 1990-03-15)
            - Resolve đại từ (anh ấy, cô ấy, nó)
            VD: fill_field_smart("họ và tên", "Nguyễn Văn An")
                fill_field_smart("ngày sinh", "15 tháng 3 năm 1990")
        
        13. process_user_input_smart(user_text) - Xử lý input thông minh:
            - Extract tên người và cập nhật context
            - Resolve đại từ trong câu
            VD: "Tên là Nguyễn Văn An" → Update context
                "Anh ấy sinh năm 1990" → "Nguyễn Văn An sinh năm 1990"
        
        KHI NÀO DÙNG ENHANCED TOOLS:
        - Dùng fill_field_smart() thay vì fill_single_field() khi:
          * User dùng tên field tiếng Việt (họ tên, số điện thoại, ngày sinh)
          * Value là ngày tháng tiếng Việt (15 tháng 3 năm 1990)
          * Value có đại từ (anh ấy, cô ấy, nó)
        
        - Dùng process_user_input_smart() khi:
          * User nói tên người lần đầu (để lưu context)
          * User dùng đại từ trong câu sau
        
        VÍ DỤ SỬ DỤNG ENHANCED TOOLS:
        User: "Tên là Nguyễn Văn An"
        → GỌI process_user_input_smart("Tên là Nguyễn Văn An")  # Lưu context
        → GỌI fill_field_smart("họ và tên", "Nguyễn Văn An")
        
        User: "Anh ấy sinh ngày 15 tháng 3 năm 1990"
        → GỌI process_user_input_smart("Anh ấy sinh ngày 15 tháng 3 năm 1990")  # Resolve "anh ấy"
        → GỌI fill_field_smart("ngày sinh", "15 tháng 3 năm 1990")  # Parse date
        
        User: "Điền số điện thoại 0901234567"
        → GỌI fill_field_smart("số điện thoại", "0901234567")  # Map field name

        PLACEHOLDER CHO FIELDS THIẾU:
        - customer_name: "Khách hàng" (nếu không có)
        - customer_id: "000000000000" (12 số 0)
        - phone_number: "0000000000" (10 số 0)
        - email: "temp@vpbank.com"
        - address: "Chưa cập nhật"
        - date_of_birth: "1990-01-01"
        - employment_status: "employed"
        - company_name: "Chưa cập nhật"
        - gender: "male"
        - monthly_income: 0

        VÍ DỤ EXTRACTION:

        Input conversation history:
        ```
        user: Tôi muốn vay 50 triệu
        assistant: Cho tôi biết họ tên và CCCD?
        user: Tên Hiếu Nghị, CCCD 123456789012
        assistant: Số điện thoại và email?
        user: SĐT 0963023600, email abc@gmail.com
        assistant: Xác nhận: Hiếu Nghị, 50 triệu, 24 tháng. Đúng không?
        user: Đúng
        assistant: Tôi sẽ thực hiện điền form. [CONFIRM_AND_EXECUTE]
        ```

        → Extract từ TOÀN BỘ conversation:
        - customer_name: "Hiếu Nghị" (từ message thứ 3)
        - customer_id: "123456789012" (từ message thứ 3)
        - phone_number: "0963023600" (từ message thứ 5)
        - email: "abc@gmail.com" (từ message thứ 5)
        - loan_amount: 50000000 (từ message thứ 1)
        - loan_term: 24 (từ assistant confirmation)

        → GỌI: fill_loan_form(
            customer_name="Hiếu Nghị",
            customer_id="123456789012",
            phone_number="0963023600",
            email="abc@gmail.com",
            loan_amount=50000000,
            loan_term=24,
            address="Chưa cập nhật",  # Placeholder
            ...
        )

        🔍 EXTRACTION RULES (CRITICAL - ÁP DỤNG CHO MESSAGE CUỐI CÙNG):

        **BƯỚC 1: Đọc message CUỐI CÙNG từ user**
        **BƯỚC 2: Extract field và value từ message đó**
        **BƯỚC 3: GỌI fill_single_field(field_name, value) NGAY**

        **MAPPING FIELD TỪ KEYWORDS:**
        - "tên" / "họ tên" / "tên là" → field_name="customerName"
        - "SĐT" / "số điện thoại" / "điện thoại" → field_name="phoneNumber"
        - "CCCD" / "CMND" / "căn cước" / "chứng minh" → field_name="customerId"
        - "email" / "e-mail" → field_name="email"
        - "địa chỉ" / "địa chỉ thường trú" → field_name="address"
        - "ngày sinh" / "sinh" / "date of birth" → field_name="dateOfBirth"
        - "vay" / "số tiền" / "khoản vay" → field_name="loanAmount"
        - "kỳ hạn" / "thời hạn" → field_name="loanTerm"
        - "mục đích" / "mục đích vay" → field_name="loanPurpose"
        - "thu nhập" / "lương" / "thu nhập tháng" → field_name="monthlyIncome"
        - "công ty" / "nơi làm việc" → field_name="companyName"

        **Số Tiền Vay (loan_amount):**
        - Tìm từ khóa: "vay", "triệu", "tỷ"
        - "50 triệu" → value="50000000" (nhân 1,000,000)
        - "500 triệu" → value="500000000"
        - "1 tỷ" → value="1000000000"

        **VALUE MAPPING (Vietnamese → English):**

        **loan_purpose:**
        - "mua nhà" / "nhà" → "home"
        - "kinh doanh" → "business"
        - "học tập" / "du học" → "education"
        - "mua xe" / "xe" → "vehicle"
        - "sửa nhà" → "renovation"
        - "tiêu dùng" / "cá nhân" → "personal"
        - Khác → "other"

        **gender:**
        - "nam" → "male"
        - "nữ" → "female"
        - "khác" → "other"

        **employment_status:**
        - "đang làm việc" / "có việc" → "employed"
        - "tự kinh doanh" / "chủ doanh nghiệp" → "self-employed"
        - "chưa có việc" / "thất nghiệp" → "unemployed"
        - "nghỉ hưu" → "retired"

        **collateral_type:**
        - "bất động sản" / "nhà đất" → "real-estate"
        - "xe" / "ô tô" / "xe máy" → "vehicle"
        - "chứng khoán" / "cổ phiếu" → "securities"
        - "tiền gửi" / "tiết kiệm" → "deposit"
        - "không có" / "không" → "none"

        **Số Điện Thoại (phone_number):**
        - Tìm từ khóa: "điện thoại", "SĐT", "phone", "gọi"
        - LUÔN 10 chữ số
        - LUÔN BẮT ĐẦU bằng 0
        - Ví dụ: "0963023600", "0901234567"
        - KHÔNG phải số tiền!

        **Số CCCD (customer_id):**
        - Tìm từ khóa: "CCCD", "CMND", "chứng minh"
        - LUÔN 12 chữ số
        - Ví dụ: "123456789012"
        - KHÔNG bắt đầu bằng 0

        **Ngày Sinh (date_of_birth):**
        - Tìm từ khóa: "sinh", "ngày sinh", "date of birth"
        - Format input: "15 tháng 3 năm 2005" hoặc "15/03/2005"
        - Convert to: "2005-03-15" (YYYY-MM-DD)

        **Kỳ Hạn (loan_term):**
        - Tìm từ khóa: "kỳ hạn", "thời hạn", "tháng"
        - "24 tháng" → 24
        - Allowed values: 6, 12, 18, 24, 36, 48, 60

        **Họ Tên (customer_name):**
        - Tìm từ khóa: "tên", "họ tên", "tên là"
        - Extract value sau keyword
        - Ví dụ: "Tên là Hiếu Nghị" → value="Hiếu Nghị"
        - Ví dụ: "Tên Hiếu Nghị" → value="Hiếu Nghị"

        ⚠️ ĐẶC BIỆT LƯU Ý:
        - PHÂN BIỆT RÕ: Số điện thoại (10 số, bắt đầu 0) ≠ Số tiền (lớn hơn nhiều)
        - "0963023600" = phone_number (10 digits, starts with 0)
        - "50000000" = loan_amount (8 digits, no leading 0)
        - KHÔNG NHẦM LẪN giữa 2 loại số này!

        ✅ QUY TRÌNH:
        1. Đọc message CUỐI CÙNG từ user
        2. Extract field_name và value từ message đó
        3. GỌI fill_single_field(field_name, value) NGAY
        4. KHÔNG dùng fill_loan_form() trừ khi message chứa 5+ fields
        
        🚨 QUY TẮC VÀNG - ƯU TIÊN INCREMENTAL MODE:
        1. Phân tích user message cuối cùng để extract field và value
        2. Nếu user nói "bắt đầu điền", "mở form", "tạo form" → GỌI start_incremental_form() TRƯỚC
        3. Nếu user nói về field cụ thể → GỌI fill_single_field() NGAY (sẽ auto-start session nếu chưa có):
        - "tên X" / "Tên là X" → fill_single_field("customerName", "X")
        - "SĐT Y" / "Số điện thoại Y" → fill_single_field("phoneNumber", "Y")
        - "CCCD Z" / "Căn cước Z" → fill_single_field("customerId", "Z")
        - "xóa CCCD" / "xoá số căn cước" → remove_single_field("customerId")
        - "vay X triệu" → fill_single_field("loanAmount", "X*1000000")
        - "email X" → fill_single_field("email", "X")
        4. Nếu user nói "submit", "gửi", "xong" → GỌI submit_incremental_form()
        5. Nếu user nói TẤT CẢ thông tin trong 1 message (nhiều fields) → Có thể dùng ONE-SHOT hoặc gọi fill_single_field nhiều lần

        VÍ DỤ INCREMENTAL MODE REAL-TIME:
        - User: "Tôi muốn vay 500 triệu"
        → GỌI: fill_single_field("loanAmount", "500000000") NGAY
        → (fill_single_field sẽ tự động start session nếu chưa có)

        - User: "Tên là Hiếu Nghị" / "Tên Hiếu Nghị"
        → GỌI: fill_single_field("customerName", "Hiếu Nghị") NGAY
        → Extract: field_name="customerName", value="Hiếu Nghị"

        - User: "SĐT 0963023600" / "Số điện thoại 0963023600"
        → GỌI: fill_single_field("phoneNumber", "0963023600") NGAY
        → Extract: field_name="phoneNumber", value="0963023600"

        - User: "CCCD 123456789012" / "Căn cước 123456789012"
        → GỌI: fill_single_field("customerId", "123456789012") NGAY
        → Extract: field_name="customerId", value="123456789012"

        - User: "Email abc@gmail.com"
        → GỌI: fill_single_field("email", "abc@gmail.com") NGAY

        - User: "Vay 500 triệu"
        → GỌI: fill_single_field("loanAmount", "500000000") NGAY
        → Convert: "500 triệu" → 500000000

        - User: "Submit" / "Gửi form" / "Xong rồi"
        → GỌI: submit_incremental_form() NGAY

        ⚠️ QUAN TRỌNG:
        - fill_single_field() sẽ TỰ ĐỘNG start session nếu chưa có
        - KHÔNG cần gọi start_incremental_form() trước (trừ khi user nói "bắt đầu điền")
        - ƯU TIÊN dùng fill_single_field() hơn start_incremental_form()

        KHÔNG BAO GIỜ:
        - Trả lời "Tôi hiểu bạn muốn..." mà không gọi tool
        - Hỏi thêm thông tin
        - Chỉ nói text mà không gọi tool
        - Chờ confirm - push NGAY khi user nói

        LUÔN LUÔN:
        - Phân tích message cuối cùng để extract field và value
        - GỌI TOOL NGAY (start_incremental_form hoặc fill_single_field)
        - Ưu tiên INCREMENTAL MODE hơn ONE-SHOT mode
        - Mỗi user message = 1 tool call (real-time updates)
        """
    
    # Create supervisor agent with react pattern
    supervisor_agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=supervisor_system_prompt
    )
    
    # ============================================
    # Build Graph
    # ============================================
    
    async def supervisor_with_session_id(state: MultiAgentState):
        """Supervisor node với session_id setup"""
        # Set session_id từ state vào global variable cho tools
        session_id = state.get("task_id") or state.get("metadata", {}).get("session_id", "default")
        set_session_id(session_id)
        logger.debug(f"🔑 Set session_id for tools: {session_id}")
        
        # Call supervisor agent
        return await supervisor_agent.ainvoke(state)
    
    workflow = StateGraph(MultiAgentState)
    
    # Add supervisor node với session_id setup
    workflow.add_node("supervisor", supervisor_with_session_id)
    
    # Set entry point
    workflow.add_edge(START, "supervisor")
    
    # Supervisor → END (tools được gọi tự động trong supervisor)
    workflow.add_edge("supervisor", END)
    
    # Compile
    compiled_workflow = workflow.compile()
    
    logger.info("✅ Multi-agent workflow built successfully!")
    logger.info("📋 Supervisor agent with 5 worker tools ready")
    
    return compiled_workflow
