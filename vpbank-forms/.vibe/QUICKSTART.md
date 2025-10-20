# Quick Start Guide - VPBank Forms

## 🚀 Bắt Đầu Nhanh

### 1. Mở Project

```bash
cd /Users/nghia.mle/Developer/vpbank-forms
```

### 2. Mở Trang Chủ

**Option A: Sử dụng trình duyệt trực tiếp**
```bash
open index.html
```

**Option B: Sử dụng Live Server (khuyến nghị)**
- Nếu có VS Code với Live Server extension:
  - Right-click vào `index.html`
  - Chọn "Open with Live Server"

### 3. Test Từng Use Case

Từ trang chủ, click vào từng card để mở form:

#### Use Case 1 - Loan Origination
```bash
open use-case-1-loan-origination/index.html
```
- Click "Test AI" để xem demo auto-fill
- AI sẽ điền: Khách hàng vay 500 triệu, kỳ hạn 24 tháng

#### Use Case 2 - CRM Update
```bash
open use-case-2-crm-update/index.html
```
- Test cập nhật địa chỉ khách hàng
- Demo: Cập nhật địa chỉ mới tự động

#### Use Case 3 - HR Workflow
```bash
open use-case-3-hr-workflow/index.html
```
- Test tạo đơn nghỉ phép
- Demo: Nghỉ phép từ 22-24/10

#### Use Case 4 - Compliance Reporting
```bash
open use-case-4-compliance-reporting/index.html
```
- Test báo cáo AML
- Demo: Báo cáo tháng 9, không vi phạm

#### Use Case 5 - Operations Validation
```bash
open use-case-5-operations-validation/index.html
```
- Test kiểm tra giao dịch
- Demo: Giao dịch 350 triệu ngày 17/10

## 🧪 Test AI Integration

### Mở Console (F12) và thử:

```javascript
// Use Case 1 - Loan
const loanAI = window.loanFormAI;
loanAI.fillForm({
  customerName: 'Nguyễn Văn An',
  loanAmount: '500000000',
  loanTerm: '24'
});

// Use Case 2 - CRM
const crmAI = window.crmFormAI;
crmAI.fillForm({
  customerName: 'Nguyễn Văn Bình',
  address: '25A Nguyễn Trãi, Q1, TP.HCM'
});

// Use Case 3 - HR
const hrAI = window.hrFormAI;
hrAI.fillForm({
  employeeName: 'Nguyễn Văn Cường',
  requestType: 'leave',
  startDate: '2024-10-22',
  endDate: '2024-10-24'
});

// Use Case 4 - Compliance
const complianceAI = window.complianceFormAI;
complianceAI.fillForm({
  reportType: 'aml',
  status: 'completed',
  violationsFound: 'none'
});

// Use Case 5 - Operations
const operationsAI = window.operationsFormAI;
operationsAI.fillForm({
  customerName: 'Nguyễn Thị Hoa',
  transactionAmount: '350000000',
  transactionDate: '2024-10-17'
});
```

## 📝 Các Tính Năng Cần Test

### 1. Form Validation
- ✅ Nhập thiếu trường bắt buộc
- ✅ Email không hợp lệ
- ✅ Số điện thoại sai format
- ✅ Số tiền âm
- ✅ Ngày không hợp lệ

### 2. AI Auto-Fill
- ✅ Click "Test AI" button
- ✅ Xem fields được highlight màu xanh
- ✅ Check console logs
- ✅ Verify data correctness

### 3. Form Submission
- ✅ Click "Gửi" button
- ✅ Xem confirmation modal
- ✅ Click "Xác Nhận"
- ✅ Xem success message

### 4. Auto-Save Draft
- ✅ Nhập một vài fields
- ✅ Refresh page
- ✅ Chọn "Load draft"
- ✅ Verify data restored

### 5. Responsive Design
- ✅ Open on mobile (F12 → Device toolbar)
- ✅ Test on tablet size
- ✅ Test on desktop

## 🔧 Tích Hợp Với AI Service

### Step 1: Include Scripts
```html
<script src="../shared/utils.js"></script>
<script src="../shared/ai-integration.js"></script>
<script src="script.js"></script>
```

### Step 2: Initialize FormAI
```javascript
const formAI = new FormAI('yourFormId');
```

### Step 3: Parse Vietnamese Input
```javascript
const input = "Điền khách hàng Nguyễn Văn An vay 500 triệu, kỳ hạn 24 tháng";
const data = formAI.parseNaturalLanguage(input);
formAI.fillForm(data);
```

### Step 4: Validate & Submit
```javascript
const validation = formAI.validateForm();
if (validation.isValid) {
  await formAI.submitForm();
}
```

## 📊 Expected Results

### Use Case 1 - Loan
- **Fields**: 20+ fields
- **AI Fill Time**: < 1 second
- **Validation**: Email, phone, amount
- **Impact**: 80% faster than manual

### Use Case 2 - CRM
- **Fields**: 15+ fields
- **Update Time**: < 2 seconds
- **Impact**: 90% less data errors

### Use Case 3 - HR
- **Fields**: 15+ fields
- **Auto-calculate**: Duration days
- **Impact**: 80% time saved

### Use Case 4 - Compliance
- **Fields**: 20+ fields
- **Auto-generate**: Report ID, title
- **Impact**: 99% accuracy

### Use Case 5 - Operations
- **Fields**: 25+ fields
- **Auto-verify**: Balance calculation
- **Impact**: 50% faster validation

## 🐛 Troubleshooting

### Forms không load
- Check browser console (F12)
- Verify file paths
- Try different browser

### AI Test không hoạt động
- Open console (F12)
- Check for JavaScript errors
- Verify FormAI initialization

### Validation không chạy
- Check required fields
- Verify input formats
- Look for error messages

### Draft không lưu
- Check localStorage enabled
- Clear browser cache
- Try incognito mode

## 📞 Support

Nếu gặp vấn đề:
1. Check console errors
2. Review `.vibe/technical-specs.md`
3. Contact development team

## ✅ Checklist

- [ ] Mở được trang chủ
- [ ] Test cả 5 use cases
- [ ] AI auto-fill hoạt động
- [ ] Validation chạy đúng
- [ ] Submit form thành công
- [ ] Responsive trên mobile
- [ ] Auto-save draft works
- [ ] Console không có errors

---

**Happy Testing! 🎉**
