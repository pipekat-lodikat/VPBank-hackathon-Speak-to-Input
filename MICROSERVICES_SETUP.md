# 🏗️ Microservices Architecture Setup

VPBank Voice Agent được tách thành **3 microservices riêng biệt** để optimize và scale độc lập.

---

## 📊 Architecture Overview

```
┌─────────────────┐
│  Voice Bot      │  Port 7860
│  (WebRTC/STT/TTS)│
└────────┬────────┘
         │ HTTP API
         ↓
┌─────────────────┐
│ Task Queue      │  Port 7862
│ Service         │
│ (HTTP REST API) │
└────────┬────────┘
         │ HTTP API
         ↓
┌─────────────────┐
│ Browser Worker  │  Port N/A (background)
│ (Workflow/Browser)│
└─────────────────┘
```

---

## 🚀 Services

### 1. **Voice Bot Service** (`main_voice.py`)
- **Port:** 7860
- **Chức năng:**
  - WebRTC server
  - Speech-to-Text (AWS Transcribe)
  - Text-to-Speech (OpenAI TTS)
  - LLM Conversation (AWS Bedrock)
  - WebSocket cho frontend
- **Giao tiếp:** Gửi tasks đến Task Queue Service

### 2. **Task Queue Service** (`services/task_queue_service/main.py`)
- **Port:** 7862
- **Chức năng:**
  - HTTP REST API để quản lý task queue
  - Long polling cho task consumption
  - Task status tracking
- **Endpoints:**
  - `POST /api/tasks/push` - Push task
  - `GET /api/tasks/pop` - Pop task (long polling)
  - `PATCH /api/tasks/{task_id}` - Update task
  - `GET /api/tasks/{task_id}` - Get task
  - `GET /api/health` - Health check

### 3. **Browser Worker Service** (`main_worker.py`)
- **Port:** N/A (background service)
- **Chức năng:**
  - Poll tasks từ Task Queue Service
  - Execute LangGraph workflow
  - Browser automation (browser-use)
- **Giao tiếp:** Lấy tasks từ Task Queue Service

---

## 🐳 Docker Setup (Recommended)

### Prerequisites
- Docker & Docker Compose
- `.env` file với đầy đủ credentials

### Start All Services

```bash
# Build và start tất cả services
docker-compose up --build

# Hoặc chạy background
docker-compose up -d

# Xem logs
docker-compose logs -f

# Xem logs của service cụ thể
docker-compose logs -f voice-bot
docker-compose logs -f browser-worker
docker-compose logs -f task-queue
```

### Stop Services

```bash
docker-compose down
```

---

## 💻 Manual Setup (Development)

### Terminal 1: Task Queue Service

```bash
# Activate venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Start Task Queue Service
python services/task_queue_service/main.py
```

**Expected output:**
```
🚀 Starting Task Queue Service...
📡 REST API Server on port 7862
```

### Terminal 2: Voice Bot Service

```bash
# Activate venv (same venv)
.\venv\Scripts\activate

# Set environment variable
$env:TASK_QUEUE_SERVICE_URL="http://localhost:7862"  # Windows PowerShell
# export TASK_QUEUE_SERVICE_URL="http://localhost:7862"  # Linux/Mac

# Start Voice Bot
python main_voice.py
```

**Expected output:**
```
🎤 Starting Voice Bot Service...
📡 Service runs on port 7860
```

### Terminal 3: Browser Worker Service

```bash
# Activate venv (same venv)
.\venv\Scripts\activate

# Set environment variable
$env:TASK_QUEUE_SERVICE_URL="http://localhost:7862"  # Windows PowerShell
# export TASK_QUEUE_SERVICE_URL="http://localhost:7862"  # Linux/Mac

# Start Browser Worker
python main_worker.py
```

**Expected output:**
```
🔨 Starting Browser Worker Service...
📡 Service connects to Task Queue Service (port 7862)
```

---

## 🔧 Environment Variables

Tất cả services share cùng `.env` file:

```env
# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# OpenAI (TTS)
OPENAI_API_KEY=your_key

# Task Queue Service URL (cho Voice Bot & Browser Worker)
TASK_QUEUE_SERVICE_URL=http://localhost:7862

# Form URLs
LOAN_FORM_URL=http://use-case-1-loan-origination.s3-website-us-west-2.amazonaws.com
CRM_FORM_URL=http://use-case-2-crm-update.s3-website-us-west-2.amazonaws.com
HR_FORM_URL=http://use-case-3-hr-workflow.s3-website-us-west-2.amazonaws.com
COMPLIANCE_FORM_URL=http://use-case-4-compliance-reporting.s3-website-us-west-2.amazonaws.com
OPERATIONS_FORM_URL=http://use-case-5-operations-validation.s3-website-us-west-2.amazonaws.com
```

---

## 📡 API Examples

### Push Task (Voice Bot → Task Queue)

```bash
curl -X POST http://localhost:7862/api/tasks/push \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "loan",
    "user_message": "Full conversation history here...",
    "session_id": "session_123"
  }'
```

### Pop Task (Browser Worker ← Task Queue)

```bash
curl http://localhost:7862/api/tasks/pop
# Long polling: waits up to 30 seconds for a task
```

### Get Task Status

```bash
curl http://localhost:7862/api/tasks/task_123
```

### Health Check

```bash
curl http://localhost:7862/api/health
```

---

## 🔄 Migration Path

### Current (Monolithic)
```
main.py → Voice Bot + Browser Worker (same process)
```

### New (Microservices)
```
main_voice.py → Voice Bot (port 7860)
main_worker.py → Browser Worker (background)
services/task_queue_service/main.py → Task Queue (port 7862)
```

**Migration steps:**
1. ✅ Task Queue Service created
2. ⏳ Update Voice Bot to use Task Queue API
3. ⏳ Update Browser Worker to use Task Queue API
4. ⏳ Test all services
5. ⏳ Deploy separately

---

## 🎯 Benefits

1. **Independent Scaling:**
   - Scale Voice Bot instances khi có nhiều users
   - Scale Browser Worker instances khi có nhiều tasks
   - Task Queue Service có thể dùng Redis backend

2. **Fault Isolation:**
   - Nếu Voice Bot crash, Browser Worker vẫn chạy
   - Nếu Browser Worker crash, Voice Bot vẫn nhận requests

3. **Resource Optimization:**
   - Voice Bot: Lightweight, chỉ cần STT/TTS/LLM
   - Browser Worker: Heavy, cần Playwright + browser-use
   - Có thể deploy Browser Worker trên machines mạnh hơn

4. **Development:**
   - Test từng service riêng
   - Deploy updates độc lập
   - Dễ debug hơn

---

## 📝 TODO

- [ ] Update `bot_multi_agent.py` để dùng `TaskQueueAPIClient`
- [ ] Update `workflow_worker.py` để dùng `TaskQueueAPIClient`
- [ ] Test end-to-end flow
- [ ] Add Redis backend option cho Task Queue Service
- [ ] Add monitoring/logging (Prometheus/Grafana)
- [ ] Add service discovery (Consul/Eureka)

