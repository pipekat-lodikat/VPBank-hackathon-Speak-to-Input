# 🚀 Quick Start Guide

Hướng dẫn nhanh để chạy VPBank Voice Agent.

## 📋 Yêu Cầu

1. Python 3.11
2. Virtual environment đã được activate
3. Dependencies đã được install (`pip install -r requirements.txt`)
4. `.env` file đã được config với AWS và OpenAI credentials

## 🏃 Cách Chạy

### Bước 1: Khởi động Browser Agent Service

Mở **Terminal 1**:

```bash
python main_browser_service.py
```

Chờ đến khi thấy:
```
✅ Workflow initialized (model: ...)
```

Service chạy tại: `http://localhost:7863`

### Bước 2: Khởi động Voice Bot Service

Mở **Terminal 2** (terminal mới):

```bash
python main_voice.py
```

Chờ đến khi thấy:
```
🚀 Voice bot ready - workflow will execute directly when needed
```

Service chạy tại: `http://localhost:7860`

### Bước 3: Mở Frontend

Mở browser và truy cập: `http://localhost:7860`

## ✅ Kiểm Tra

### Health Check

```bash
# Kiểm tra Browser Service
curl http://localhost:7863/api/health

# Kết quả mong đợi:
# {"status": "healthy", "service": "browser-agent-service", "workflow_loaded": true}
```

### Logs

- **Terminal 1**: Hiển thị logs của Browser Agent Service
- **Terminal 2**: Hiển thị logs của Voice Bot Service

## 🔧 Troubleshooting

### Lỗi: "Cannot connect to Browser Service"

- Đảm bảo Browser Agent Service đã start trước
- Kiểm tra port 7863 có bị chiếm không
- Set `BROWSER_SERVICE_URL` trong `.env` nếu cần

### Lỗi: "Module not found"

- Đảm bảo virtual environment đã activate
- Chạy lại: `pip install -r requirements.txt`

### Lỗi: "AWS credentials not found"

- Kiểm tra `.env` file có đúng path không
- Đảm bảo các biến `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` đã được set

## 📝 Ghi Chú

- **Luôn start Browser Agent Service trước** Voice Bot Service
- Nếu thay đổi port, update `BROWSER_SERVICE_URL` trong `.env` hoặc environment variable
- Xem `README.md` để biết chi tiết về configuration và architecture

