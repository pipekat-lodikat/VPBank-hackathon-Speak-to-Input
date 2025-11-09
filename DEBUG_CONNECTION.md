# Hướng Dẫn Debug Kết Nối WebRTC

## 🔍 Vấn Đề
Kết nối giữa frontend (nút Start) và backend `main_voice.py` không hoạt động.

## ✅ Đã Cải Thiện

### 1. Backend (`src/voice_bot.py`)
- ✅ Thêm logging chi tiết cho endpoint `/offer`
- ✅ Cải thiện error handling
- ✅ Log request headers, body, và response

### 2. Frontend (`frontend/src/pages/ChatPage.tsx`)
- ✅ Thêm console logs để track connection flow
- ✅ Cải thiện error messages

## 🧪 Cách Debug

### Bước 1: Kiểm Tra Backend Đang Chạy

```bash
# Chạy backend
python main_voice.py

# Kiểm tra logs - bạn sẽ thấy:
# 🎤 Starting Voice Bot Service...
# 📡 Service runs on 0.0.0.0:7860
```

### Bước 2: Kiểm Tra Frontend Console

Mở **Developer Console** (F12) và bấm nút **Start**. Bạn sẽ thấy:

```
🔗 Connecting to WebRTC endpoint: http://localhost:7860/offer
📤 Sending WebRTC offer...
📥 Response status: 200 OK
✅ Received WebRTC answer: answer
```

### Bước 3: Kiểm Tra Backend Logs

Khi frontend gọi `/offer`, backend sẽ log:

```
📥 Received WebRTC offer request
🔧 Creating WebRTC connection...
🔧 Initializing WebRTC connection with offer...
🔧 Getting answer from WebRTC connection...
✅ Got answer: type=answer, sdp_length=...
🚀 Starting bot pipeline...
✅ Bot pipeline started successfully, returning answer to client
```

## 🐛 Các Lỗi Thường Gặp

### Lỗi 1: "Failed to fetch" hoặc "Network error"

**Nguyên nhân:**
- Backend không chạy
- Port không đúng
- CORS bị chặn

**Giải pháp:**
1. Kiểm tra backend đang chạy: `curl http://localhost:7860/api/sessions`
2. Kiểm tra port trong `frontend/src/config/api.ts`
3. Kiểm tra CORS headers trong backend logs

### Lỗi 2: "Invalid offer" (400)

**Nguyên nhân:**
- Request body không đúng format
- Missing `sdp` hoặc `type`

**Giải pháp:**
- Kiểm tra console logs xem request body có đúng không
- Backend sẽ log: `⚠️ Invalid offer: type=..., has_sdp=...`

### Lỗi 3: "Server error: 500"

**Nguyên nhân:**
- Lỗi trong WebRTC initialization
- Lỗi trong bot pipeline

**Giải pháp:**
1. Xem backend logs chi tiết (có `exc_info=True`)
2. Kiểm tra environment variables (AWS credentials, etc.)

### Lỗi 4: Connection timeout

**Nguyên nhân:**
- ICE servers không accessible
- Firewall chặn WebRTC

**Giải pháp:**
1. Kiểm tra STUN/TURN servers trong `src/voice_bot.py`
2. Test với public STUN server: `stun:stun.l.google.com:19302`

## 🔧 Kiểm Tra Cấu Hình

### Frontend Config (`frontend/src/config/api.ts`)

```typescript
// Development
API_BASE_URL = 'http://localhost:7860'

// Production (set via env var)
VITE_API_BASE_URL=https://api.yourdomain.com
```

### Backend Config (`main_voice.py`)

```python
PORT = int(os.getenv("PORT", "7860"))
HOST = os.getenv("HOST", "0.0.0.0")
```

## 📋 Checklist Debug

- [ ] Backend đang chạy và log "Starting Voice Bot Service"
- [ ] Frontend console không có CORS errors
- [ ] Frontend console hiển thị "Connecting to WebRTC endpoint"
- [ ] Backend logs hiển thị "Received WebRTC offer request"
- [ ] Response status là 200 (không phải 400/500)
- [ ] WebRTC connection state chuyển sang "connected"

## 🚀 Test Thủ Công

### Test Backend Endpoint

```bash
# Test OPTIONS (CORS preflight)
curl -X OPTIONS http://localhost:7860/offer \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -v

# Test POST (should return 400 without valid offer)
curl -X POST http://localhost:7860/offer \
  -H "Content-Type: application/json" \
  -d '{"type":"offer","sdp":"test"}' \
  -v
```

### Test Frontend Config

Mở browser console và chạy:

```javascript
// Kiểm tra config
import { API_ENDPOINTS, WS_URL } from './config/api';
console.log('API Endpoints:', API_ENDPOINTS);
console.log('WebSocket URL:', WS_URL);

// Test endpoint có accessible không
fetch(API_ENDPOINTS.WEBRTC_OFFER, { method: 'OPTIONS' })
  .then(r => console.log('CORS OK:', r.status))
  .catch(e => console.error('CORS Error:', e));
```

## 📞 Nếu Vẫn Không Hoạt Động

1. **Copy toàn bộ logs** từ:
   - Browser Console (F12)
   - Backend terminal
   
2. **Kiểm tra:**
   - Network tab trong DevTools (xem request/response)
   - Backend có nhận được request không
   - CORS headers có đúng không

3. **Thông tin cần cung cấp:**
   - Browser console logs
   - Backend logs
   - Network request details (Headers, Payload, Response)
   - Error messages chính xác

