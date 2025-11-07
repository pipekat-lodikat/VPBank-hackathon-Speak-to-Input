# VPBank Voice Agent - User Guide

Welcome to VPBank Voice Agent - your intelligent voice-powered banking form automation assistant!

## Table of Contents

- [Getting Started](#getting-started)
- [How to Use Voice Commands](#how-to-use-voice-commands)
- [Supported Form Types](#supported-form-types)
- [Voice Command Examples](#voice-command-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Privacy & Security](#privacy--security)

---

## Getting Started

### System Requirements

- **Browser:** Chrome, Firefox, Safari, or Edge (latest version)
- **Microphone:** Working microphone for voice input
- **Internet Connection:** Stable connection (minimum 1 Mbps)
- **Permissions:** Allow microphone access when prompted

### Accessing the System

1. Open your web browser
2. Navigate to the VPBank Voice Agent URL:
   - Local: `http://localhost:5173`
   - Remote: `http://<server-ip>:5173`
3. Click **"Đăng nhập"** (Login) if you have an account
4. Or click **"Đăng ký"** (Register) to create a new account

### First-Time Setup

**Step 1: Login or Register**
- Enter your username and password
- For new users, provide email and phone number
- Check your email for verification code if required

**Step 2: Grant Microphone Permission**
- Browser will ask for microphone access
- Click **"Allow"** to enable voice features
- You'll see a green microphone icon when ready

**Step 3: Start Speaking**
- Click the **"Connect"** button to start voice session
- Wait for the greeting: "Xin chào! Tôi là trợ lý ảo của VPBank..."
- Start speaking naturally in Vietnamese

---

## How to Use Voice Commands

### Two Ways to Fill Forms

#### 1. ONE-SHOT MODE (Quick Method)

Speak all information in one go - the system will automatically extract and fill everything.

**Example:**
> "Tạo đơn vay cho khách hàng Nguyễn Văn An, căn cước công dân 012345678901, sinh ngày 15/03/1985, địa chỉ 123 Lê Lợi Quận 1, số điện thoại 0901234567, email abc@gmail.com, vay 500 triệu mua nhà kỳ hạn 24 tháng, kỹ sư phần mềm công ty FPT thu nhập 30 triệu mỗi tháng"

**What happens:**
1. Bot acknowledges: "Dạ, tôi đã ghi nhận: Nguyễn Văn An, căn cước công dân 012345678901, 500 triệu, 24 tháng. Đang xử lý..."
2. System automatically fills ALL fields
3. You receive notification when complete

#### 2. INCREMENTAL MODE (Step-by-Step Method)

Fill forms field by field with voice commands.

**Example Flow:**
```
You: "Bắt đầu điền đơn vay"
Bot: "Dạ, tôi đã mở form đơn vay. Anh/chị có thể bắt đầu điền từng thông tin."

You: "Điền tên là Hiếu Nghị"
Bot: "Đã điền tên. Tiếp tục điền hoặc nói 'Submit' khi xong."

You: "Điền căn cước công dân 123456789123"
Bot: "Đã điền Căn Cước Công Dân."

You: "Điền số điện thoại 0963023600"
Bot: "Đã điền số điện thoại."

You: "Vay 3 tỷ đồng"
Bot: "Đã điền số tiền vay."

You: "Submit form"
Bot: "Đang gửi form... Form đã được gửi thành công!"
```

---

## Supported Form Types

The system supports 5 types of banking forms:

### 1. Loan Application (Đơn Vay Vốn & KYC)

Fill loan applications with customer information.

**Required Information:**
- Full name (Họ và tên)
- National ID (Căn cước công dân/CMND)
- Date of birth (Ngày sinh)
- Address (Địa chỉ)
- Phone number (Số điện thoại)
- Email
- Loan amount (Số tiền vay)
- Loan purpose (Mục đích vay)
- Loan term (Kỳ hạn)
- Occupation (Nghề nghiệp)
- Company (Công ty)
- Monthly income (Thu nhập hàng tháng)

**Example Command:**
> "Vay 500 triệu Nguyễn Văn An căn cước công dân 012345678901 số điện thoại 0901234567 mua nhà kỳ hạn 24 tháng"

---

### 2. CRM Update (Cập Nhật CRM)

Update customer records and complaints.

**Required Information:**
- Customer name (Tên khách hàng)
- Customer ID (Mã khách hàng)
- Complaint type (Loại khiếu nại)
- Status (Trạng thái)
- Handled by (Nhân viên xử lý)

**Example Command:**
> "Cập nhật CRM khách Trần Văn B mã CUS002 khiếu nại thẻ bị khóa đã xử lý nhân viên Phạm Nam"

---

### 3. HR Request (Yêu Cầu HR)

Submit HR requests like leave applications.

**Required Information:**
- Employee name (Tên nhân viên)
- Employee ID (Mã nhân viên)
- Request type (Loại yêu cầu)
- Start date (Ngày bắt đầu)
- End date (Ngày kết thúc)
- Reason (Lý do)
- Department (Phòng ban)
- Manager (Quản lý)

**Example Command:**
> "Đơn nghỉ phép nhân viên Trần Thị Cúc NV001 từ 22 đến 24/10 việc gia đình phòng Kinh Doanh quản lý Lê Hoàng"

---

### 4. Compliance Report (Báo Cáo Tuân Thủ)

Submit compliance reports (AML, KYC checks).

**Required Information:**
- Report type (Loại báo cáo)
- Month (Tháng)
- Employee name (Tên nhân viên)
- Violations (Số vi phạm)
- Notes (Ghi chú)

**Example Command:**
> "Báo cáo AML tháng 9 nhân viên Lê Văn Cường không vi phạm"

---

### 5. Operations Check (Kiểm Tra Giao Dịch)

Review transactions and operations.

**Required Information:**
- Transaction ID (Mã giao dịch)
- Amount (Số tiền)
- Customer name (Tên khách hàng)
- Date (Ngày giao dịch)
- Reviewer (Người kiểm tra)

**Example Command:**
> "Kiểm tra giao dịch TXN12345 số tiền 10 triệu khách hàng Nguyễn Văn A"

---

## Voice Command Examples

### Starting a Form

```
"Bắt đầu điền đơn vay"
"Mở form vay"
"Tạo đơn vay mới"
"Làm đơn vay"
```

### Filling Individual Fields

```
"Điền tên là [Tên]"
"Căn cước công dân là [Số]"
"Số điện thoại [Số]"
"Email là [Email]"
"Vay [Số tiền]"
"Kỳ hạn [Số] tháng"
```

### Submitting Forms

```
"Submit form"
"Gửi đơn"
"Xong rồi"
"Hoàn tất"
```

### Checking Status

```
"Tình trạng form như thế nào?"
"Đã điền xong chưa?"
```

---

## Best Practices

### For Clear Voice Recognition

1. **Speak Clearly and Naturally**
   - Use normal conversational tone
   - No need to speak slowly
   - Pause naturally between sentences

2. **Pronounce Numbers Carefully**
   - Phone numbers: Speak digit by digit
     - Example: "0963023600" → "không chín sáu ba không hai ba sáu không không"
   - National ID: Speak digit by digit
     - Example: "123456789123" → "một hai ba bốn năm sáu bảy tám chín một hai ba"
   - Money amounts: Use "triệu" or "tỷ"
     - Example: "500 triệu đồng" (NOT "500 triệu VNĐ")

3. **Dates and Formats**
   - Date of birth: "ngày [X] tháng [Y] năm [Z]"
     - Example: "ngày mười lăm tháng ba năm hai nghìn không trăm lẻ năm"
   - Email: Spell clearly with "a-còng" for @
     - Example: "abc a-còng gmail chấm com"

4. **Quiet Environment**
   - Minimize background noise
   - Turn off music or TV
   - Close windows if traffic is loud

5. **Microphone Position**
   - Keep microphone 15-30 cm from mouth
   - Use headset microphone for best results
   - Avoid covering microphone with hand

### For Efficient Form Filling

1. **Prepare Information First**
   - Have all documents ready before starting
   - Know all required information
   - Write down complex numbers (ID, phone, amounts)

2. **Use ONE-SHOT Mode When Possible**
   - Faster completion
   - Less back-and-forth
   - Speak all info in one sentence

3. **Check Your Input**
   - Look at the form preview if available
   - Verify important numbers (amounts, IDs)
   - Correct mistakes immediately

4. **Wait for Confirmations**
   - Let the bot acknowledge each command
   - Don't speak over the bot
   - Wait for "Đang xử lý..." before continuing

---

## Troubleshooting

### Voice Not Detected

**Problem:** Bot doesn't hear you

**Solutions:**
1. Check microphone is connected and working
2. Grant microphone permission in browser settings
3. Test microphone in browser settings (chrome://settings/content/microphone)
4. Try refreshing the page
5. Use a different microphone or headset

---

### Bot Misunderstands Commands

**Problem:** Bot fills wrong information

**Solutions:**
1. Speak more clearly and slowly
2. Break long sentences into shorter ones
3. Use INCREMENTAL mode for complex forms
4. Spell out confusing names or addresses
5. Repeat the command if misunderstood

---

### Form Not Submitting

**Problem:** "Submit" command doesn't work

**Solutions:**
1. Make sure all required fields are filled
2. Wait for "Đã điền xong" confirmation
3. Try saying "Gửi đơn" or "Xong rồi" instead
4. Check if browser automation is working
5. Contact support if issue persists

---

### Connection Issues

**Problem:** "Network error" or disconnected

**Solutions:**
1. Check internet connection
2. Refresh the page and reconnect
3. Try different browser (Chrome recommended)
4. Clear browser cache and cookies
5. Restart your router if needed

---

### Slow Response Time

**Problem:** Bot takes too long to respond

**Solutions:**
1. Check internet speed (minimum 1 Mbps)
2. Close other tabs using bandwidth
3. Wait patiently - complex forms take 30-60 seconds
4. Don't interrupt the bot during processing
5. Use ONE-SHOT mode for faster processing

---

## Frequently Asked Questions

### General Questions

**Q: What languages are supported?**
A: Currently only Vietnamese is supported for voice input.

**Q: Can I use this on mobile?**
A: Yes, but desktop browsers provide better experience. Chrome mobile is recommended.

**Q: Is my data secure?**
A: Yes, all data is encrypted and stored securely in AWS. See [Privacy & Security](#privacy--security).

**Q: How accurate is the voice recognition?**
A: 95%+ accuracy for clear speech in quiet environments.

**Q: Can I edit filled information?**
A: Yes, use "Điền lại [field] là [value]" to update any field.

---

### Technical Questions

**Q: What browsers are supported?**
A: Chrome (recommended), Firefox, Safari, Edge. Latest versions required.

**Q: Do I need to install anything?**
A: No, it's 100% web-based. Just allow microphone access.

**Q: Can multiple people use it at once?**
A: Yes, each user gets their own session. No conflicts.

**Q: How long does form filling take?**
A: ONE-SHOT mode: 10-30 seconds. INCREMENTAL mode: 1-2 minutes.

**Q: What happens if I lose connection?**
A: Session is saved. Reconnect and continue where you left off.

---

### Account Questions

**Q: How do I reset my password?**
A: Click "Quên mật khẩu" on login page and follow email instructions.

**Q: Can I change my username?**
A: No, username is permanent. Contact support for account changes.

**Q: Is registration required?**
A: Yes, authentication is required for security and session tracking.

**Q: How long are sessions stored?**
A: Sessions are stored indefinitely in DynamoDB for audit purposes.

---

## Privacy & Security

### Data Protection

**What We Collect:**
- Voice recordings (temporary, deleted after transcription)
- Transcribed text of your commands
- Form data you provide (names, IDs, amounts, etc.)
- Session metadata (timestamps, user ID)

**How We Protect It:**
- End-to-end encryption for WebRTC audio
- JWT tokens for authentication
- AWS Cognito for secure user management
- AWS DynamoDB encryption at rest
- PII masking in system logs
- No voice recordings stored permanently

**Who Has Access:**
- Only authenticated users can access their own sessions
- VPBank administrators (for support and audit)
- No third-party access without your consent

### Your Rights

- **Access:** View all your session transcripts
- **Delete:** Request deletion of your data (contact support)
- **Correct:** Update incorrect form information anytime
- **Export:** Download your session history

### Security Best Practices

1. **Never share your login credentials**
2. **Log out after each session**
3. **Use strong passwords (8+ characters, mixed case, numbers)**
4. **Don't use public WiFi for sensitive transactions**
5. **Enable two-factor authentication if available**
6. **Report suspicious activity immediately**

---

## Getting Help

### Support Channels

**Email Support:**
- support@vpbank.com
- Response time: 24-48 hours

**Phone Support:**
- Hotline: 1900-xxxx
- Available: Mon-Fri, 8:00-17:00 ICT

**Live Chat:**
- Available in-app (click chat icon)
- Available: Mon-Fri, 8:00-17:00 ICT

**Documentation:**
- User Guide: https://docs.vpbank.com/voice-agent/user-guide
- Video Tutorials: https://docs.vpbank.com/voice-agent/videos
- FAQs: https://docs.vpbank.com/voice-agent/faq

### Before Contacting Support

Please have ready:
1. Your username (NOT password)
2. Date and time of issue
3. Browser name and version
4. Error message or screenshot
5. Steps to reproduce the problem

---

## Tips for Success

### First-Time Users

1. **Start with simple commands** - Test with "Tạo đơn vay" before complex forms
2. **Practice pronunciation** - Say numbers and IDs slowly at first
3. **Use INCREMENTAL mode** - Build confidence field by field
4. **Review transcripts** - Check what the bot understood
5. **Ask for help** - Don't hesitate to contact support

### Power Users

1. **Master ONE-SHOT mode** - Prepare full sentence before speaking
2. **Use templates** - Save common commands for repeat use
3. **Optimize phrasing** - Learn which phrases work best
4. **Leverage shortcuts** - Use abbreviated commands when possible
5. **Monitor metrics** - Track your completion times

---

## System Status

Check system status at: https://status.vpbank.com

**Current Status:** All systems operational ✅

**Scheduled Maintenance:**
- Every Sunday, 2:00-4:00 AM ICT
- Advanced notice via email

**Incident History:**
- View past 90 days at status page

---

## Updates & Changelog

### Version 1.0.0 (Current)

**Features:**
- Voice-powered form automation for 5 form types
- ONE-SHOT and INCREMENTAL filling modes
- Real-time transcript display
- AWS Cognito authentication
- Session history and replay

**Coming Soon:**
- English language support
- Mobile app (iOS/Android)
- Voice biometric authentication
- Offline mode for poor connectivity
- Custom form templates

**Submit Feature Requests:**
- Email: features@vpbank.com
- Include: Feature name, use case, priority

---

## Glossary

**Terms to Know:**

- **ONE-SHOT Mode:** Fill entire form with one voice command
- **INCREMENTAL Mode:** Fill form field by field
- **WebRTC:** Real-time audio streaming technology
- **STT:** Speech-to-Text (voice recognition)
- **TTS:** Text-to-Speech (bot voice)
- **Session:** One complete conversation with the bot
- **Transcript:** Written record of conversation
- **JWT Token:** Secure authentication credential

---

## Appendix

### Supported Vietnamese Accents

- Northern (Hanoi)
- Central (Huế, Đà Nẵng)
- Southern (Hồ Chí Minh)

### Number Pronunciation Guide

**Digits (0-9):**
- 0: "không"
- 1: "một"
- 2: "hai"
- 3: "ba"
- 4: "bốn"
- 5: "năm"
- 6: "sáu"
- 7: "bảy"
- 8: "tám"
- 9: "chín"

**Large Numbers:**
- 1,000: "một nghìn"
- 1,000,000: "một triệu"
- 1,000,000,000: "một tỷ"

**Phone Number Example:**
- 0963023600 → "không chín sáu ba không hai ba sáu không không"

### Date Format Examples

**Vietnamese Format:**
- DD/MM/YYYY → "ngày [DD] tháng [MM] năm [YYYY]"
- 15/03/2005 → "ngày mười lăm tháng ba năm hai nghìn không trăm lẻ năm"

---

**Document Version:** 1.0.0
**Last Updated:** November 7, 2025
**Next Review:** January 7, 2026

---

Thank you for using VPBank Voice Agent! We hope this guide helps you make the most of our voice-powered banking automation system.

For additional support, contact us at support@vpbank.com or call 1900-xxxx.

**Happy banking! 🏦**
