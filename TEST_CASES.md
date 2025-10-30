# 🧪 TEST CASES - VPBANK MULTI-AGENT VOICE BOT

Các test cases để kiểm tra 5 use cases của hệ thống multi-agent.  
Mỗi test case là một **lệnh voice duy nhất** chứa đủ thông tin để điền form.

---

## 📋 USE CASE 1: LOAN ORIGINATION & KYC

### Test Case 1.1: Đơn vay mua nhà (Đầy đủ thông tin)

**Voice Command:**
```
Tạo đơn vay cho khách hàng Nguyễn Văn An, số CCCD 012345678901, 
sinh ngày 15 tháng 3 năm 1985, địa chỉ số 123 đường Lê Lợi, Quận 1, TP.HCM, 
số điện thoại 0901234567, email nguyenvanan@gmail.com. 
Khách muốn vay 500 triệu đồng để mua nhà, kỳ hạn 24 tháng. 
Nghề nghiệp là kỹ sư phần mềm, làm việc tại công ty FPT Software, 
thu nhập hàng tháng 30 triệu đồng.
```

**Expected Fields:**
- Customer Name: Nguyễn Văn An
- ID Number: 012345678901
- Date of Birth: 15/03/1985
- Address: 123 đường Lê Lợi, Quận 1, TP.HCM
- Phone: 0901234567
- Email: nguyenvanan@gmail.com
- Loan Amount: 500,000,000 VNĐ
- Loan Purpose: Mua nhà
- Loan Term: 24 tháng
- Occupation: Kỹ sư phần mềm
- Workplace: FPT Software
- Monthly Income: 30,000,000 VNĐ

**Expected Result:** ✅ Form được điền đầy đủ và submit thành công

---

### Test Case 1.2: Đơn vay kinh doanh

**Voice Command:**
```
Điền đơn vay vốn cho chị Trần Thị Bình, CCCD số 098765432109, 
ngày sinh 20/07/1990, ở 456 Nguyễn Huệ, Quận 5, Sài Gòn, 
điện thoại 0912345678, email tranbinhbiz@yahoo.com. 
Chị cần vay 1 tỷ 200 triệu để kinh doanh nhà hàng, vay trong 36 tháng. 
Chị là chủ doanh nghiệp, tên công ty là Nhà Hàng Hương Việt, 
thu nhập mỗi tháng khoảng 50 triệu.
```

**Expected Fields:**
- Customer Name: Trần Thị Bình
- ID Number: 098765432109
- Date of Birth: 20/07/1990
- Address: 456 Nguyễn Huệ, Quận 5, Sài Gòn
- Phone: 0912345678
- Email: tranbinhbiz@yahoo.com
- Loan Amount: 1,200,000,000 VNĐ
- Loan Purpose: Kinh doanh nhà hàng
- Loan Term: 36 tháng
- Occupation: Chủ doanh nghiệp
- Workplace: Nhà Hàng Hương Việt
- Monthly Income: 50,000,000 VNĐ

**Expected Result:** ✅ Form được điền và validation pass

---

### Test Case 1.3: Đơn vay du học

**Voice Command:**
```
Làm đơn vay cho anh Phạm Minh Cường, CCCD 011223344556, sinh 10/11/1998, 
địa chỉ 789 Lê Văn Sỹ, Phú Nhuận, TP.HCM, SĐT 0923456789, 
email cuongpham98@gmail.com. Anh vay 800 triệu cho con đi du học, 
kỳ hạn 60 tháng. Nghề giáo viên, dạy tại trường THPT Nguyễn Du, 
lương 25 triệu mỗi tháng.
```

**Expected Fields:**
- Customer Name: Phạm Minh Cường
- ID Number: 011223344556
- Date of Birth: 10/11/1998
- Address: 789 Lê Văn Sỹ, Phú Nhuận, TP.HCM
- Phone: 0923456789
- Email: cuongpham98@gmail.com
- Loan Amount: 800,000,000 VNĐ
- Loan Purpose: Du học
- Loan Term: 60 tháng
- Occupation: Giáo viên
- Workplace: THPT Nguyễn Du
- Monthly Income: 25,000,000 VNĐ

