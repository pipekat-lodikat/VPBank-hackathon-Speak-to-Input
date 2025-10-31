# 🏗️ MICROSERVICES ARCHITECTURE - VPBANK VOICE BOT

**Updated:** October 30, 2025  
**Architecture:** Microservices với Task Queue

---

## 🎯 CURRENT vs PROPOSED

### ❌ Current (Monolith):
```
Voice Bot + Workflow Worker + Browser Agent
  → Chạy trong 1 process
  → Browser block voice bot
  → Không scale riêng được
```

### ✅ Proposed (Microservices):
```
Service 1: Voice Bot
  → Nhận voice, chat, push queue
  → Lightweight, fast response
  
Service 2: Browser Worker (x N instances)
  → Poll queue
  → Fill forms
  → Scalable, parallel processing
```

---

## 📁 PROJECT STRUCTURE (Microservices)

```
VPBankHackathon/
├── services/
│   ├── voice-bot/                # Service 1
│   │   ├── main.py              # WebRTC server
│   │   ├── bot.py               # Voice pipeline
│   │   ├── task_queue_client.py # Push to queue
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── browser-worker/           # Service 2
│       ├── main.py               # Worker loop
│       ├── supervisor.py         # LangGraph
│       ├── browser_agent.py      # Browser automation
│       ├── task_queue_client.py  # Poll from queue
│       ├── Dockerfile
│       └── requirements.txt
│
├── shared/
│   ├── task_queue.py             # Shared queue client
│   └── models.py                 # Task/Response models
│
├── docker-compose.yml             # Local development
├── k8s/                          # Kubernetes manifests
└── README.md
```

---

## 🔧 IMPLEMENTATION OPTIONS

### Option 1: Redis Queue (RECOMMENDED)
**Pros:**
- Fast, in-memory
- Pub/Sub support
- Easy to scale
- Built-in persistence

**Cons:**
- Needs Redis server

**Stack:**
```
Voice Bot → Redis List (LPUSH)
Browser Worker → Redis List (BRPOP - blocking pop)
```

### Option 2: PostgreSQL/MySQL Queue
**Pros:**
- No additional infrastructure
- Persistent by default
- ACID guarantees

**Cons:**
- Slower than Redis
- Need polling mechanism

### Option 3: RabbitMQ/AWS SQS
**Pros:**
- Purpose-built for messaging
- Advanced routing
- Dead letter queues

**Cons:**
- More complex setup
- AWS SQS has costs

---

## 🚀 IMPLEMENTATION PLAN

### Step 1: Tách Voice Bot

Tạo `services/voice-bot/`:
```python
# services/voice-bot/main.py
from task_queue_client import TaskQueueClient

queue_client = TaskQueueClient(redis_url="redis://localhost:6379")

async def handle_transcript(message):
    if "BẮT ĐẦU XỬ LÝ" in message:
        # Push to Redis instead of in-process queue
        await queue_client.push_task({
            "task_id": uuid.uuid4(),
            "conversation": conversation_history,
            "type": "loan"  # or crm, hr, etc.
        })
```

### Step 2: Tạo Browser Worker

Tạo `services/browser-worker/`:
```python
# services/browser-worker/main.py
from task_queue_client import TaskQueueClient
from supervisor import build_supervisor_workflow

queue_client = TaskQueueClient(redis_url="redis://localhost:6379")

async def main():
    while True:
        # Blocking pop from Redis
        task = await queue_client.pop_task()
        
        # Process with LangGraph
        result = await process_task(task)
        
        # Update status
        await queue_client.update_task_status(task["id"], "completed", result)
```

### Step 3: Docker Compose

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  voice-bot:
    build: ./services/voice-bot
    ports:
      - "7860:7860"
    environment:
      - REDIS_URL=redis://redis:6379
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
    depends_on:
      - redis
  
  browser-worker:
    build: ./services/browser-worker
    environment:
      - REDIS_URL=redis://redis:6379
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
    deploy:
      replicas: 3  # Scale to 3 workers!
    depends_on:
      - redis
```

### Step 4: Run với Docker Compose

```bash
docker-compose up --scale browser-worker=5
```

→ 1 Voice Bot + 5 Browser Workers chạy song song!

---

## 📊 BENEFITS

### Performance:
- Voice Bot: <100ms response (không chờ browser)
- Browser Workers: Parallel processing (5 tasks cùng lúc)

### Scalability:
- Scale voice bot: 1-2 instances (light)
- Scale browser workers: 5-50 instances (heavy)

### Reliability:
- Voice bot crash → Browser workers vẫn chạy
- Browser crash → Chỉ 1 worker die, 4 còn lại OK

---

Bạn muốn tôi implement architecture này không? 🚀

