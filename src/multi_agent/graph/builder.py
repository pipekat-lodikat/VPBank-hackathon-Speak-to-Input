"""
LangGraph Multi-Agent Workflow - Supervisor Pattern
Sử dụng Supervisor Agent với tools để điều phối 5 use cases
Ref: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/
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
    gender: str = "male"
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
        "applicationDate": datetime.now().strftime("%Y-%m-%d"),
        "employmentStatus": employment_status,
        "companyName": company_name,
        "monthlyIncome": str(monthly_income),
        "collateralType": "none"  # Default value
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
    interaction_date: str,
    issue_description: str,
    resolution: str,
    agent_name: str,
    satisfaction_rating: int
) -> str:
    """
    Cập nhật thông tin CRM (Use Case 2).
    
    Args:
        customer_name: Tên khách hàng
        customer_id: Mã khách hàng
        interaction_type: Loại tương tác (Call/Email/Visit)
        interaction_date: Ngày tương tác
        issue_description: Mô tả vấn đề
        resolution: Cách giải quyết
        agent_name: Tên nhân viên xử lý
        satisfaction_rating: Đánh giá hài lòng (1-5)
        
    Returns:
        Kết quả cập nhật CRM
    """
    logger.info(f"📞 Filling CRM form for: {customer_name}")
    
    form_data = {
        "customerName": customer_name,
        "customerId": customer_id,
        "interactionType": interaction_type,
        "interactionDate": interaction_date,
        "issueDescription": issue_description,
        "resolution": resolution,
        "agentName": agent_name,
        "satisfactionRating": satisfaction_rating
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
    department: str
) -> str:
    """
    Điền form HR workflow (Use Case 3).
    
    Args:
        employee_name: Tên nhân viên
        employee_id: Mã nhân viên
        request_type: Loại yêu cầu (Leave/Training/Other)
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc
        reason: Lý do
        manager_name: Tên quản lý
        department: Phòng ban
        
    Returns:
        Kết quả điền form HR
    """
    logger.info(f"👤 Filling HR form for: {employee_name}")
    
    form_data = {
        "employeeName": employee_name,
        "employeeId": employee_id,
        "requestType": request_type,
        "startDate": start_date,
        "endDate": end_date,
        "reason": reason,
        "managerName": manager_name,
        "department": department
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
    report_period: str,
    submitted_by: str,
    submission_date: str,
    violations_found: int,
    risk_level: str,
    compliance_status: str,
    notes: str
) -> str:
    """
    Điền form báo cáo tuân thủ (Use Case 4).
    
    Args:
        report_type: Loại báo cáo (AML/KYC/GDPR)
        report_period: Kỳ báo cáo
        submitted_by: Người nộp
        submission_date: Ngày nộp
        violations_found: Số vi phạm phát hiện
        risk_level: Mức độ rủi ro (Low/Medium/High)
        compliance_status: Trạng thái (Compliant/Non-Compliant)
        notes: Ghi chú
        
    Returns:
        Kết quả điền form compliance
    """
    logger.info(f"📋 Filling COMPLIANCE form: {report_type}")
    
    form_data = {
        "reportType": report_type,
        "reportPeriod": report_period,
        "submittedBy": submitted_by,
        "submissionDate": submission_date,
        "violationsFound": violations_found,
        "riskLevel": risk_level,
        "complianceStatus": compliance_status,
        "notes": notes
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
    transaction_date: str,
    customer_name: str,
    transaction_amount: int,
    transaction_type: str,
    beneficiary_name: str,
    beneficiary_account: str,
    transaction_status: str,
    verified_by: str,
    fraud_score: int,
    notes: str
) -> str:
    """
    Điền form kiểm tra giao dịch (Use Case 5).
    
    Args:
        transaction_id: Mã giao dịch
        transaction_date: Ngày giao dịch
        customer_name: Tên khách hàng
        transaction_amount: Số tiền (VNĐ)
        transaction_type: Loại giao dịch
        beneficiary_name: Tên người thụ hưởng
        beneficiary_account: Tài khoản người thụ hưởng
        transaction_status: Trạng thái (Pending/Completed/Failed)
        verified_by: Người xác minh
        fraud_score: Điểm nghi ngờ gian lận (0-100)
        notes: Ghi chú
        
    Returns:
        Kết quả điền form operations
    """
    logger.info(f"� Filling OPERATIONS form: {transaction_id}")
    
    form_data = {
        "transactionId": transaction_id,
        "transactionDate": transaction_date,
        "customerName": customer_name,
        "transactionAmount": transaction_amount,
        "transactionType": transaction_type,
        "beneficiaryName": beneficiary_name,
        "beneficiaryAccount": beneficiary_account,
        "transactionStatus": transaction_status,
        "verifiedBy": verified_by,
        "fraudScore": fraud_score,
        "notes": notes
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
        fill_loan_form,
        fill_crm_form,
        fill_hr_form,
        fill_compliance_form,
        fill_operations_form
    ]
    
    supervisor_system_prompt = """Bạn là SUPERVISOR AGENT - Phân tích message và GỌI TOOL khi ĐỦ ĐIỀU KIỆN!

BẠN CÓ 5 TOOLS:
1. fill_loan_form - Đơn vay vốn & KYC
2. fill_crm_form - CRM update
3. fill_hr_form - HR workflow  
4. fill_compliance_form - Báo cáo tuân thủ
5. fill_operations_form - Kiểm tra giao dịch

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

**Số Tiền Vay (loan_amount, monthlyIncome):**
- Tìm từ khóa: "vay", "triệu", "tỷ", "thu nhập", "lương"
- "50 triệu" → 50000000 (nhân 1,000,000)
- "500 triệu" → 500000000
- "1 tỷ" → 1000000000
- "25 triệu/tháng" → monthly_income = 25000000

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
