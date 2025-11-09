# VPBank Voice Agent - Production Architecture

**Last Updated**: 2025-11-09  
**Environment**: Production (AWS us-east-1)

---

## Architecture Overview

```
                                    Internet
                                       │
                                       ▼
                    ┌──────────────────────────────────┐
                    │      CloudFront CDN              │
                    │  d359aaha3l67dn.cloudfront.net   │
                    │  Distribution: E157XTMGCFVXEO    │
                    │                                  │
                    │  • Global Edge Locations         │
                    │  • HTTPS Enforcement             │
                    │  • DDoS Protection               │
                    │  • Caching & Compression         │
                    └──────────┬───────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                │ Default (/)                 │ /api/*, /offer, /ws
                │ Static Files                │ Dynamic Backend
                ▼                             ▼
    ┌───────────────────────┐    ┌───────────────────────────┐
    │   S3 Origin           │    │   ALB Origin              │
    │   Frontend Bucket     │    │   vpbank-voice-agent-alb  │
    │                       │    │                           │
    │   • React SPA         │    │   • Port 80 (HTTP)        │
    │   • Static Assets     │    │   • Health Checks         │
    │   • index.html        │    │   • Target Groups         │
    └───────────────────────┘    └──────────┬────────────────┘
                                            │
                                            ▼
                              ┌─────────────────────────────┐
                              │   ECS Fargate Cluster       │
                              │   vpbank-voice-agent-cluster│
                              └──────────┬──────────────────┘
                                         │
                        ┌────────────────┴────────────────┐
                        │                                 │
                        ▼                                 ▼
            ┌───────────────────────┐      ┌───────────────────────┐
            │  Voice Bot Service    │      │  Browser Agent Service│
            │  Port: 7860           │      │  Port: 7863           │
            │  Tasks: 2             │      │  Tasks: 2             │
            │                       │      │                       │
            │  • WebRTC (Pipecat)   │◄────►│  • Playwright         │
            │  • AWS Transcribe     │ HTTP │  • browser-use        │
            │  • AWS Bedrock        │      │  • GPT-4              │
            │  • ElevenLabs TTS     │      │  • Form Automation    │
            │  • WebSocket /ws      │      │                       │
            └───────────────────────┘      └───────────────────────┘
                        │                              │
                        ▼                              ▼
            ┌───────────────────────┐      ┌───────────────────────┐
            │  AWS Services         │      │  External APIs        │
            │                       │      │                       │
            │  • Cognito (Auth)     │      │  • OpenAI GPT-4       │
            │  • DynamoDB (Sessions)│      │  • ElevenLabs TTS     │
            │  • Transcribe (STT)   │      │                       │
            │  • Bedrock (LLM)      │      │                       │
            └───────────────────────┘      └───────────────────────┘
```

---

## Component Details

### CloudFront Distribution

**ID**: E157XTMGCFVXEO  
**Domain**: d359aaha3l67dn.cloudfront.net  
**Status**: Deployed & Enabled

**Origins**:
1. **S3-vpbank-voice-agent-frontend-590183822512**
   - Type: S3 bucket
   - Purpose: Static frontend files
   - Access: Origin Access Control (OAC)

2. **ALB-backend**
   - Type: Application Load Balancer
   - Domain: vpbank-voice-agent-alb-1745174960.us-east-1.elb.amazonaws.com
   - Protocol: HTTP (port 80)

**Cache Behaviors**:

| Path Pattern | Origin | TTL | Methods | Caching |
|--------------|--------|-----|---------|---------|
| `/` (default) | S3 | 3600s | GET, HEAD, OPTIONS | Yes |
| `/api/*` | ALB | 0s | All | No |
| `/offer` | ALB | 0s | All | No |
| `/ws` | ALB | 0s | All | No |
| `/health` | ALB | 0s | GET | No |
| `/metrics` | ALB | 0s | GET | No |

**Features**:
- HTTPS redirect enforced
- Compression enabled
- HTTP/2 enabled
- IPv6 enabled
- SPA routing (403/404 → index.html)

---

### S3 Frontend Bucket

**Name**: vpbank-voice-agent-frontend-590183822512  
**Region**: us-east-1  
**Access**: Private (via CloudFront OAC only)