**Expected Result:** ✅ Form submit thành công

---

## 📋 USE CASE 2: CRM UPDATE & CUSTOMER INTERACTION

### Test Case 2.1: Cập nhật địa chỉ khách hàng

**Voice Command:**
```
Cập nhật thông tin khách hàng Nguyễn Văn Bình, mã khách hàng CUS001. 
Loại tương tác là cập nhật thông tin, ngày 25 tháng 10 năm 2025. 
Khách hàng yêu cầu đổi địa chỉ mới thành 25A Nguyễn Trãi, Quận 1, TP.HCM 
vì đã chuyển nhà. Đã xử lý xong, khách hàng hài lòng. 
Nhân viên xử lý là Lê Thị Hoa, đánh giá 5 sao.
```

**Expected Fields:**
- Customer Name: Nguyễn Văn Bình
- Customer ID: CUS001
- Interaction Type: Cập nhật thông tin
- Interaction Date: 25/10/2025
- Issue Description: Khách hàng yêu cầu đổi địa chỉ mới thành 25A Nguyễn Trãi, Quận 1, TP.HCM vì đã chuyển nhà
- Resolution: Đã xử lý xong, khách hàng hài lòng
- Agent Name: Lê Thị Hoa
- Satisfaction Rating: 5

**Expected Result:** ✅ CRM form updated successfully

---

### Test Case 2.2: Khiếu nại dịch vụ

**Voice Command:**
```
Ghi nhận tương tác khách hàng Trần Minh Tuấn, ID là CUS002. 
Khiếu nại về dịch vụ vào ngày hôm nay 30 tháng 10. 
Khách phản ánh thẻ tín dụng bị khóa đột ngột mà không thông báo trước, 
gây bất tiện khi thanh toán. Đã mở khóa và xin lỗi khách hàng, 
giải thích do hệ thống phát hiện giao dịch bất thường. 
Nhân viên Phạm Văn Nam xử lý, khách đánh giá 4 điểm.
```

**Expected Fields:**
- Customer Name: Trần Minh Tuấn
- Customer ID: CUS002
- Interaction Type: Khiếu nại
- Interaction Date: 30/10/2025
- Issue Description: Thẻ tín dụng bị khóa đột ngột mà không thông báo trước, gây bất tiện khi thanh toán
- Resolution: Đã mở khóa và xin lỗi khách hàng, giải thích do hệ thống phát hiện giao dịch bất thường
- Agent Name: Phạm Văn Nam
- Satisfaction Rating: 4

**Expected Result:** ✅ Complaint logged successfully

---

### Test Case 2.3: Tư vấn sản phẩm

**Voice Command:**
```
Lưu tương tác với khách Lê Thị Mai, mã CUS003. 
Tư vấn sản phẩm ngày 28 tháng 10 năm 2025. 
Khách hỏi về gói tiết kiệm có lãi suất cao cho kỳ hạn 12 tháng. 
Đã tư vấn gói Tiết Kiệm Vàng với lãi suất 6.5% năm, 
khách hàng hài lòng và đồng ý mở tài khoản. 
Nhân viên tư vấn Nguyễn Thị Lan, rating 5 sao.
```

**Expected Fields:**
- Customer Name: Lê Thị Mai
- Customer ID: CUS003
- Interaction Type: Tư vấn
- Interaction Date: 28/10/2025
- Issue Description: Khách hỏi về gói tiết kiệm có lãi suất cao cho kỳ hạn 12 tháng
- Resolution: Đã tư vấn gói Tiết Kiệm Vàng với lãi suất 6.5% năm, khách hàng hài lòng và đồng ý mở tài khoản
- Agent Name: Nguyễn Thị Lan
- Satisfaction Rating: 5

**Expected Result:** ✅ Consultation recorded

---

## 📋 USE CASE 3: HR & INTERNAL WORKFLOW

