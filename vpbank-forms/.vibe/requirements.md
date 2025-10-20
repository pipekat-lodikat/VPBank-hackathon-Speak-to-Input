# Requirements Document - VPBank Forms

## Business Requirements

### Use Case 1 – Loan Origination & KYC Automation
**Department**: Retail Lending  
**Current Problem**: Manual entry of 20–30 fields per application in LOS causes delay and error propagation.  
**Solution**: RM states: "Điền khách hàng Nguyễn Văn An vay 500 triệu, kỳ hạn 24 tháng."  
AI parses and fills LOS form automatically, requests confirmation, and submits.  
**Expected Impact**: 
- ↓ 80% form time
- ↓ 80% error rate
- Saving ₫3–4B/year per 1,000 RMs

**Required Fields**:
- Customer name (text)
- Customer ID/CCCD (text)
- Phone number (text)
- Email (text)
- Address (textarea)
- Loan amount (number)
- Loan term (select: 6, 12, 18, 24, 36, 48, 60 months)
- Loan purpose (select)
- Monthly income (number)
- Employment status (select)
- Date of application (date)
- Collateral type (select)
- Additional notes (textarea)

---

### Use Case 2 – CRM Update & Customer Interaction Logging
**Department**: Customer Service  
**Current Problem**: Post-call updates take ~2 min/call.  
**Solution**: "Cập nhật địa chỉ khách Nguyễn Văn Bình thành 25A Nguyễn Trãi."  
AI updates CRM record instantly.  
**Expected Impact**:
- ↑ 25% call throughput
- ↓ 90% data inconsistency

**Required Fields**:
- Customer name (text)
- Customer ID (text)
- Phone number (text)
- Email (text)
- Address (textarea)
- Interaction type (select: Call, Email, Visit, Chat)
- Interaction date (date)
- Agent name (text)
- Issue category (select)
- Resolution status (select: Resolved, Pending, Escalated)
- Notes (textarea)

---

### Use Case 3 – HR & Internal Workflow Automation
**Department**: Human Resources  
**Current Problem**: Staff fill multiple administrative forms manually.  
**Solution**: "Tạo đơn nghỉ phép từ 22 đến 24 tháng 10, lý do cá nhân."  
AI identifies the correct HR form, populates, validates, and submits.  
**Expected Impact**:
- ↓ 80% manual time
- ↑ employee satisfaction from 3.8→4.6/5

**Required Fields**:
- Employee name (text)
- Employee ID (text)
- Department (select)
- Request type (select: Leave, Training, Equipment, Other)
- Start date (date)
- End date (date)
- Reason (textarea)
- Approval status (select: Pending, Approved, Rejected)
- Manager name (text)
- Submission date (date)

---

### Use Case 4 – Compliance & Audit Reporting
**Department**: Risk & Compliance  
**Current Problem**: AML/KYC reports are manually compiled; prone to data mismatch.  
**Solution**: "Điền báo cáo AML tháng 9, trạng thái hoàn thành, không vi phạm."  
AI fills and validates compliance template.  
**Expected Impact**:
- ↓ 80% report prep time
- ↑ accuracy to 99%
- ↓ audit rework > 80%

**Required Fields**:
- Report ID (text)
- Report type (select: AML, KYC, Risk Assessment, Other)
- Reporting period (date)
- Status (select: In Progress, Completed, Under Review)
- Compliance officer (text)
- Violations found (select: None, Minor, Major)
- Number of cases reviewed (number)
- High-risk cases (number)
- Actions taken (textarea)
- Submission date (date)
- Additional notes (textarea)

---

### Use Case 5 – Operations & Transaction Validation
**Department**: Operations  
**Current Problem**: Manual reconciliation across systems.  
**Solution**: "Kiểm tra giao dịch khách Nguyễn Thị Hoa ngày 17 tháng 10, số tiền 350 triệu."  
AI retrieves transaction data, reads summary, awaits confirmation.  
**Expected Impact**:
- ↓ 50% validation time
- ↑ accuracy to 99%

**Required Fields**:
- Customer name (text)
- Customer ID (text)
- Transaction ID (text)
- Transaction date (date)
- Transaction amount (number)
- Transaction type (select: Deposit, Withdrawal, Transfer, Payment)
- Channel (select: Branch, ATM, Online, Mobile)
- Status (select: Pending, Completed, Failed)
- Validation result (select: Valid, Invalid, Needs Review)
- Reviewer name (text)
- Notes (textarea)

---

## Technical Requirements

### Functional Requirements
1. All forms must be accessible via standard web browsers
2. Forms must support both manual entry and AI-powered auto-fill
3. Client-side validation before submission
4. Confirmation dialog before final submission
5. Success/error feedback after submission
6. Forms must be responsive (mobile, tablet, desktop)

### Non-Functional Requirements
1. **Performance**: Form load time < 1 second
2. **Accessibility**: WCAG 2.1 Level AA compliance
3. **Browser Support**: Chrome, Firefox, Safari, Edge (latest 2 versions)
4. **Security**: Input sanitization, XSS prevention
5. **Maintainability**: Clean, documented code

### AI Integration Requirements
1. Forms must expose JavaScript API for programmatic filling
2. Each field must have unique ID for targeting
3. Support for validation before submission
4. Event listeners for AI monitoring
5. Error handling and fallback mechanisms
