# 🎙️ VOICE TEST SCENARIOS - ONE-SHOT MODE

**Format:** 1 câu duy nhất chứa TẤT CẢ thông tin  
**Updated:** October 31, 2025

**Lưu ý:** Nói 1 lần duy nhất, bot xác nhận, user confirm → Thực thi!

---

## 🔵 USE CASE 1: LOAN (ONE-SHOT)

### Scenario 1.1: Vay mua nhà

**User says (1 sentence):**
```
"Tạo đơn vay cho khách hàng Nguyễn Văn An CCCD 012345678901 sinh ngày 15 tháng 3 năm 1985 địa chỉ 123 đường Lê Lợi Quận 1 TP HCM số điện thoại 0901234567 email nguyenvanan@gmail.com vay 500 triệu đồng mua nhà kỳ hạn 24 tháng kỹ sư phần mềm tại FPT Software thu nhập 30 triệu mỗi tháng"
```

**Bot confirms:**
```
"Để tôi xác nhận:
- Họ tên: Nguyễn Văn An
- CCCD: 012345678901 (12 chữ số)
- Ngày sinh: 15/03/1985
- Địa chỉ: 123 Lê Lợi, Quận 1, TP.HCM
- SĐT: 0901234567 (10 chữ số)
- Email: nguyenvanan@gmail.com
- Số tiền: 500 triệu VNĐ
- Kỳ hạn: 24 tháng
- Mục đích: Mua nhà
- Công việc: Kỹ sư phần mềm, FPT Software
- Thu nhập: 30 triệu VNĐ/tháng
Anh xác nhận ĐÚNG không?"
```

**User:** "Đúng"

**Bot:** "Dạ, tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

**→ Browser fills 13 fields automatically!**

---

### Scenario 1.2: Vay kinh doanh

**User says:**
```
"Đơn vay Trần Thị Bình CCCD 098765432109 sinh 20/07/1990 địa chỉ 456 Nguyễn Huệ Quận 5 SĐT 0912345678 email tranbinhbiz@yahoo.com vay 1 tỷ 200 triệu kinh doanh nhà hàng 36 tháng chủ doanh nghiệp Nhà Hàng Hương Việt thu nhập 50 triệu"
```

**Bot:** "Xác nhận: Trần Thị Bình, 1.2 tỷ, 36 tháng... Đúng không?"

**User:** "Đúng"

**→ Executes!**

---

## 🔵 USE CASE 2: CRM (ONE-SHOT)

### Scenario 2.1: Khiếu nại thẻ

**User says (1 sentence):**
```
"Cập nhật CRM khách hàng Trần Văn B mã CUS002 SĐT 0912345678 khiếu nại thẻ bị khóa đột ngột đã mở khóa và xin lỗi khách nhân viên Phạm Văn Nam xử lý"
```

**Bot:** "Xác nhận: KH Trần Văn B (CUS002), khiếu nại thẻ bị khóa, đã xử lý, NV Phạm Văn Nam. Đúng không?"

**User:** "Đúng"

**Bot:** "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

**→ Fills 18 CRM fields!**

---

### Scenario 2.2: Tư vấn sản phẩm

**User says:**
```
"Lưu tương tác khách Lê Thị Mai CUS003 tư vấn sản phẩm tiết kiệm lãi suất cao đã tư vấn gói Vàng khách đồng ý mở tài khoản nhân viên Nguyễn Lan"
```

**Bot:** "Xác nhận..."

**User:** "OK"

**→ Executes!**

---

## 🟡 USE CASE 3: HR (ONE-SHOT)

### Scenario 3.1: Nghỉ phép

**User says (1 sentence):**
```
"Đơn nghỉ phép nhân viên Trần Thị Cúc mã NV001 từ ngày 22 đến 24 tháng 10 năm 2025 lý do việc gia đình phòng Kinh Doanh quản lý Lê Minh Hoàng"
```

**Bot:** "Xác nhận: NV Trần Thị Cúc (NV001), nghỉ phép 22-24/10/2025, việc gia đình, Phòng Kinh Doanh, QL Lê Minh Hoàng. Đúng không?"

**User:** "Đúng"

**Bot:** "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

**→ Fills 20 HR fields!**

---

### Scenario 3.2: Đăng ký đào tạo

**User says:**
```
"Đăng ký đào tạo Phạm Minh Tuấn NV002 từ 5 đến 7 tháng 11 kỹ năng chăm sóc khách hàng phòng CSKH quản lý Trần Thu Hà"
```

**Bot:** "Xác nhận..."

**User:** "OK"

**→ Executes!**

---

## 🟡 USE CASE 4: COMPLIANCE (ONE-SHOT)

### Scenario 4.1: Báo cáo AML

**User says (1 sentence):**
```
"Báo cáo AML tháng 9 năm 2025 nhân viên Lê Văn Cường không phát hiện vi phạm kiểm tra 1250 giao dịch mức độ rủi ro thấp"
```

**Bot:** "Xác nhận: Báo cáo AML tháng 9/2025, NV Lê Văn Cường, 0 vi phạm, 1250 GD, rủi ro thấp. Đúng không?"

**User:** "Đúng"

**Bot:** "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

**→ Auto-fills 23 compliance fields!**

---

### Scenario 4.2: Báo cáo KYC

**User says:**
```
"Báo cáo KYC quý 3 năm 2025 nhân viên Nguyễn Thị Lan phát hiện 3 vi phạm khách không cập nhật giấy tờ 850 hồ sơ rủi ro trung bình"
```

**Bot:** "Xác nhận..."

**User:** "OK"

**→ Executes!**

---

## 🟢 USE CASE 5: OPERATIONS (ONE-SHOT - MINIMAL)

### Scenario 5.1: Kiểm tra giao dịch (FASTEST!)

**User says (minimal - 3 fields only):**
```
"Kiểm tra giao dịch TXN12345 số tiền 10 triệu khách hàng Nguyễn Văn A"
```

**Bot:** "Xác nhận: Mã GD TXN12345, số tiền 10 triệu VNĐ, KH Nguyễn Văn A. Đúng không?"

**User:** "Đúng"

**Bot:** "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

**→ AUTO-FILLS 23 FIELDS:**
- transactionDate: today
- transactionType: "transfer"
- channel: "online"  
- status: "completed"
- reviewerName: "Hệ thống"
- fraudScore: "0"
- ... (20 more fields)

**Total:** 1 user input + 1 confirm = 2 turns only!  
**Time:** ~15 seconds (NHANH NHẤT!)

---

### Scenario 5.2: Đối soát giao dịch

**User says:**
```
"Đối soát GD999 50 triệu Trần Văn B"
```

**Bot:** "Xác nhận..."

**User:** "OK"

**→ Done in 15 seconds!**

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

