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

# Import browser_agent using absolute import to avoid issues
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from browser_agent import browser_agent


# ============================================
# BROWSER TOOLS - Các tools để điền form
# ============================================

# ============================================
# INCREMENTAL MODE TOOLS (NEW!)
# ============================================

@tool
async def start_incremental_form(form_type: str) -> str:
    """
    Bắt đầu session điền form incremental - Mở browser và giữ mở.
    
    Args:
        form_type: Loại form (loan/crm/hr/compliance/operations)
        
    Returns:
        Kết quả mở form
    """
    import os
    
    # Get form URL
    urls = {
        "loan": os.getenv("LOAN_FORM_URL", "http://use-case-1-loan-origination.s3-website-us-west-2.amazonaws.com"),
        "crm": os.getenv("CRM_FORM_URL", "http://use-case-2-crm-update.s3-website-us-west-2.amazonaws.com"),
        "hr": os.getenv("HR_FORM_URL", "http://use-case-3-hr-workflow.s3-website-us-west-2.amazonaws.com"),
        "compliance": os.getenv("COMPLIANCE_FORM_URL", "http://use-case-4-compliance-reporting.s3-website-us-west-2.amazonaws.com"),
        "operations": os.getenv("OPERATIONS_FORM_URL", "http://use-case-5-operations-validation.s3-website-us-west-2.amazonaws.com")
    }
    
    form_url = urls.get(form_type)
    if not form_url:
        return f"❌ Invalid form type: {form_type}"
    
    logger.info(f"🚀 Starting incremental form: {form_type}")
    
    result = await browser_agent.start_form_session(form_url, form_type)
    
    if result.get("success"):
        return f"✅ Đã mở form {form_type}. Bạn có thể bắt đầu điền từng field bằng cách nói: 'Điền tên là X', 'Điền SĐT là Y'..."
    else:
        return f"❌ Lỗi mở form: {result.get('error')}"


@tool
async def fill_single_field(field_name: str, field_value: str) -> str:
    """
    Điền 1 field cụ thể trong form đang mở (incremental mode).
    
    Args:
        field_name: Tên field HTML (customerName, phoneNumber, email, loanAmount, etc.)
        field_value: Giá trị cần điền
        
    Returns:
        Kết quả điền field
    """
    logger.info(f"📝 Incremental fill: {field_name} = {field_value}")
    
    result = await browser_agent.fill_field_incremental(field_name, field_value)
    
    if result.get("success"):
        fields_count = result.get("fields_filled", 0)
        return f"✅ Đã điền {field_name}. Tổng đã điền: {fields_count} fields. Tiếp tục điền hoặc nói 'Submit' để gửi."
    else:
        return f"❌ Lỗi điền field: {result.get('error')}"


