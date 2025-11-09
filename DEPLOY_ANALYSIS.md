# Phân Tích Khả Năng Deploy Lên ECS

## 🔍 Tổng Quan

Hiện tại code **KHÔNG ĐỘNG** để deploy lên ECS vì có nhiều hardcoded URLs. Cần refactor để sử dụng environment variables.

---

## ❌ Vấn Đề Hiện Tại

### 1. Frontend - Hardcoded URLs

#### **ChatPage.tsx**
- `http://localhost:7860/api/auth/verify` (line 341)
- `ws://localhost:7860/ws` (line 379)
- `http://localhost:7860/offer` (line 626)
- `http://localhost:7863/api/live` (line 516)

#### **useTranscripts.ts**
- `http://localhost:7860/api/sessions?limit=50` (line 27)
- `http://localhost:7860/api/sessions/${sessionId}` (line 54)

#### **AuthLogin.tsx & Login.tsx**
- `http://localhost:7860/api/auth/login`
- `http://localhost:7860/api/auth/register`
- `http://localhost:7860/api/auth/forgot-password`
- `http://localhost:7860/api/auth/reset-password`

#### **SessionHistory.tsx**
- `http://localhost:7860/api/sessions?limit=50`

### 2. Backend - Hardcoded URLs

#### **voice_bot.py**
- `BROWSER_SERVICE_URL = os.getenv("BROWSER_SERVICE_URL", "http://localhost:7863")` (line 36)
  - ✅ Đã có env var nhưng default là localhost

#### **main_voice.py**
- Port hardcoded: `port=7860` (line 27)
  - ⚠️ Có thể dùng env var `PORT`

---

## ✅ Giải Pháp

### Bước 1: Tạo Config File cho Frontend

Tạo `frontend/src/config/api.ts`:

```typescript
// API Configuration
const getApiBaseUrl = () => {
  // Production: Use environment variable
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  // Development: Default to localhost
  return 'http://localhost:7860';
};

const getBrowserServiceUrl = () => {
  if (import.meta.env.VITE_BROWSER_SERVICE_URL) {
    return import.meta.env.VITE_BROWSER_SERVICE_URL;
  }
  return 'http://localhost:7863';
};

export const API_BASE_URL = getApiBaseUrl();
export const BROWSER_SERVICE_URL = getBrowserServiceUrl();
export const WS_URL = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://');
```

### Bước 2: Tạo `.env.example` cho Frontend

```bash
# Frontend Environment Variables
VITE_API_BASE_URL=http://localhost:7860
VITE_BROWSER_SERVICE_URL=http://localhost:7863
```

### Bước 3: Update Backend để Support Environment Variables

#### **main_voice.py**
```python
import os
from loguru import logger

PORT = int(os.getenv("PORT", "7860"))
HOST = os.getenv("HOST", "0.0.0.0")

if __name__ == "__main__":
    logger.info(f"🎤 Starting Voice Bot Service...")
    logger.info(f"📡 Service runs on {HOST}:{PORT}")
    logger.info(f"🔗 Connects to Browser Agent Service: {os.getenv('BROWSER_SERVICE_URL', 'http://localhost:7863')}")
    
    app = create_app()
    web.run_app(app, host=HOST, port=PORT)
```

### Bước 4: ECS Task Definition

```json
{
  "containerDefinitions": [
    {
      "name": "voice-bot",
      "image": "your-ecr-repo/voice-bot:latest",
      "environment": [
        {
          "name": "PORT",
          "value": "7860"
        },
        {
          "name": "BROWSER_SERVICE_URL",
          "value": "http://browser-service:7863"
        },
        {
          "name": "AWS_ACCESS_KEY_ID",
          "valueFrom": "arn:aws:secretsmanager:..."
        }
      ],
      "portMappings": [
        {
          "containerPort": 7860,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

### Bước 5: Frontend Build với Environment Variables

```bash
# Build với production URLs
VITE_API_BASE_URL=https://api.yourdomain.com \
VITE_BROWSER_SERVICE_URL=https://browser.yourdomain.com \
npm run build
```

---

## 🚀 Kiến Trúc Deploy Lên ECS

### Option 1: Single ECS Service (Simple)

```
┌─────────────────────────────────┐
│   Application Load Balancer     │
│   (HTTPS/WSS)                   │
└──────────────┬──────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│  ECS Task   │  │  ECS Task    │
│ Voice Bot   │  │ Browser Svc  │
│ :7860       │  │ :7863        │
└─────────────┘  └──────────────┘
```

### Option 2: Separate ECS Services (Recommended)

```
┌─────────────────────────────────┐
│   ALB - Voice Bot Service       │
│   api.yourdomain.com            │
└──────────────┬──────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│  ECS Service│  │  ECS Service│
│ Voice Bot   │  │ Browser Svc │
│ :7860       │  │ :7863        │
└─────────────┘  └──────────────┘
```

---

## 📋 Checklist Deploy

### Frontend
- [ ] Tạo `frontend/src/config/api.ts`
- [ ] Thay thế tất cả hardcoded URLs bằng config
- [ ] Tạo `.env.example`
- [ ] Update build script để inject env vars
- [ ] Test với production URLs

### Backend
- [ ] Update `main_voice.py` để dùng `PORT` env var
- [ ] Đảm bảo `BROWSER_SERVICE_URL` được set đúng
- [ ] Test với environment variables

### Infrastructure
- [ ] Tạo ECS Task Definition
- [ ] Setup Application Load Balancer
- [ ] Configure Security Groups
- [ ] Setup Service Discovery (nếu cần internal communication)
- [ ] Configure Auto Scaling
- [ ] Setup CloudWatch Logs

---

## 🔧 WebRTC & WebSocket Considerations

### WebRTC
- Cần **STUN/TURN servers** cho production
- ALB không support WebRTC trực tiếp → cần **Network Load Balancer (NLB)** hoặc **direct connection**

### WebSocket
- ALB hỗ trợ WebSocket (HTTP/1.1 upgrade)
- Cần configure `idle_timeout` trong ALB target group
- Frontend cần dùng `wss://` (secure WebSocket) cho production

---

## 📝 Next Steps

1. **Refactor Frontend**: Tạo config file và thay thế hardcoded URLs
2. **Update Backend**: Support environment variables
3. **Create Dockerfiles**: Cho cả frontend và backend
4. **Setup ECS**: Task definitions, services, load balancers
5. **Test**: Deploy to staging environment first

---

## ⚠️ Lưu Ý Quan Trọng

1. **CORS**: Cần configure CORS đúng cho production domains
2. **HTTPS/WSS**: Production phải dùng secure connections
3. **Service Discovery**: Nếu services giao tiếp internal, dùng ECS Service Discovery
4. **Secrets Management**: Dùng AWS Secrets Manager cho API keys
5. **Monitoring**: Setup CloudWatch alarms và logs