### Test Case 3.1: Đơn nghỉ phép

**Voice Command:**
```
Tạo đơn nghỉ phép cho nhân viên Trần Thị Cúc, mã NV001. 
Nghỉ phép từ ngày 22 đến 24 tháng 10 năm 2025, tổng 3 ngày. 
Lý do nghỉ là việc gia đình cá nhân. Công việc đã bàn giao cho 
đồng nghiệp Nguyễn Văn Đức phụ trách. Phòng ban Kinh Doanh, 
người quản lý trực tiếp là Lê Minh Hoàng.
```

**Expected Fields:**
- Employee Name: Trần Thị Cúc
- Employee ID: NV001
- Request Type: Nghỉ phép
- Start Date: 22/10/2025
- End Date: 24/10/2025
- Number of Days: 3
- Reason: Việc gia đình cá nhân
- Handover: Nguyễn Văn Đức
- Department: Kinh Doanh
- Manager: Lê Minh Hoàng

**Expected Result:** ✅ Leave request submitted

---

### Test Case 3.2: Đăng ký đào tạo

**Voice Command:**
```
Đăng ký khóa đào tạo cho nhân viên Phạm Minh Tuấn, mã số NV002. 
Đăng ký đào tạo kỹ năng, từ 5 đến 7 tháng 11 năm 2025, kéo dài 3 ngày. 
Lý do là nâng cao kỹ năng chăm sóc khách hàng và xử lý khiếu nại. 
Phòng Chăm Sóc Khách Hàng, quản lý là bà Trần Thu Hà. 
Công việc trong thời gian đào tạo sẽ do anh Lê Văn Nam đảm nhận.
```

**Expected Fields:**
- Employee Name: Phạm Minh Tuấn
- Employee ID: NV002
- Request Type: Đào tạo
- Start Date: 05/11/2025
- End Date: 07/11/2025
- Number of Days: 3
- Reason: Nâng cao kỹ năng chăm sóc khách hàng và xử lý khiếu nại
- Handover: Lê Văn Nam
- Department: Chăm Sóc Khách Hàng
- Manager: Trần Thu Hà

**Expected Result:** ✅ Training registration complete

---

### Test Case 3.3: Đơn xin tăng ca

**Voice Command:**
```
Làm đơn tăng ca cho nhân viên Nguyễn Thị Hương, ID NV003. 
Đăng ký tăng ca từ 1 đến 3 tháng 11, ba ngày cuối tuần. 
Lý do tăng ca để hoàn thành dự án triển khai hệ thống mới cho khách hàng. 
Không cần bàn giao vì làm thêm ngoài giờ. Phòng IT, 
quản lý dự án Phạm Đức Anh phê duyệt.
```

**Expected Fields:**
- Employee Name: Nguyễn Thị Hương
- Employee ID: NV003
- Request Type: Tăng ca
- Start Date: 01/11/2025
- End Date: 03/11/2025
- Number of Days: 3
- Reason: Hoàn thành dự án triển khai hệ thống mới cho khách hàng
- Handover: Không cần bàn giao
- Department: IT
- Manager: Phạm Đức Anh

**Expected Result:** ✅ Overtime request logged

---

## 📋 USE CASE 4: COMPLIANCE & REGULATORY REPORTING

### Test Case 4.1: Báo cáo AML tháng 9

**Voice Command:**
```
Điền báo cáo tuân thủ AML và chống rửa tiền cho tháng 9 năm 2025. 
Kỳ báo cáo từ 1 đến 30 tháng 9. Không phát hiện vi phạm nào, 
tổng số giao dịch kiểm tra là 1250 giao dịch. Mức độ rủi ro thấp. 
Nhân viên tuân thủ Lê Văn Cường lập báo cáo, 
người phê duyệt là Trưởng phòng Trần Thị Mai, đã phê duyệt ngày 5 tháng 10.
```

