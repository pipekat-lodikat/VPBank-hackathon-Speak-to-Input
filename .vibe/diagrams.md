### 1. Kiến trúc tổng quan

```mermaid
flowchart LR
    %% ===== Frontend Layer =====
    subgraph FE["Frontend React UI"]
        U["🧑‍💻 User<br/>Phát biểu lệnh / thông tin cần điền"] --> MIC["🎤 Microphone"]
        MIC -->|Voice Stream| RTC1["WebRTC Connection"]
    end
    FE_UI["Mở Web Nhập Liệu<br/>(Demo như Sheet)"] --> BE

    %% ===== Backend AI (Pipecat) =====
    subgraph BE["Backend AI - Python / Pipecat"]
        RTC2["WebRTC Connection"] --> STT["🗣️ STT<br/>(Speech to Text)"]
        STT --> LLM["🧠 LLM<br/>(Xử lý ngữ cảnh, sinh prompt)"]
        LLM --> TTS["🔊 TTS<br/>(Text to Speech)"]
        LLM -->|Trigger action| CALL["λ Browser-Use Function Call"]
    end

    %% ===== Browser Automation =====
    subgraph BR["Browser-Use Flow"]
        OPEN["🌐 Mở web form nhập liệu"] --> FILL["🧾 Điền thông tin tự động"]
        FILL --> DONE["Báo hoàn tất"]
    end

    %% ===== Connections =====
    RTC1 --> RTC2
    CALL --> BR
    DONE --> FE_UI
```

**Giải thích:**
- **Frontend (React)**: User nói vào microphone → stream qua WebRTC
- **Backend (Pipecat)**: Nhận voice → STT chuyển thành text → LLM xử lý ngữ cảnh & quyết định → TTS trả lời
- **Browser-Use**: Nhận lệnh từ LLM → tự động mở browser → điền form/sheet → báo kết quả
- **Luồng**: User nói → Pipecat xử lý AI → gọi Browser-Use để automation → kết quả về User

---

### 2. Chi tiết Flow - Nhập liệu Google Sheet bằng giọng nói

#### 2.1. Flow tổng quan đơn giản

```mermaid
sequenceDiagram
    actor User as 👤 User
    participant Pipecat as 🎙️ Pipecat UI<br/>(Voice + LLM + TTS)
    participant BrowserUse as Browser-Use<br/>(Sheets Automation)
    participant GSheet as Google Sheets
    
    Note over User,GSheet: User nói để nhập liệu
    User->>Pipecat: 🗣️ "Thêm khách hàng Nguyễn Văn A, SĐT 0123456789"
    
    Pipecat->>Pipecat: STT → Text
    Pipecat->>Pipecat: LLM phân tích & trích xuất data
    Note right of Pipecat: {<br/>  name: "Nguyễn Văn A",<br/>  phone: "0123456789"<br/>}
    
    Pipecat-->>User: 🔊 "Đã ghi nhận. Email là gì?"
    User->>Pipecat: 🗣️ "nguyenvana@gmail.com"
    
    Pipecat->>Pipecat: Data đủ → Trigger automation
    Pipecat->>BrowserUse: Gửi lệnh thêm dòng mới
    
    BrowserUse->>BrowserUse: Khởi động browser
    BrowserUse->>GSheet: Mở sheet & điền dữ liệu
    GSheet-->>BrowserUse: ✅ Thành công
    
    BrowserUse-->>Pipecat: Trả kết quả + screenshot
    Pipecat-->>User: 🔊 "Đã thêm khách hàng vào sheet"
    Pipecat-->>User: 📸 Hiển thị screenshot
```

**Giải thích:**
- User nói thông tin khách hàng bằng tiếng nói
- Pipecat dùng LLM để hiểu ý định và trích xuất dữ liệu (tên, SĐT, email)
- Nếu thiếu thông tin, Pipecat hỏi lại bằng TTS
- Khi đủ dữ liệu → gọi Browser-Use để tự động điền vào Google Sheets
- Kết quả trả về với screenshot xác nhận

---

#### 2.2. Pipecat Flow - Xử lý voice & quyết định