**Contents**:
```
/
├── index.html                    (478 bytes)
├── assets/
│   ├── index-DP-Y9uXp.js        (823 KB) ← Main app bundle
│   └── index-aEJbKnow.css       (46 KB)  ← Styles
├── LogoVPBank_Header.svg         (27 KB)
├── icon.png                      (25 KB)
└── vite.svg                      (1.5 KB)
```

**Deployment Method**:
```bash
aws s3 sync frontend/dist/ s3://vpbank-voice-agent-frontend-590183822512/ --delete
aws cloudfront create-invalidation --distribution-id E157XTMGCFVXEO --paths "/*"
```

---

### Application Load Balancer

**Name**: vpbank-voice-agent-alb  
**DNS**: vpbank-voice-agent-alb-1745174960.us-east-1.elb.amazonaws.com  
**Type**: Application Load Balancer  
**Scheme**: Internet-facing

**Target Groups**:
- **vpbank-voice-bot-tg**: Port 7860 (Voice Bot)
- **vpbank-browser-agent-tg**: Port 7863 (Browser Agent)

**Health Checks**:
- Voice Bot: `GET /health`
- Browser Agent: `GET /api/health`
- Interval: 30s
- Timeout: 10s
- Healthy threshold: 2
- Unhealthy threshold: 3

---

### ECS Fargate Cluster

**Name**: vpbank-voice-agent-cluster  
**Region**: us-east-1  
**Launch Type**: Fargate

#### Voice Bot Service

**Service Name**: voice-bot  
**Desired Count**: 2  
**Port**: 7860

**Container**:
- Image: 590183822512.dkr.ecr.us-east-1.amazonaws.com/vpbank-voice-bot:latest
- CPU: 2 vCPU
- Memory: 4 GB
- Command: `python main_voice.py`

**Environment Variables**:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION=us-east-1
- BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
- ELEVENLABS_API_KEY
- ELEVENLABS_VOICE_ID
- BROWSER_SERVICE_URL=http://browser-agent:7863
- COGNITO_USER_POOL_ID
- COGNITO_CLIENT_ID
- DYNAMODB_TABLE_NAME=vpbank-sessions

**Endpoints**:
- `POST /offer` - WebRTC offer/answer
- `GET /ws` - WebSocket for transcripts
- `GET /health` - Health check

#### Browser Agent Service

**Service Name**: browser-agent  
**Desired Count**: 2  
**Port**: 7863

**Container**:
- Image: 590183822512.dkr.ecr.us-east-1.amazonaws.com/vpbank-browser-agent:latest
- CPU: 2 vCPU
- Memory: 4 GB
- Command: `python main_browser_service.py`

**Environment Variables**:
- OPENAI_API_KEY
- LOG_LEVEL=INFO

**Endpoints**:
- `POST /api/execute` - Execute browser automation
- `GET /api/health` - Health check
- `GET /api/live-url` - Get current browser URL

---

## Data Flow

### User Request Flow

1. **User accesses**: https://d359aaha3l67dn.cloudfront.net/
2. **CloudFront** serves cached `index.html` from S3
3. **Browser loads** React app (`index-DP-Y9uXp.js`)
4. **User clicks** "Start Conversation"
5. **Frontend sends** WebRTC offer to `/offer` (via CloudFront → ALB → ECS)
6. **Voice Bot** establishes WebRTC connection
7. **User speaks** → Audio stream via WebRTC
8. **Voice Bot processes**:
   - AWS Transcribe: Speech → Text
   - AWS Bedrock (Claude): Text → Intent + Data extraction
   - ElevenLabs: Response → Speech
9. **Voice Bot sends** extracted data to Browser Agent via HTTP
10. **Browser Agent**:
    - GPT-4 plans actions
    - Playwright executes form filling
    - Returns success/failure
11. **Voice Bot** confirms to user via voice

### WebSocket Transcript Flow

1. **Frontend** connects to `wss://d359aaha3l67dn.cloudfront.net/ws`
2. **Voice Bot** sends real-time transcripts:
   ```json
   {
     "type": "transcript",
     "role": "user|assistant",
     "content": "Transcript text",
     "timestamp": "2025-11-09T16:00:00Z"
   }
   ```
3. **Frontend** displays in chat panel

---

## Security

### Network Security

**CloudFront**:
- HTTPS enforced (TLS 1.2+)
- Origin Access Control for S3
- DDoS protection (AWS Shield Standard)

**ALB**:
- Security groups restrict access
- Health checks verify service availability

**ECS**:
- Private subnets (no direct internet access)
- NAT Gateway for outbound traffic
- IAM roles for AWS service access

