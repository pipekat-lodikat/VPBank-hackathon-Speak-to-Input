# CX Genie - AI Voice Bot cho Thu hồi Công nợ

<div align="center">
  
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Pipecat](https://img.shields.io/badge/Pipecat-0.0.78-green.svg)](https://docs.pipecat.ai/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

**Hệ thống Voice Bot AI thông minh sử dụng WebRTC, AWS Services và Pipecat Framework**

[Tài liệu Kỹ thuật](#tài-liệu-kỹ-thuật) • [Cài đặt](#cài-đặt) • [Chạy dự án](#chạy-dự-án) • [Kiến trúc](#kiến-trúc-hệ-thống)

</div>

---

## 📋 Tổng Quan

CX Genie là một hệ thống Voice Bot AI chuyên nghiệp, được thiết kế để tự động hóa quy trình chăm sóc khách hàng và thu hồi công nợ qua cuộc gọi điện thoại. Bot có khả năng:

-  Giao tiếp tự nhiên bằng tiếng Việt với độ trễ thấp 
-  Xác minh thông tin khách hàng theo quy trình chuẩn
-  Tra cứu và cung cấp thông tin hợp đồng, công nợ
-  Phát hiện và phản hồi theo ý định (intent) của người dùng
-  Ghi lại toàn bộ cuộc hội thoại để audit và phân tích

##  Kịch Bản Hoạt Động

### Luồng Cuộc gọi Mẫu

```
👨‍💼 Bot: Chào anh/chị, cảm ơn anh/chị đã liên hệ đến Công ty Mua Bán Nợ ABC. Em là Nghiêm, em có thể hỗ trợ gì cho anh/chị ạ?

👤 Khách: Anh muốn hỏi khoản vay đã thanh toán chưa?

👨‍💼 Bot: Dạ em xin phép hỏi tên anh/chị là gì ạ?

👤 Khách: Anh Nguyễn Nhân Khánh em.

👨‍💼 Bot: Cho em xin số căn cước công dân của số hợp đồng vay?

👤 Khách: 021681099

👨‍💼 Bot: Và cuối cùng cho em xin ngày tháng năm sinh của anh/chị ạ?

👤 Khách: Ngày 31, tháng 12, năm 1989

👨‍💼 Bot: Dạ, hiện tại theo thông tin số căn cước công dân anh cung cấp,
         em kiểm tra anh có 1 hợp đồng vay tiền mặt năm 2018 bên XYZ. 
         Hiện tại hợp đồng này vẫn chưa thanh toán xong, 
         đã quá thời hạn thanh toán nên XYZ đã bán nợ qua bên công ty ABC. 
         Em kiểm tra hợp đồng này của anh, 
         mình còn nợ lại tổng số tiền là ba mươi sáu triệu tám trăm sáu mươi hai nghìn đồng nha anh,
         bao gồm gốc, lãi và phí phạt ạ.
         Dạ anh còn cần em hỗ trợ gì thêm không ạ?

👤 Khách: Oke anh hiểu rồi, cảm ơn em.

👨‍💼 Bot: Em xin cảm ơn anh đã liên hệ. Chúc anh một ngày tốt lành ạ!
```

##  Kiến Trúc Hệ Thống

### Tech Stack

| Thành phần | Công nghệ | Vai trò |
|-----------|-----------|---------|
| **Framework Core** | [Pipecat AI](https://docs.pipecat.ai/) v0.0.78 | Framework xử lý pipeline âm thanh real-time |
| **Conversation Flow** | Pipecat Flows v0.0.17 | Quản lý luồng hội thoại và state machine |
| **Backend Server** | Python 3.10+ / aiohttp | Server bất đồng bộ xử lý WebRTC signaling |
| **Frontend UI** | React 19 + TypeScript + Vite | Giao diện người dùng và WebRTC client |
| **Transport Layer** | Small WebRTC (prebuilt) | Kết nối âm thanh hai chiều qua WebRTC |
| **Speech-to-Text** | AWS Transcribe (Vietnamese) | Phiên âm giọng nói thành văn bản |
| **LLM** | AWS Bedrock (Claude 3.5 Sonnet) | Hiểu ngữ cảnh và tạo phản hồi thông minh |
| **Text-to-Speech** | ElevenLabs (eleven_flash_v2_5) | Tổng hợp giọng nói tiếng Việt tự nhiên |
| **VAD** | Silero VAD Analyzer | Phát hiện hoạt động giọng nói |
| **Intent Detection** | Custom API (CX Genie Core AI) | Phân tích ý định người dùng |

### Cấu trúc Dự án

```
cxgenie-aiagent-roleplay/
├── src/                              # Backend Python source code
│   ├── __init__.py
│   ├── bot.py                        #  Core: WebRTC server & Pipecat pipeline orchestrator
│   ├── flow.py                       #  Logic nghiệp vụ & state machine
│   ├── prompt.py                     #  System & task prompts cho LLM
│   ├── waiting_sound_processor.py   #  Custom processor: âm thanh chờ
│   ├── data/
│   │   └── mock_data.json           #  Dữ liệu khách hàng giả lập
│   ├── assets/
│   │   ├── waiting_sound.mp3        # Âm thanh chờ gốc
│   │   ├── waiting_sound.pcm        # Âm thanh chờ đã tối ưu (pre-converted)
│   │   └── waiting_sound_metadata.json
│   ├── output/
│   │   └── result.json              # Kết quả xác minh tổng hợp
│   └── transcripts/                 #  Lưu transcript từng cuộc gọi
│
├── pipecat-react-ui/                 # Frontend React application
│   ├── src/
│   │   ├── App.tsx                  #  Main component: WebRTC client & UI
│   │   ├── main.tsx
│   │   ├── index.css
│   │   └── vite-env.d.ts
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── requirements.txt                  # Python dependencies
├── .env.example                     # Template file cấu hình môi trường
├── .env                             #  File cấu hình (không commit)
├── README.md                        #  Tài liệu này
└── tech_docs.md                     #  Tài liệu kỹ thuật chi tiết
```

## 🚀 Cài Đặt

### Yêu Cầu Hệ Thống

#### Backend (Python)
- **Python**: 3.10 hoặc cao hơn
- **Hệ điều hành**: 
  - Linux/macOS: Chạy trực tiếp
  - Windows: **Bắt buộc** sử dụng WSL (Windows Subsystem for Linux) do dependencies của Pipecat
- **Công cụ**: `pip`, `venv` hoặc `conda`

#### Frontend (React)
- **Node.js**: 18.0 hoặc cao hơn
- **npm** hoặc **yarn**

#### Services: 
- AWS Account với quyền truy cập:
  - AWS Transcribe
  - AWS Bedrock (Claude 3.5 Sonnet)
- ElevenLabs API Key (hoặc OpenAI API Key cho development)
- CX Genie Intent Detection API

### Bước 1: Clone Repository

```bash
git clone https://github.com/renova-cloud/cxgenie-aiagent-roleplay.git
cd cxgenie-aiagent-roleplay
```

### Bước 2: Cài đặt Backend (Python)

#### 2.1. Tạo môi trường ảo

```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt (Linux/macOS)
source venv/bin/activate

# Kích hoạt (Windows WSL)
source venv/bin/activate
```

#### 2.2. Cài đặt dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Lưu ý quan trọng về Dependencies:**
- `pipecat-ai[daily,aws,silero,elevenlabs]`: Core framework với các extension
- `pipecat-ai-flows[aws]`: Quản lý conversation flow
- `pipecat-ai-small-webrtc-prebuilt`: Transport layer cho WebRTC
- Một số package có thể yêu cầu build tools (gcc, make) trên Linux

#### 2.3. Cấu hình biến môi trường

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Mở file `.env` và điền các thông tin cần thiết:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=ap-southeast-1

# ElevenLabs TTS (Production)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id

# OpenAI TTS (Development - Optional)
OPENAI_API_KEY=your_openai_api_key

# Intent Detection API (CX Genie Core AI)
INTENT_API_ENDPOINT=https://call-center-coreai.dev.cxgenie.ai/intent-detection
```


### Bước 3: Cài đặt Frontend (React)

```bash
cd pipecat-react-ui

# Cài đặt dependencies
npm install

# Hoặc sử dụng yarn
yarn install
```




## ▶ Chạy Dự Án

### Chế độ Development 

Chạy backend và frontend đồng thời trong 2 terminal riêng biệt.

#### Terminal 1: Khởi động Backend Server

```bash
# Kích hoạt virtual environment (nếu chưa)
source venv/bin/activate

# Chạy server
python main.py
```

**Kết quả mong đợi:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860
```

Server sẽ lắng nghe trên các endpoint:
- `http://localhost:7860/offer` - WebRTC signaling (SDP offer/answer)
- `ws://localhost:7860/ws` - WebSocket cho transcript streaming
- `http://localhost:7860/` - Health check

#### Terminal 2: Khởi động Frontend UI

```bash
cd pipecat-react-ui

# Chạy development server
npm run dev

# Hoặc
yarn dev
```

**Kết quả mong đợi:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Sử dụng Ứng dụng

1. **Mở trình duyệt** và truy cập `http://localhost:5173`
2. **Cho phép truy cập Microphone** khi trình duyệt yêu cầu
3. **Chọn thiết bị âm thanh:**
   - Audio Input Device (Micro)
   - Audio Output Device (Loa/Tai nghe)
4. **Click "Start Conversation"** để bắt đầu cuộc gọi
5. **Nói chuyện** với bot như trong kịch bản mẫu
6. **Click "End Conversation"** khi muốn kết thúc



### Chuyển đổi giữa OpenAI và ElevenLabs TTS

Trong `src/bot.py`, comment/uncomment để chuyển đổi:

```python
# ElevenLabs 
tts = ElevenLabsTTSService(
    api_key=elevenlabs_api_key,
    voice_id=elevenlabs_voice_id,
    model="eleven_flash_v2_5",
    # ... các tham số khác
)

# OpenAI (Development - Tiết kiệm chi phí)
# tts = OpenAITTSService(
#     api_key=openai_api_key,
#     voice="nova",
#     model="gpt-4o-mini-tts"
# )
```

### Tùy chỉnh Prompts

Chỉnh sửa file `src/prompt.py` để thay đổi:
- Nhân cách của bot (persona)
- Quy tắc đọc số tiền, số CCCD
- Kịch bản hội thoại chi tiết



### Tham khảo Logs

Các file logs quan trọng:
- `src/transcripts/conversation_*.json` - Transcript của từng cuộc gọi
- `src/output/result.json` - Kết quả xác minh khách hàng

##  Tài Liệu Kỹ Thuật

Để hiểu sâu hơn về kiến trúc và cách hoạt động của hệ thống, vui lòng đọc:

- **`Technical Documentation`** - Tài liệu kỹ thuật chi tiết về:
  - Kiến trúc Backend Layer (bot.py, flow.py, prompt.py)
  - Kiến trúc Frontend Layer (App.tsx, WebRTC Client)
  - Pipecat Pipeline Architecture
  - Prompt Engineering Techniques
  - Conversation Flow Management

Gồm file  file Technical Documentation.docx chinh va file Reference Documentation.docx tham khao

- **[Pipecat Documentation](https://docs.pipecat.ai/)** - Framework documentation
  - [Core Concepts](https://docs.pipecat.ai/guides/learn/overview)
  - [Processors](https://docs.pipecat.ai/guides/learn/processors)
  - [Transports](https://docs.pipecat.ai/guides/learn/transports)
  - [Flows](https://docs.pipecat.ai/guides/flows/overview)



## 📄 License

Proprietary - © 2025 Renova Cloud. All rights reserved.

---

<div align="center">
  
**Phát triển bởi Renova Cloud - AI Factory**





