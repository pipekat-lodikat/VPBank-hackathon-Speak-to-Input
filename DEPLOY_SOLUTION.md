# Giải Pháp Deploy VPBank Voice Agent lên AWS

## 🎯 Giải Pháp Được Đề Xuất: EC2 Single Instance

**Approach**: Deploy toàn bộ ứng dụng (frontend + backend services) lên 1 EC2 instance và expose frontend qua Nginx reverse proxy.

### ✅ Ưu Điểm

1. **Đơn giản nhất** - Chỉ cần 1 EC2 instance, không cần setup phức tạp
2. **Chi phí thấp** - ~$30-60/tháng (t3.medium/large)
3. **Dễ quản lý** - Tất cả services trên cùng 1 server
4. **Nhanh chóng** - Setup trong 30-60 phút
5. **Phù hợp cho MVP/Demo** - Đủ cho production nhỏ đến trung bình

### 📋 Kiến Trúc

```
Internet
   ↓
EC2 Instance (t3.medium/large)
   ├── Nginx (Port 80/443)
   │   ├── Frontend (Static files từ /frontend/dist)
   │   └── Reverse Proxy → Backend Services
   │
   ├── Voice Bot Service (Port 7860 - internal)
   │   └── WebRTC, STT, TTS, LLM
   │
   └── Browser Agent Service (Port 7863 - internal)
       └── Browser automation, Multi-agent workflow
```

### 🔄 Luồng Request

1. User truy cập `http://<EC2-IP>` → Nginx serve frontend
2. Frontend gọi `/api/*` → Nginx proxy đến Voice Bot (port 7860)
3. Voice Bot gọi Browser Agent (port 7863) qua internal network
4. WebSocket/WebRTC connections được Nginx forward đúng cách

## 📦 Files Đã Tạo

Tất cả files deploy đã được tạo trong thư mục `deploy/`:

- ✅ `ec2-setup.sh` - Setup system dependencies
- ✅ `install-dependencies.sh` - Install Python/Node dependencies  
- ✅ `nginx.conf` - Nginx reverse proxy config
- ✅ `setup-nginx.sh` - Setup Nginx
- ✅ `voice-bot.service` - Systemd service cho Voice Bot
- ✅ `browser-agent.service` - Systemd service cho Browser Agent
- ✅ `configure-services.sh` - Configure systemd services
- ✅ `update-frontend-urls.sh` - Fix frontend URLs cho production
- ✅ `quick-deploy.sh` - Auto deploy script
- ✅ `DEPLOY_GUIDE.md` - Hướng dẫn chi tiết
- ✅ `.env.example` - Template cho environment variables

## 🚀 Các Bước Deploy (Tóm Tắt)

1. **Tạo EC2 Instance**
   - Ubuntu 22.04 LTS
   - t3.medium hoặc t3.large
   - Security Group: mở port 80, 443, 22

2. **Upload Code**
   ```bash
   # SSH vào EC2
   ssh -i key.pem ubuntu@<EC2-IP>
   
   # Clone hoặc upload code
   cd /opt
   git clone <repo> vpbank-voice-agent
   ```

3. **Chạy Deploy Script**
   ```bash
   cd /opt/vpbank-voice-agent
   chmod +x deploy/*.sh
   
   # Tạo .env file
   cp .env.example .env
   nano .env  # Điền credentials
   
   # Quick deploy
   ./deploy/quick-deploy.sh http://<EC2-IP>
   ```

4. **Truy cập ứng dụng**
   - Mở browser: `http://<EC2-IP>`

## 🔧 Cấu Hình Cần Thiết

### Environment Variables (.env)

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
OPENAI_API_KEY=...
BROWSER_SERVICE_URL=http://localhost:7863
```

### Frontend URLs

Frontend hiện hardcode `localhost:7860`. Script `update-frontend-urls.sh` sẽ tự động fix:
- Option 1: Dùng relative URLs (recommended)
- Option 2: Dùng production IP/domain

## 💰 Chi Phí Ước Tính

- **EC2 t3.medium**: ~$30/tháng (on-demand)
- **EC2 t3.large**: ~$60/tháng (on-demand)  
- **Data Transfer**: First 100GB free
- **Total**: ~$30-70/tháng

*Có thể giảm 30-60% nếu dùng Reserved Instances*

## 🔄 Alternatives (Nếu Cần Scale)

Nếu sau này cần scale, có thể migrate sang:

1. **ECS/EKS** - Container orchestration
2. **Elastic Beanstalk** - Platform as a Service
3. **Lambda + API Gateway** - Serverless (cần refactor nhiều)
4. **Multiple EC2 instances** - Load balancer + auto scaling

Nhưng cho **least development effort**, giải pháp EC2 single instance là tốt nhất.

## 📚 Tài Liệu

- Chi tiết: Xem `deploy/DEPLOY_GUIDE.md`
- Quick start: Xem `deploy/README.md`

## ⚠️ Lưu Ý

1. **Security**: Setup SSL/TLS với Let's Encrypt cho production
2. **Monitoring**: Cân nhắc CloudWatch hoặc monitoring tools
3. **Backup**: Backup `.env` và config files
4. **Updates**: Update system packages định kỳ

## 🆘 Troubleshooting

Xem section Troubleshooting trong `deploy/DEPLOY_GUIDE.md` hoặc:

```bash
# Check services
sudo systemctl status voice-bot browser-agent nginx

# View logs
sudo journalctl -u voice-bot -f
sudo journalctl -u browser-agent -f
sudo tail -f /var/log/nginx/error.log
```