**Expected Fields:**
- Report Type: AML
- Period Start: 01/09/2025
- Period End: 30/09/2025
- Violations Found: 0
- Total Transactions: 1250
- Risk Level: Thấp
- Compliance Officer: Lê Văn Cường
- Approver: Trần Thị Mai
- Approval Date: 05/10/2025

**Expected Result:** ✅ AML report filed

---

### Test Case 4.2: Báo cáo KYC quý 3

**Voice Command:**
```
Lập báo cáo tuân thủ KYC cho quý 3 năm 2025, 
từ ngày 1 tháng 7 đến 30 tháng 9. Phát hiện 3 trường hợp vi phạm, 
khách hàng không cập nhật giấy tờ đúng hạn. Đã xử lý và yêu cầu bổ sung. 
Tổng số hồ sơ KYC kiểm tra là 850 hồ sơ, mức độ rủi ro trung bình. 
Nhân viên Nguyễn Thị Lan lập, Phó Giám Đốc Phạm Văn Hùng phê duyệt 
vào ngày 10 tháng 10.
```

**Expected Fields:**
- Report Type: KYC
- Period Start: 01/07/2025
- Period End: 30/09/2025
- Violations Found: 3
- Total Transactions: 850
- Risk Level: Trung bình
- Compliance Officer: Nguyễn Thị Lan
- Approver: Phạm Văn Hùng
- Approval Date: 10/10/2025

**Expected Result:** ✅ KYC report submitted

---

### Test Case 4.3: Báo cáo GDPR

**Voice Command:**
```
Tạo báo cáo tuân thủ GDPR và bảo vệ dữ liệu cá nhân tháng 10 năm 2025. 
Kỳ báo cáo từ 1 đến 31 tháng 10. Không có vi phạm, 
đã xử lý 45 yêu cầu truy cập dữ liệu và 12 yêu cầu xóa dữ liệu từ khách hàng. 
Mức độ rủi ro thấp. Chuyên viên bảo vệ dữ liệu Trần Minh Tuấn lập báo cáo, 
Trưởng phòng Pháp chế Lê Thị Hoa phê duyệt ngày 2 tháng 11.
```

**Expected Fields:**
- Report Type: GDPR
- Period Start: 01/10/2025
- Period End: 31/10/2025
- Violations Found: 0
- Total Transactions: 57 (45 + 12 requests)
- Risk Level: Thấp
- Compliance Officer: Trần Minh Tuấn
- Approver: Lê Thị Hoa
- Approval Date: 02/11/2025

**Expected Result:** ✅ GDPR compliance report saved

---

## 📋 USE CASE 5: OPERATIONS & TRANSACTION VALIDATION

### Test Case 5.1: Kiểm tra giao dịch chuyển khoản

**Voice Command:**
```
Kiểm tra giao dịch của khách hàng Nguyễn Thị Hoa, mã khách CUS100, 
ngày 17 tháng 10 năm 2025. Giao dịch chuyển khoản số tiền 350 triệu đồng 
từ tài khoản 1234567890 sang tài khoản người nhận 0987654321, 
tên người nhận Trần Văn Bình. Đã đối soát thành công với hệ thống core banking 
và hệ thống T24, không phát hiện bất thường. Điểm fraud score là 15 (thấp). 
Nhân viên kiểm tra Lê Minh Tâm.
```

**Expected Fields:**
- Customer Name: Nguyễn Thị Hoa
- Customer ID: CUS100
- Transaction Date: 17/10/2025
- Transaction Type: Chuyển khoản
- Amount: 350,000,000 VNĐ
- From Account: 1234567890
- To Account: 0987654321
- Beneficiary: Trần Văn Bình
- Reconciliation Status: Thành công
- Fraud Score: 15
- Validator: Lê Minh Tâm

**Expected Result:** ✅ Transaction validated

---

### Test Case 5.2: Xác nhận rút tiền ATM

