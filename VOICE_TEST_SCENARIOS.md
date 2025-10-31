# 🎙️ VOICE TEST SCENARIOS - CONVERSATION FLOW

**Format:** Realistic conversation flows matching actual system prompt  
**Updated:** October 31, 2025

---

## 🔵 USE CASE 1: LOAN (FULL MODE)

### Scenario 1: Vay mua nhà

```
User: "Vay tiền mua nhà"
Bot: "Họ tên và CCCD?"
User: "Nguyễn Văn An, CCCD 012345678901"
Bot: "Ngày sinh?"
User: "15/03/1985"
Bot: "Địa chỉ?"
User: "123 Lê Lợi, Quận 1, TP.HCM"
Bot: "SĐT và email?"
User: "0901234567, nguyenvanan@gmail.com"
Bot: "Số tiền vay?"
User: "500 triệu"
Bot: "Kỳ hạn?"
User: "24 tháng"
Bot: "Mục đích vay?"
User: "Mua nhà"
Bot: "Công việc?"
User: "Kỹ sư phần mềm, FPT Software, thu nhập 30 triệu/tháng"
Bot: "Xác nhận: [đọc lại tất cả]. Đúng không?"
User: "Đúng"
Bot: "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."
```

**Fields:** 13 fields - customerName, customerId, dateOfBirth, address, phoneNumber, email, loanAmount, loanTerm, loanPurpose, employmentStatus, companyName, monthlyIncome, gender

---

## 🔵 USE CASE 2: CRM (FULL MODE)

### Scenario 1: Khiếu nại thẻ

```
User: "Ghi nhận khiếu nại khách hàng"
Bot: "Tên và mã KH?"
User: "Trần Văn B, mã CUS002"
Bot: "Loại tương tác?"
User: "Khiếu nại"
Bot: "Vấn đề gì?"
User: "Thẻ bị khóa đột ngột"
Bot: "Đã xử lý như thế nào?"
User: "Đã mở khóa và xin lỗi"
Bot: "Nhân viên xử lý?"
User: "Phạm Văn Nam"
Bot: "Xác nhận: KH Trần Văn B, khiếu nại thẻ... Đúng không?"
User: "Đúng"
Bot: "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."
```

**Fields:** 18 fields - Full CRM update

---

## 🟡 USE CASE 3: HR (MEDIUM MODE)

### Scenario 1: Nghỉ phép

```
User: "Tạo đơn nghỉ phép"
Bot: "Tên và mã nhân viên?"
User: "Trần Thị Cúc, NV001"
Bot: "Từ ngày nào đến ngày nào?"
User: "22 đến 24 tháng 10"
Bot: "Lý do?"
User: "Việc gia đình"
Bot: "Phòng ban và quản lý?"
User: "Phòng Kinh Doanh, quản lý Lê Minh Hoàng"
Bot: "Xác nhận: Trần Thị Cúc, nghỉ 22-24/10... Đúng không?"
User: "Đúng"
Bot: "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."
```

**Fields:** 20 fields - Full HR workflow

---

## 🟡 USE CASE 4: COMPLIANCE (MEDIUM MODE)

### Scenario 1: Báo cáo AML

```
User: "Tạo báo cáo AML"
Bot: "Tên người nộp báo cáo?"
User: "Lê Văn Cường"
Bot: "Kỳ báo cáo?"
User: "Tháng 9 năm 2025"
Bot: "Số vi phạm phát hiện?"
User: "Không có vi phạm"
Bot: "Xác nhận: Báo cáo AML tháng 9/2025, người nộp Lê Văn Cường, không vi phạm. Đúng không?"
User: "Đúng"
Bot: "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."
```

**Fields:** 23 fields - Auto-fills status, dates, etc.

---

## 🟢 USE CASE 5: OPERATIONS (ONE-SHOT MODE) ⚡

### Scenario 1: Kiểm tra giao dịch (FASTEST!)

```
User: "Kiểm tra giao dịch"
Bot: "Dạ, cho tôi biết:
- Mã giao dịch?
- Số tiền?
- Tên khách hàng?"

User: "Mã TXN12345, 10 triệu, Nguyễn Văn A"

Bot: "Xác nhận:
- Mã GD: TXN12345
- Số tiền: 10 triệu VNĐ
- Khách hàng: Nguyễn Văn A
Đúng không?"

User: "Đúng"

Bot: "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."
```

**→ AUTO-FILLS 23 FIELDS:**
- customerId: "CUS00000"
- accountNumber: "0000000000"
- transactionDate: today
- transactionType: "transfer"
- channel: "online"
- status: "completed"
- validationResult: "valid"
- reviewerName: "Hệ thống Voice Bot"
- reviewDate: today
- fraudScore: "0"
- ... và 13 fields khác

**Total turns:** 3 only! (vs 8-12 turns for FULL mode)  
**Time:** ~30 seconds (vs ~2 minutes)

---

## 📊 COMPARISON TABLE

| Mode | Use Cases | Turns | Time | User Provides | Auto-fills |
|------|-----------|-------|------|---------------|------------|
| 🔵 FULL | 1, 2 | 8-12 | ~2 min | 10-13 fields | 0-3 fields |
| 🟡 MEDIUM | 3, 4 | 5-8 | ~1.5 min | 6-8 fields | 5-10 fields |
| 🟢 ONE-SHOT | 5 | 3 | ~30 sec | 3 fields | 23 fields |

---

## ✅ QUICK TEST COMMANDS

### Use Case 1 (Loan):
```
Say: "Vay 500 triệu"
(Answer bot's questions)
Confirm: "Đúng"
```

### Use Case 2 (CRM):
```
Say: "Cập nhật khách hàng"
(Answer questions)
Confirm: "Đúng"
```

### Use Case 3 (HR):
```
Say: "Nghỉ phép 3 ngày"
(Answer questions)
Confirm: "OK"
```

### Use Case 4 (Compliance):
```
Say: "Báo cáo AML"
(Answer questions)
Confirm: "Xác nhận"
```

### Use Case 5 (Operations) - FASTEST:
```
Say: "Kiểm tra GD TXN123, 10 triệu, KH Nguyễn A"
Bot: "Xác nhận?"
Say: "Đúng"
→ Done in 30 seconds!
```

---

## 🎯 SUCCESS CRITERIA

✅ Bot hỏi đúng sequence theo mode  
✅ Bot đọc lại thông tin đầy đủ trước khi confirm  
✅ Bot nói trigger "BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ"  
✅ Task pushed với full conversation history  
✅ Supervisor extracts correctly từ conversation  
✅ Browser fills form với đúng field names  
✅ Submit button clicked  
✅ Form submitted successfully  

---

*Format này MATCH 100% với system prompt thực tế!* ✅