* Tập trung vào: STT → LLM → TTS
* LLM thu thập đủ thông tin rồi mới trigger Browser-Use

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant UI as 🎙️ Pipecat UI
    participant STT as Speech-to-Text
    participant LLM as 🧠 LLM
    participant TTS as Text-to-Speech
    participant BrowserUse as 🌐 Browser-Use
    
    User->>UI: Nói vào microphone
    UI->>STT: Stream audio
    STT-->>UI: "Thêm khách hàng Nguyễn Văn A"
    
    UI->>LLM: Gửi text + context
    LLM->>LLM: Phân tích intent & entities
    LLM-->>UI: Need more info: email missing
    
    UI->>TTS: "Email là gì?"
    TTS-->>User: Phát giọng nói
    
    User->>UI: "nguyenvana@gmail.com"
    UI->>STT: Stream audio
    STT-->>UI: Text
    
    UI->>LLM: Update data
    LLM-->>UI: Data complete → Action: add_to_sheet
    
    UI->>BrowserUse: Execute automation
    BrowserUse-->>UI: Success result
    
    UI->>TTS: "Đã hoàn tất"
    TTS-->>User: Phát giọng nói
```

**Giải thích:**
- **STT (Speech-to-Text)**: Chuyển giọng nói thành text
- **LLM**: Phân tích intent (ý định) & entities (tên, SĐT, email)
- LLM theo dõi context để biết còn thiếu thông tin gì
- **TTS (Text-to-Speech)**: Hỏi lại user để bổ sung thông tin
- Khi data đủ → trigger Browser-Use automation
- Conversational AI: hỏi đáp tự nhiên, không cần form cứng nhắc

---

#### 2.3. Browser-Use Flow - Automation Google Sheets

- nhận lệnh → launch browser → điền sheet → trả kết quả

```mermaid
sequenceDiagram
    participant Pipecat as 🎙️ Pipecat
    participant Agent as 🤖 Browser Agent
    participant Browser as 🌐 Chromium
    participant GSheet as 📊 Google Sheets
    
    Pipecat->>Agent: add_row_to_sheet(data)
    Note right of Agent: data = {<br/>  name: "Nguyễn Văn A",<br/>  phone: "0123456789",<br/>  email: "nguyenvana@gmail.com"<br/>}
    
    Agent->>Browser: Launch browser
    Browser->>GSheet: Navigate to sheet URL
    
    alt Cần login
        Browser->>GSheet: Auto login
    end
    
    Browser->>GSheet: Tìm dòng trống cuối cùng
    Browser->>GSheet: Click cell & điền data
    Note right of GSheet: Row 11: A11="Nguyễn Văn A"<br/>B11="0123456789"<br/>C11="nguyenvana@gmail.com"
    
    Browser->>Browser: Take screenshot
    Browser->>Agent: Screenshot + verify
    
    Agent-->>Pipecat: Result { status: "success", screenshot }
```

**Giải thích:**
- Browser Agent nhận structured data từ Pipecat
- Launch Chromium browser (headless hoặc có UI)
- Navigate đến Google Sheets URL
- Tự động login nếu cần (dùng saved credentials)
- Tìm dòng trống cuối cùng trong sheet
- Click vào cells và điền data (giống người dùng thao tác)
- Chụp screenshot để verify
- Trả kết quả về Pipecat

---

#### 2.4. Error Handling - Xử lý lỗi đơn giản

- 3 case chính: voice unclear, validation, browser error

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Pipecat as 🎙️ Pipecat
    participant BrowserUse as 🌐 Browser-Use
    
    User->>Pipecat: 🗣️ Voice input không rõ
    Pipecat-->>User: 🔊 "Không nghe rõ, vui lòng nói lại"
    
    User->>Pipecat: 🗣️ "Email là abc"
    Pipecat->>Pipecat: LLM validate → Invalid email
    Pipecat-->>User: 🔊 "Email không đúng định dạng"
    
    Pipecat->>BrowserUse: Execute automation
    BrowserUse->>BrowserUse: Timeout / Error
    BrowserUse-->>Pipecat: Error result
    Pipecat-->>User: 🔊 "Có lỗi xảy ra, thử lại sau"
```

**Giải thích:**
- **Voice unclear**: STT không nghe rõ → yêu cầu nói lại
- **Validation**: LLM validate format (email, phone) → báo lỗi và hướng dẫn
- **Browser error**: Timeout, không truy cập được sheet, hoặc lỗi automation → thông báo lỗi
- Tất cả phản hồi đều qua TTS để user nghe, giữ trải nghiệm voice-first
- Có thể retry tự động hoặc yêu cầu user thử lại