**Voice Command:**
```
Xác minh giao dịch rút tiền mặt của anh Phạm Đức Long, ID CUS101, 
ngày 29 tháng 10 năm 2025. Rút 20 triệu đồng từ tài khoản 5566778899 
tại ATM chi nhánh Quận 3. Đã đối soát với hệ thống ATM và core banking, 
khớp dữ liệu. Không có dấu hiệu gian lận, fraud score 8 điểm rất thấp. 
Nhân viên vận hành Nguyễn Văn Kiên xác nhận.
```

**Expected Fields:**
- Customer Name: Phạm Đức Long
- Customer ID: CUS101
- Transaction Date: 29/10/2025
- Transaction Type: Rút tiền
- Amount: 20,000,000 VNĐ
- From Account: 5566778899
- To Account: ATM Quận 3
- Beneficiary: Phạm Đức Long
- Reconciliation Status: Thành công
- Fraud Score: 8
- Validator: Nguyễn Văn Kiên

**Expected Result:** ✅ ATM withdrawal verified

---

### Test Case 5.3: Kiểm tra thanh toán thẻ quốc tế

**Voice Command:**
```
Xác thực giao dịch thanh toán thẻ tín dụng của chị Võ Thị Lan, CUS102, 
vào ngày 28 tháng 10 năm 2025. Thanh toán online 85 triệu đồng 
từ thẻ tín dụng số 4111222233334444 cho merchant Amazon Singapore. 
Đã đối soát với Visa và core banking, giao dịch hợp lệ. 
Fraud score 25 điểm ở mức trung bình do giao dịch quốc tế. 
Chuyên viên Trần Thị Hương xác minh và phê duyệt.
```

**Expected Fields:**
- Customer Name: Võ Thị Lan
- Customer ID: CUS102
- Transaction Date: 28/10/2025
- Transaction Type: Thanh toán thẻ
- Amount: 85,000,000 VNĐ
- From Account: 4111222233334444
- To Account: Amazon Singapore
- Beneficiary: Amazon Singapore
- Reconciliation Status: Thành công
- Fraud Score: 25
- Validator: Trần Thị Hương

**Expected Result:** ✅ International card payment validated

---

## 🎯 SUMMARY TABLE

| Use Case | Test Cases | Total Fields | Avg. Voice Length |
|----------|------------|--------------|-------------------|
| **1. Loan** | 3 | 12 fields | ~120 words |
| **2. CRM** | 3 | 8 fields | ~80 words |
| **3. HR** | 3 | 10 fields | ~90 words |
| **4. Compliance** | 3 | 9 fields | ~100 words |
| **5. Operations** | 3 | 11 fields | ~110 words |
| **TOTAL** | **15 tests** | **50 fields** | **~500 words** |

---

## 🧪 HOW TO TEST

### Manual Testing (Voice)
1. Start bot: `python main.py`
2. Open frontend: `http://localhost:5173`
3. Click microphone button
4. Đọc một trong 15 test cases ở trên
5. Observe:
   - Voice → Text transcription
   - Task pushed to queue
   - Workflow worker processes
   - Form filled in browser
   - Success message

### Automated Testing (Script)
```python
import asyncio
from task_queue import task_queue, Task, TaskType

async def run_test_case(voice_command: str, task_type: TaskType):
    task = Task(
        task_type=task_type,
        user_message=voice_command
    )
    task_id = await task_queue.push(task)
    print(f"✅ Test case queued: {task_id}")

# Run test
asyncio.run(run_test_case(
    "Tạo đơn vay cho khách hàng Nguyễn Văn An...",
    TaskType.LOAN
))
```

---

## ✅ SUCCESS CRITERIA

Mỗi test case được coi là **PASS** nếu:
1. ✅ Voice transcription chính xác (>95%)
2. ✅ Task được push vào queue
3. ✅ Supervisor agent classify đúng use case
4. ✅ Tool được gọi với đúng parameters
5. ✅ Browser agent điền form thành công
6. ✅ Tất cả required fields được điền
7. ✅ Form submit without errors
8. ✅ Task status = COMPLETED

---

**Total Test Coverage:** 5 Use Cases × 3 Test Cases = **15 Test Scenarios** 🎯