@tool
async def submit_incremental_form() -> str:
    """
    Submit form đang được điền incremental.
    
    Returns:
        Kết quả submit
    """
    logger.info(f"🚀 Submitting incremental form...")
    
    result = await browser_agent.submit_form_incremental()
    
    if result.get("success"):
        fields_count = result.get("fields_filled", 0)
        return f"✅ Form đã được submit thành công! Đã điền {fields_count} fields."
    else:
        return f"❌ Lỗi submit form: {result.get('error')}"


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
    logger.info(f"🏦 Filling LOAN form for: {customer_name}")
    
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
    
    try:
        # Execute browser task
        import asyncio
        import os
        
        # Get form URL from environment
        form_url = os.getenv("LOAN_FORM_URL", "http://use-case-1-loan-origination.s3-website-us-west-2.amazonaws.com")
        
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
    
    logger.info(f"📞 Filling CRM form for: {customer_name}")
    
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
        form_url = os.getenv("CRM_FORM_URL", "http://use-case-2-crm-update.s3-website-us-west-2.amazonaws.com")
        
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
        form_url = os.getenv("HR_FORM_URL", "http://use-case-3-hr-workflow.s3-website-us-west-2.amazonaws.com")
        
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
        form_url = os.getenv("COMPLIANCE_FORM_URL", "http://use-case-4-compliance-reporting.s3-website-us-west-2.amazonaws.com")
        
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
        form_url = os.getenv("OPERATIONS_FORM_URL", "http://use-case-5-operations-validation.s3-website-us-west-2.amazonaws.com")
        
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
        
        # Incremental mode (3 tools - NEW!)
        start_incremental_form,
        fill_single_field,
        submit_incremental_form
    ]
    
    supervisor_system_prompt = """Bạn là SUPERVISOR AGENT - Phân tích message và GỌI TOOL phù hợp!

BẠN CÓ 8 TOOLS (2 MODES):

🔵 **ONE-SHOT MODE** (5 tools - khi có ĐẦY ĐỦ thông tin):
1. fill_loan_form - Điền TẤT CẢ fields đơn vay cùng lúc
2. fill_crm_form - Điền TẤT CẢ fields CRM cùng lúc
3. fill_hr_form - Điền TẤT CẢ fields HR cùng lúc
4. fill_compliance_form - Điền TẤT CẢ fields compliance cùng lúc
5. fill_operations_form - Điền TẤT CẢ fields operations cùng lúc

🟢 **INCREMENTAL MODE** (3 tools - khi điền TỪNG FIELD):
6. start_incremental_form(form_type) - Mở browser, navigate to form, GIỮ MỞ
7. fill_single_field(field_name, value) - Điền 1 field (có thể gọi NHIỀU LẦN)
8. submit_incremental_form() - Submit form sau khi điền xong

KHI NÀO DÙNG MỖI MODE:

📋 **Use ONE-SHOT** khi:
- User nói 1 câu chứa NHIỀU thông tin
- VD: "Vay 500 triệu Nguyễn Văn An CCCD 123... SĐT 0901..."
- → GỌI fill_loan_form() với TẤT CẢ params

📝 **Use INCREMENTAL** khi:
- User nói "Bắt đầu điền đơn vay" / "Mở form vay"
  → GỌI start_incremental_form("loan")
- User nói "Điền tên Hiếu Nghị"
  → GỌI fill_single_field("customerName", "Hiếu Nghị")
- User nói "Điền SĐT 0963023600"
  → GỌI fill_single_field("phoneNumber", "0963023600")
- User nói "Submit" / "Gửi form"
  → GỌI submit_incremental_form()

⚠️ QUAN TRỌNG:
        - Bạn nhận TOÀN BỘ conversation history (multiple user messages)
        - User đã XÁC NHẬN thông tin qua Voice Agent
        - Message cuối cùng chứa "[CONFIRM_AND_EXECUTE]" = User đã đồng ý

        NHIỆM VỤ:
        1. Phân tích TOÀN BỘ conversation history
        2. Trích xuất thông tin từ TẤT CẢ user messages
        3. GỌI TOOL phù hợp với thông tin đã extract
        4. Dùng PLACEHOLDER cho fields vẫn còn thiếu

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

        🔍 EXTRACTION RULES (CRITICAL - Phân Biệt Rõ Ràng):

        **Số Tiền Vay (loan_amount, monthlyIncome, collateralValue):**
        - Tìm từ khóa: "vay", "triệu", "tỷ", "thu nhập", "lương", "tài sản"
        - "50 triệu" → 50000000 (nhân 1,000,000)
        - "500 triệu" → 500000000
        - "1 tỷ" → 1000000000
        - "25 triệu/tháng" → monthly_income = 25000000
        - "460 nghìn" hoặc "460000" → 460000 (giữ nguyên nếu đã là số)

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
        - Ví dụ: "Nguyễn Văn An", "Hiếu Nghị"

        ⚠️ ĐẶC BIỆT LƯU Ý:
        - PHÂN BIỆT RÕ: Số điện thoại (10 số, bắt đầu 0) ≠ Số tiền (lớn hơn nhiều)
        - "0963023600" = phone_number (10 digits, starts with 0)
        - "50000000" = loan_amount (8 digits, no leading 0)
        - KHÔNG NHẦM LẪN giữa 2 loại số này!

        ✅ LUÔN GỌI TOOL với thông tin đã extract!
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
    
    workflow = StateGraph(MultiAgentState)
    
    # Add supervisor node
    workflow.add_node("supervisor", supervisor_agent)
    
    # Set entry point
    workflow.add_edge(START, "supervisor")
    
    # Supervisor → END (tools được gọi tự động trong supervisor)
    workflow.add_edge("supervisor", END)
    
    # Compile
    compiled_workflow = workflow.compile()
    
    logger.info("✅ Multi-agent workflow built successfully!")
    logger.info("📋 Supervisor agent with 5 worker tools ready")
    
    return compiled_workflow
