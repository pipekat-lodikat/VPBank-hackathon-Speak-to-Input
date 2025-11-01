# 🔄 INCREMENTAL MODE - USER GUIDE

**Feature:** Điền form từng field qua voice commands liên tục  
**Status:** ✅ IMPLEMENTED  
**Version:** 1.0

---

## 🎯 2 MODES AVAILABLE

### Mode 1: ONE-SHOT (Fast)
```
User: "Vay 500 triệu Nguyễn Văn An CCCD 123... [đầy đủ info]"
Bot: [xác nhận]
User: "Đúng"
→ Done in 30 seconds!
```

### Mode 2: INCREMENTAL (Flexible - NEW!)
```
User: "Bắt đầu đơn vay"
Bot: "Đã mở form"

User: "Điền tên Hiếu Nghị"
Bot: "Đã điền"

User: "Điền CCCD 123456789123"
Bot: "Đã điền"

... (20+ turns)

User: "Submit"
Bot: "Đã gửi thành công!"
```

---

## 📝 INCREMENTAL MODE TEST SCENARIOS

### Test 1: Loan Form (Incremental)

```
1. User: "Mở form đơn vay"
   Bot: "Đã mở form. Anh có thể bắt đầu điền."
   System: start_incremental_form("loan") → Browser opens

2. User: "Điền tên của tôi là Hiếu Nghị"
   Bot: "Đã điền tên Hiếu Nghị."
   System: fill_single_field("customerName", "Hiếu Nghị")

3. User: "Căn cước công dân 123456789123"
   Bot: "Đã điền số Căn Cước."
   System: fill_single_field("customerId", "123456789123")

4. User: "Sinh ngày 3 tháng 3 năm 2005"
   Bot: "Đã điền ngày sinh."
   System: fill_single_field("dateOfBirth", "2005-03-03")

5. User: "Địa chỉ 828 đường Sư Vạn Hạnh Phường 12"
   Bot: "Đã điền địa chỉ."
   System: fill_single_field("address", "828...")

6. User: "Số điện thoại 0963023600"
   Bot: "Đã điền SĐT."
   System: fill_single_field("phoneNumber", "0963023600")

7. User: "Email hieunghiwork123 a-còng gmail chấm com"
   Bot: "Đã điền email."
   System: fill_single_field("email", "hieunghiwork123@gmail.com")

8. User: "Giới tính nam"
   Bot: "Đã điền."
   System: fill_single_field("gender", "male")

9. User: "Vay 3 tỷ đồng"
   Bot: "Đã điền số tiền vay 3 tỷ."
   System: fill_single_field("loanAmount", "3000000000")

10. User: "Mục đích kinh doanh"
    Bot: "Đã điền mục đích vay."
    System: fill_single_field("loanPurpose", "business")

11. User: "Kỳ hạn 48 tháng"
    Bot: "Đã điền kỳ hạn."
    System: fill_single_field("loanTerm", "48")

12. User: "Đang làm việc"
    Bot: "Đã điền tình trạng việc làm."
    System: fill_single_field("employmentStatus", "employed")

13. User: "Công ty Renova Cloud Company Limited"
    Bot: "Đã điền tên công ty."
    System: fill_single_field("companyName", "Renova Cloud...")

14. User: "Thu nhập 30 triệu đồng mỗi tháng"
    Bot: "Đã điền thu nhập."
    System: fill_single_field("monthlyIncome", "30000000")

15. User: "Địa chỉ làm việc Bitexco Quận 1"
    Bot: "Đã điền địa chỉ làm việc."
    System: fill_single_field("workAddress", "Bitexco...")

16. User: "Tài sản bất động sản"
    Bot: "Đã điền loại tài sản."
    System: fill_single_field("collateralType", "real-estate")

17. User: "Giá trị 5 tỷ đồng"
    Bot: "Đã điền giá trị tài sản."
    System: fill_single_field("collateralValue", "5000000000")

18. User: "Mô tả căn hộ dịch vụ Quận 2"
    Bot: "Đã điền mô tả."
    System: fill_single_field("collateralDescription", "Căn hộ...")

19. User: "Nhân viên quan hệ Nguyễn Văn X"
    Bot: "Đã điền tên RM."
    System: fill_single_field("relationshipManager", "Nguyễn Văn X")

20. User: "Ghi chú khách hàng VIP"
    Bot: "Đã điền ghi chú."
    System: fill_single_field("additionalNotes", "Khách VIP")

21. User: "Submit form"
    Bot: "Đang gửi đơn vay... Vui lòng đợi."
    System: submit_incremental_form() → Click submit → Modal → Success
    Bot: "✅ Đơn vay đã được gửi thành công!"
```