### Application Security

**Authentication**:
- AWS Cognito user pools
- JWT token validation
- Session management via DynamoDB

**Data Protection**:
- PII masking in logs
- Encrypted environment variables
- Secrets Manager for sensitive data

**Rate Limiting**:
- CloudFront rate limiting
- Application-level throttling

---

## Monitoring & Logging

### CloudWatch Logs

**Log Groups**:
- `/ecs/vpbank-voice-bot` - Voice Bot logs
- `/ecs/vpbank-browser-agent` - Browser Agent logs

**Retention**: 7 days

### CloudWatch Metrics

**ECS**:
- CPUUtilization
- MemoryUtilization
- TaskCount

**ALB**:
- TargetResponseTime
- HealthyHostCount
- RequestCount
- HTTPCode_Target_4XX_Count
- HTTPCode_Target_5XX_Count

**CloudFront**:
- Requests
- BytesDownloaded
- 4xxErrorRate
- 5xxErrorRate

---

## Deployment Process

### Frontend Deployment

```bash
# 1. Build
cd frontend
npm run build

# 2. Deploy to S3
aws s3 sync dist/ s3://vpbank-voice-agent-frontend-590183822512/ --delete

# 3. Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id E157XTMGCFVXEO \
  --paths "/*"
```

**Downtime**: None (cache invalidation takes 2-5 min)

### Backend Deployment

```bash
# 1. Build Docker image
docker build -t vpbank-voice-bot:latest .

# 2. Tag and push to ECR
docker tag vpbank-voice-bot:latest \
  590183822512.dkr.ecr.us-east-1.amazonaws.com/vpbank-voice-bot:latest
docker push 590183822512.dkr.ecr.us-east-1.amazonaws.com/vpbank-voice-bot:latest

# 3. Update ECS service
aws ecs update-service \
  --cluster vpbank-voice-agent-cluster \
  --service voice-bot \
  --force-new-deployment
```

**Downtime**: None (rolling deployment)

---

## Cost Optimization

**Estimated Monthly Costs**:

| Service | Usage | Cost |
|---------|-------|------|
| CloudFront | 1TB data transfer | $85 |
| S3 | 2GB storage + requests | $1 |
| ALB | 730 hours + LCU | $25 |
| ECS Fargate | 4 tasks × 2 vCPU × 4GB | $120 |
| AWS Transcribe | 10,000 minutes | $240 |
| AWS Bedrock | 10M tokens | $30 |
| DynamoDB | On-demand | $5 |
| **Total** | | **~$506/month** |

**Optimization Tips**:
- Enable CloudFront caching for static assets
- Use LLM response caching
- Set DynamoDB TTL for old sessions
- Use Fargate Spot for non-critical tasks

---

## Disaster Recovery

### Backup Strategy

**S3 Frontend**:
- Versioning enabled
- Cross-region replication (optional)

**DynamoDB**:
- Point-in-time recovery enabled
- On-demand backups

**ECR Images**:
- Image scanning enabled
- Lifecycle policies for old images

### Rollback Procedures

**Frontend**:
```bash
# Restore previous version from S3 versioning
aws s3api list-object-versions \
  --bucket vpbank-voice-agent-frontend-590183822512 \
  --prefix index.html

aws s3api copy-object \
  --copy-source "bucket/index.html?versionId=VERSION_ID" \
  --bucket vpbank-voice-agent-frontend-590183822512 \
  --key index.html
```

**Backend**:
```bash
# Rollback to previous task definition
aws ecs update-service \
  --cluster vpbank-voice-agent-cluster \
  --service voice-bot \
  --task-definition voice-bot:PREVIOUS_REVISION
```

---

## Performance

**Latency Targets**:
- CloudFront cache hit: <50ms
- API response: <500ms
- WebRTC connection: <2s
- Voice response: <3s

**Throughput**:
- Concurrent users: 100+
- Requests/second: 1000+
- WebRTC connections: 50+

---

## Contact & Support

**Infrastructure Team**: DevOps  
**Application Team**: Backend/Frontend Developers  
**On-Call**: PagerDuty rotation

**Documentation**:
- Architecture: This file
- Deployment: `DEPLOYMENT_SUCCESS_20251109.md`
- Troubleshooting: `DEBUG_REPORT_20251109.md`

---

**Last Deployment**: 2025-11-09 16:27 UTC  
**Status**: ✅ Production Ready