**Total:** 21 turns (vs 2 turns for ONE-SHOT)  
**Time:** ~5-7 phút (vs 30 giây for ONE-SHOT)  
**Benefit:** Tự nhiên hơn, dễ sửa từng field

---

## 🆚 WHEN TO USE WHICH MODE?

| Scenario | Recommended Mode | Reason |
|----------|------------------|--------|
| User biết TẤT CẢ info | ONE-SHOT | Nhanh nhất |
| User chỉ biết MỘT SỐ info | INCREMENTAL | Điền từng phần |
| User muốn SỬA 1 field | INCREMENTAL | Mở → Sửa → Submit |
| Demo/Presentation | INCREMENTAL | Impressive, step-by-step |
| Production/Speed | ONE-SHOT | Efficient |

---

## 🧪 TEST COMMANDS

### Start Session:
```
"Bắt đầu điền đơn vay"
"Mở form CRM"
"Tạo đơn nghỉ phép mới"
```

### Fill Fields:
```
"Điền tên Hiếu Nghị"
"Điền CCCD 123456789123"
"Điền SĐT 0963023600"
"Điền email abc a-còng gmail chấm com"
"Vay 3 tỷ đồng"
"Kỳ hạn 48 tháng"
```

### Multi-field in 1 command:
```
"Điền tên Hiếu Nghị và SĐT 0963023600"
"Điền email abc@gmail.com và địa chỉ 123 Lê Lợi"
```

### Submit:
```
"Submit form"
"Gửi đơn"
"Xong rồi gửi đi"
```

---

## 🔧 TECHNICAL DETAILS

### Browser Lifecycle:
```
start_incremental_form()
  → Browser(keep_alive=True)
  → Navigate to form
  → Keep browser OPEN
  
fill_single_field() × N
  → agent.add_new_task()  ← Same browser!
  → Fill 1 field
  → Browser still open
  
submit_incremental_form()
  → agent.add_new_task()
  → Click submit
  → Handle modal
  → browser.close()
```

### Tools Chain:
```
Supervisor
  → start_incremental_form("loan")
    → browser_agent.start_form_session()
  
  → fill_single_field("customerName", "X")
    → browser_agent.fill_field_incremental()
      → incremental_agent.add_new_task()
  
  → fill_single_field("phoneNumber", "Y")
    → browser_agent.fill_field_incremental()
      → incremental_agent.add_new_task()
  
  → submit_incremental_form()
    → browser_agent.submit_form_incremental()
      → incremental_agent.add_new_task()
      → browser.close()
```

---

## ✅ IMPLEMENTATION STATUS

| Component | Status | Details |
|-----------|--------|---------|
| Browser Agent | ✅ DONE | 3 new methods added |
| Supervisor Tools | ✅ DONE | 3 new async tools |
| Voice Agent Prompt | ✅ DONE | Incremental instructions |
| Task Queue | ✅ OK | No changes needed |
| Testing | ⏳ PENDING | Need manual testing |

**Overall:** 90% complete, ready for testing!

---

## 🚀 HOW TO TEST

**Restart server:**
```bash
python main.py
```

**Test Incremental Mode:**
```
Say: "Bắt đầu điền đơn vay"
(Wait for bot: "Đã mở form")

Say: "Điền tên Hiếu Nghị"
(Wait: "Đã điền")

Say: "Điền CCCD 123456789123"
(Wait: "Đã điền")

... (continue for 10-15 fields)

Say: "Submit form"
(Wait ~30 seconds)
(Bot: "✅ Đã gửi thành công!")
```

---

*Implementation by: Claude AI*  
*Date: October 31, 2025*  
*Status: Ready for testing*

