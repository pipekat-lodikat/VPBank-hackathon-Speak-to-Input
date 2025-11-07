# Developer Guide

Comprehensive guide for developers working on VPBank Voice Agent codebase.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [Testing](#testing)
- [Debugging](#debugging)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Code Style & Standards](#code-style--standards)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites

**Required Software:**
- Python 3.11.x (NOT 3.12 or 3.13 - dependency constraints)
- Node.js 18+ and npm
- Git
- AWS CLI (configured with credentials)
- Docker & Docker Compose (optional)
- VS Code or PyCharm (recommended)

**System Requirements:**
- Ubuntu 20.04+ or macOS 12+ or Windows 11 with WSL2
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

### Initial Setup

**1. Clone Repository:**
```bash
git clone https://github.com/yourusername/vpbank-voice-agent.git
cd vpbank-voice-agent
```

**2. Python Environment:**
```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Verify Python version
python --version  # Must be 3.11.x

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium  # Linux only
```

**3. Frontend Environment:**
```bash
cd frontend
npm install
cd ..
```

**4. Environment Variables:**
```bash
# Copy template
cp env .env

# Edit .env with your values
nano .env  # or vim .env
```

**Required Environment Variables:**
```bash
# AWS Credentials (Transcribe/Bedrock)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# AWS Bedrock Model
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# OpenAI (Browser Automation)
OPENAI_API_KEY=sk-...

# ElevenLabs (TTS)
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=your_voice_id

# AWS Cognito (Auth)
COGNITO_USER_POOL_ID=us-east-1_...
COGNITO_CLIENT_ID=...
AUTH_AWS_ACCESS_KEY_ID=your_auth_key
AUTH_AWS_SECRET_ACCESS_KEY=your_auth_secret

# DynamoDB (Sessions)
DYNAMODB_TABLE_NAME=vpbank_sessions
DYNAMODB_AWS_ACCESS_KEY_ID=your_db_key
DYNAMODB_AWS_SECRET_ACCESS_KEY=your_db_secret

# Browser Service
BROWSER_SERVICE_URL=http://localhost:7863
BROWSER_HEADLESS=false

# Form URLs
LOAN_FORM_URL=https://vpbank-shared-form-fastdeploy.vercel.app/
CRM_FORM_URL=https://case2-ten.vercel.app/
HR_FORM_URL=https://case3-seven.vercel.app/
COMPLIANCE_FORM_URL=https://case4-beta.vercel.app/
OPERATIONS_FORM_URL=https://case5-chi.vercel.app/
```

**5. Verify Installation:**
```bash
# Test Python imports
python -c "import pipecat; import browser_use; print('OK')"

# Test frontend
cd frontend && npm run build && cd ..

# Run health checks
python main_browser_service.py &
sleep 5
curl http://localhost:7863/api/health
kill %1
```

---

## Project Structure

```
vpbank-voice-agent/
│
├── src/                           # Backend Python source code
│   ├── voice_bot.py              # Voice Bot pipeline (STT/TTS/LLM)
│   ├── browser_agent.py          # Browser automation handler
│   ├── dynamodb_service.py       # DynamoDB session storage
│   ├── auth_service.py           # AWS Cognito authentication
│   ├── dynamic_vad.py            # Dynamic Voice Activity Detection
│   │
│   ├── prompts/                  # LLM prompt templates
│   │   ├── system_prompt.py     # Main system prompt
│   │   └── browser_prompts.py   # Browser automation prompts
│   │
│   ├── security/                 # Security utilities
│   │   ├── pii_masking.py       # PII data masking
│   │   └── rate_limiter.py      # Rate limiting
│   │
│   ├── monitoring/               # Observability
│   │   └── metrics.py           # Prometheus metrics
│   │
│   ├── cost/                     # Cost optimization
│   │   └── usage_tracker.py     # API usage tracking
│   │
│   └── llm_evaluator/            # LangSmith evaluation
│       └── evaluator.py         # LLM response evaluation
│
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── config.ts            # Dynamic API URL config
│   │   ├── pages/               # Page components
│   │   │   ├── ChatPage.tsx    # Main voice chat interface
│   │   │   └── TranscriptsPage.tsx  # Session history
│   │   ├── components/          # Reusable components
│   │   │   ├── auth/           # Auth components
│   │   │   └── voice/          # Voice UI components
│   │   └── hooks/              # React hooks
│   │       └── useTranscripts.ts  # Session management hook
│   ├── package.json
│   └── vite.config.ts
│
├── vpbank-forms/                 # Form templates (5 cases)
│   ├── case1-loan.html
│   ├── case2-crm.html
│   ├── case3-hr.html
│   ├── case4-compliance.html
│   └── case5-operations.html
│
├── main_voice.py                 # Voice Bot entry point
├── main_browser_service.py       # Browser Agent entry point
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Container orchestration
├── Dockerfile                    # Container image
├── .env                          # Environment variables (git-ignored)
├── env                           # Environment template
├── README.md                     # Project overview
├── CLAUDE.md                     # AI assistant instructions
├── API_DOCUMENTATION.md          # API reference
├── USER_GUIDE.md                 # End-user documentation
├── DEVELOPER_GUIDE.md            # This file
└── ARCHITECTURE.md               # System architecture

```

### Key Files Explained

**Backend Entry Points:**
- `main_browser_service.py` - HTTP server for browser automation
- `main_voice.py` - WebRTC/Voice Bot server

**Core Services:**
- `src/voice_bot.py` - Pipecat AI pipeline (STT → LLM → TTS)
- `src/browser_agent.py` - browser-use wrapper for form automation
- `src/dynamodb_service.py` - Session CRUD operations
- `src/auth_service.py` - Cognito authentication wrapper

**Frontend Key Files:**
- `frontend/src/pages/ChatPage.tsx` - Main voice interface
- `frontend/src/config.ts` - Dynamic API URL detection
- `frontend/src/hooks/useTranscripts.ts` - Session management

---

## Architecture Overview

### System Components

```
┌─────────────────┐
│    Frontend     │ (React + Vite)
│   Port: 5173    │
└────────┬────────┘
         │ WebRTC Audio (bidirectional)
         │ WebSocket (transcripts)
         ↓
┌─────────────────┐
│   Voice Bot     │ (Python + Pipecat AI)
│   Port: 7860    │
│                 │
│ ┌─────────────┐ │
│ │ STT Service │ │ → AWS Transcribe (Vietnamese)
│ └─────────────┘ │
│ ┌─────────────┐ │
│ │ LLM Service │ │ → AWS Bedrock Claude Sonnet 4
│ └─────────────┘ │
│ ┌─────────────┐ │
│ │ TTS Service │ │ → ElevenLabs (Vietnamese)
│ └─────────────┘ │
└────────┬────────┘
         │ HTTP POST /api/execute
         ↓
┌─────────────────┐
│ Browser Agent   │ (Python + browser-use)
│   Port: 7863    │
│                 │
│ ┌─────────────┐ │
│ │  Playwright │ │ → Chromium browser
│ └─────────────┘ │
│ ┌─────────────┐ │
│ │  OpenAI GPT │ │ → AI form filling
│ └─────────────┘ │
└─────────────────┘
```

### Data Flow

**1. Voice Input Flow:**
```
User speaks → Microphone → WebRTC → Voice Bot
→ AWS Transcribe → Vietnamese text → LLM (Claude)
→ Intent detection → HTTP POST → Browser Agent
→ Form automation → HTTP Response → Voice Bot
→ ElevenLabs TTS → Audio response → WebRTC → User hears
```

**2. Session Management:**
```
WebRTC connection → Session created
→ Transcript saved to DynamoDB
→ WebSocket broadcasts updates to frontend
→ Session persists until disconnect
```

### Technology Stack

**Backend:**
- **Framework:** aiohttp 3.12.15
- **Voice Processing:** Pipecat AI 0.0.91
- **STT:** AWS Transcribe (Vietnamese)
- **LLM:** AWS Bedrock Claude Sonnet 4
- **TTS:** ElevenLabs (Vietnamese)
- **Browser Automation:** browser-use 0.9.5 + Playwright 1.55.0
- **AI Agent:** OpenAI GPT-4
- **Auth:** AWS Cognito
- **Database:** AWS DynamoDB
- **Monitoring:** Prometheus + Loguru

**Frontend:**
- **Framework:** React 19.1.1
- **Build Tool:** Vite 7.1.2
- **Language:** TypeScript 5.8.3
- **UI Library:** Pipecat React UI Kit
- **Styling:** TailwindCSS 4.1.13
- **WebRTC:** SmallWebRTC Transport

---

## Backend Development

### Running Services Locally

**Start Browser Agent (Terminal 1):**
```bash
# MUST start first!
python main_browser_service.py
```

Expected output:
```
🌐 Starting Browser Agent Service...
📡 Service runs on port 7863
🔗 Endpoints:
   POST   /api/execute - Execute workflow
   GET    /api/health - Health check
   GET    /api/live  - Current browser live URL
```

**Start Voice Bot (Terminal 2):**
```bash
# Start after Browser Agent is running
python main_voice.py
```

Expected output:
```
🚀 Starting VPBank Multi-Agent Bot Server...
🎤 Voice Bot Service ready
📡 WebRTC endpoint: POST /offer
📡 WebSocket endpoint: GET /ws
```

**Verify Services:**
```bash
# Browser Agent health
curl http://localhost:7863/api/health

# Voice Bot metrics
curl http://localhost:7860/metrics
```

### Adding New Form Types

**1. Define Form URL:**
```python
# main_browser_service.py or src/browser_agent.py
NEW_FORM_URL = os.getenv("NEW_FORM_URL", "https://your-form-url.com")
```

**2. Update Browser Agent:**
```python
# src/browser_agent.py - execute_freeform method
comprehensive_task = (
    "STEP 1 - NAVIGATE:\n"
    "Decide the most relevant form among these URLs:\n"
    f"- new_type: {NEW_FORM_URL}\n"
    # ... existing forms
)
```

**3. Update System Prompt:**
```python
# src/voice_bot.py - system_prompt variable
system_prompt = """
...
6️ **NEW FORM TYPE** (Use Case 6)
- ONE-SHOT or INCREMENTAL (similar to above)
...
"""
```

**4. Test New Form:**
```bash
# Test voice command
curl -X POST http://localhost:7863/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Fill new form type with data...",
    "session_id": "test_123"
  }'
```

### Modifying LLM Behavior

**System Prompt Location:** `src/voice_bot.py:405`

**Example Modifications:**

**Add New Intent Detection:**
```python
# src/voice_bot.py - handle_transcript_update function
if message.role == "user":
    msg_lower = message.content.lower()

    # Add new intent keywords
    new_intent_keywords = [
        "new intent", "trigger word", "command"
    ]

    if any(keyword in msg_lower for keyword in new_intent_keywords):
        should_push_task = True
        logger.info(f"🚀 Detected new intent")
```

**Change Response Style:**
```python
# Modify system_prompt in src/voice_bot.py
system_prompt = """
...
QUY TẮC PHONG CÁCH TRẢ LỜI:
- [Add new style rules here]
- [Example: Always include emoji]
- [Example: Respond in English]
...
"""
```

### Adding Monitoring Metrics

**1. Define Metric:**
```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram

# Add new metric
form_submissions_total = Counter(
    'form_submissions_total',
    'Total form submissions',
    ['form_type', 'status']
)
```

**2. Track Metric:**
```python
# src/browser_agent.py
from src.monitoring.metrics import form_submissions_total

# In execute_freeform method
try:
    result = await agent.run()
    form_submissions_total.labels(
        form_type='loan',
        status='success'
    ).inc()
except Exception as e:
    form_submissions_total.labels(
        form_type='loan',
        status='failure'
    ).inc()
```

**3. Verify Metric:**
```bash
curl http://localhost:7860/metrics | grep form_submissions
```

### Debugging Backend Issues

**Enable Debug Logging:**
```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in code (src/voice_bot.py)
logger.remove()
logger.add(sys.stderr, level="DEBUG")
```

**View Logs:**
```bash
# Follow logs in real-time
tail -f logs/voice_bot.log

# Search for errors
grep -i "error" logs/*.log

# Filter by session ID
grep "session_123" logs/*.log
```

**Common Debug Patterns:**
```python
# src/voice_bot.py or src/browser_agent.py

# Add debug breakpoint
import pdb; pdb.set_trace()

# Log variable state
logger.debug(f"Variable state: {variable_name}")

# Log function entry/exit
logger.info(f"→ Entering function_name with args: {args}")
logger.info(f"← Exiting function_name with result: {result}")

# Log exceptions with traceback
try:
    risky_operation()
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
```

---

## Frontend Development

### Running Frontend Locally

```bash
cd frontend

# Development server (local only)
npm run dev

# Development server (remote access)
npm run dev -- --host 0.0.0.0

# Build for production
npm run build

# Preview production build
npm run preview
```

### Project Structure

```
frontend/
├── src/
│   ├── config.ts              # API URL configuration
│   ├── pages/
│   │   ├── ChatPage.tsx       # Main voice interface
│   │   └── TranscriptsPage.tsx  # Session history
│   ├── components/
│   │   ├── auth/
│   │   │   ├── AuthLogin.tsx  # Login form
│   │   │   └── AuthRegister.tsx  # Registration form
│   │   └── voice/
│   │       └── VoiceChat.tsx  # Voice UI component
│   ├── hooks/
│   │   └── useTranscripts.ts  # Session management
│   └── App.tsx                # Root component
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

### Key Components

**1. ChatPage (`src/pages/ChatPage.tsx`)**

Main voice chat interface using Pipecat React UI Kit.

```tsx
import { VoiceClientProvider, useVoiceClient } from '@pipecat-ai/client-react';

export function ChatPage() {
  const voiceClient = useVoiceClient({
    apiUrl: getApiUrl(),  // Dynamic URL from config.ts
    enableWebRTC: true,
    onConnected: () => console.log('Connected'),
    onDisconnected: () => console.log('Disconnected'),
  });

  return (
    <VoiceClientProvider value={voiceClient}>
      {/* Voice UI components */}
    </VoiceClientProvider>
  );
}
```

**2. Dynamic API URL (`src/config.ts`)**

Auto-detects hostname for local/remote access:

```typescript
export function getApiUrl(): string {
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;

  // If accessing via IP/domain (not localhost), use that hostname
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `${protocol}//${hostname}:7860`;
  }

  // Local development
  return 'http://localhost:7860';
}
```

**3. Session Management (`src/hooks/useTranscripts.ts`)**

Fetches and manages conversation sessions:

```typescript
export function useTranscripts() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSessions() {
      const response = await fetch(`${getApiUrl()}/api/sessions`);
      const data = await response.json();
      setSessions(data.sessions);
    }
    fetchSessions();
  }, []);

  return { sessions, loading };
}
```

### Adding New Features

**Add New Page:**

```bash
# Create page file
touch frontend/src/pages/NewPage.tsx
```

```tsx
// frontend/src/pages/NewPage.tsx
import { useState } from 'react';

export function NewPage() {
  const [data, setData] = useState(null);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold">New Page</h1>
      {/* Page content */}
    </div>
  );
}
```

**Register Route:**

```tsx
// frontend/src/App.tsx
import { NewPage } from './pages/NewPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/new" element={<NewPage />} />
        {/* Existing routes */}
      </Routes>
    </Router>
  );
}
```

**Add New Component:**

```bash
# Create component file
mkdir -p frontend/src/components/feature
touch frontend/src/components/feature/Feature.tsx
```

```tsx
// frontend/src/components/feature/Feature.tsx
import { FC } from 'react';

interface FeatureProps {
  title: string;
  description: string;
}

export const Feature: FC<FeatureProps> = ({ title, description }) => {
  return (
    <div className="p-4 border rounded">
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="text-gray-600">{description}</p>
    </div>
  );
};
```

### Styling with TailwindCSS

**Common Patterns:**

```tsx
// Card component
<div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
  {/* Content */}
</div>

// Button
<button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
  Click Me
</button>

// Form input
<input
  className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
  type="text"
  placeholder="Enter text"
/>

// Grid layout
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => <ItemCard key={item.id} {...item} />)}
</div>
```

**Responsive Design:**

```tsx
// Mobile-first approach
<div className="
  p-4           /* mobile: padding 1rem */
  md:p-6        /* tablet: padding 1.5rem */
  lg:p-8        /* desktop: padding 2rem */

  text-sm       /* mobile: small text */
  md:text-base  /* tablet: base text */
  lg:text-lg    /* desktop: large text */
">
  Responsive content
</div>
```

### Debugging Frontend Issues

**Browser DevTools:**

```javascript
// Console logging
console.log('State:', state);
console.table(arrayData);
console.error('Error:', error);

// Network monitoring
// Open DevTools → Network tab
// Filter: XHR/Fetch to see API calls

// React DevTools
// Install React DevTools extension
// Inspect component props and state
```

**Common Issues:**

**CORS Errors:**
```javascript
// Issue: "No 'Access-Control-Allow-Origin' header"
// Solution: Verify backend CORS middleware is enabled
// Check: src/voice_bot.py - cors_middleware function
```

**WebRTC Connection Fails:**
```javascript
// Issue: "Failed to connect to WebRTC"
// Debug:
console.log('ICE Connection State:', pc.iceConnectionState);
console.log('Signaling State:', pc.signalingState);

// Check:
// 1. Voice Bot service is running (port 7860)
// 2. Microphone permissions granted
// 3. No firewall blocking UDP ports
```

**WebSocket Disconnects:**
```javascript
// Issue: WebSocket closes unexpectedly
// Debug:
ws.onerror = (error) => console.error('WS Error:', error);
ws.onclose = (event) => console.log('WS Closed:', event.code, event.reason);

// Check:
// 1. Network stability
// 2. Session timeout settings
// 3. Server logs for errors
```

---

## Testing

### Backend Testing

**Unit Tests:**

```python
# tests/test_browser_agent.py
import pytest
from src.browser_agent import BrowserAgentHandler

@pytest.mark.asyncio
async def test_fill_form():
    agent = BrowserAgentHandler()
    result = await agent.fill_form(
        form_url="https://test-form.com",
        form_data={"name": "Test User"},
        form_type="loan"
    )
    assert result["success"] is True

# Run tests
pytest tests/
```

**Integration Tests:**

```python
# tests/integration/test_voice_bot.py
import aiohttp
import pytest

@pytest.mark.asyncio
async def test_webrtc_offer():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:7860/offer',
            json={"sdp": "...", "type": "offer"}
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "sdp" in data
```

**Load Testing:**

```bash
# Install locust
pip install locust

# Create load test (locustfile.py)
from locust import HttpUser, task

class VoiceBotUser(HttpUser):
    @task
    def health_check(self):
        self.client.get("/api/health")

# Run load test
locust -f locustfile.py --host=http://localhost:7863
```

### Frontend Testing

**Unit Tests (Jest + React Testing Library):**

```bash
# Install dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest
```

```tsx
// tests/ChatPage.test.tsx
import { render, screen } from '@testing-library/react';
import { ChatPage } from '../src/pages/ChatPage';

test('renders chat page', () => {
  render(<ChatPage />);
  expect(screen.getByText(/Connect/i)).toBeInTheDocument();
});

// Run tests
npm test
```

**E2E Tests (Playwright):**

```bash
# Install Playwright
npm install --save-dev @playwright/test

# Create test
# tests/e2e/voice-chat.spec.ts
import { test, expect } from '@playwright/test';

test('voice chat workflow', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Grant microphone permission
  await page.context().grantPermissions(['microphone']);

  // Click connect button
  await page.click('button:has-text("Connect")');

  // Wait for connection
  await expect(page.locator('.status')).toHaveText('Connected');
});

# Run E2E tests
npx playwright test
```

---

## Debugging

### Backend Debugging

**Python Debugger (pdb):**

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Commands:
# n - next line
# s - step into function
# c - continue execution
# p variable_name - print variable
# q - quit debugger
```

**VS Code Debugging:**

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Voice Bot",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/main_voice.py",
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Browser Agent",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/main_browser_service.py",
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

**Loguru Advanced Usage:**

```python
# src/voice_bot.py
from loguru import logger

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    "logs/voice_bot_{time}.log",
    rotation="100 MB",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# Structured logging
logger.info("Processing request", extra={
    "session_id": session_id,
    "user_id": user_id,
    "action": "form_fill"
})

# Context manager
with logger.contextualize(request_id=uuid4()):
    logger.info("Start processing")
    process_request()
    logger.info("End processing")
```

### Frontend Debugging

**React DevTools:**

- Install React DevTools browser extension
- Inspect component hierarchy
- View props and state
- Profile performance

**Browser Console:**

```javascript
// Debug API calls
fetch(url).then(r => {
  console.log('Response:', r);
  return r.json();
}).then(data => {
  console.log('Data:', data);
});

// Debug WebSocket
ws.addEventListener('message', (event) => {
  console.log('WS Message:', JSON.parse(event.data));
});

// Debug WebRTC
pc.oniceconnectionstatechange = () => {
  console.log('ICE State:', pc.iceConnectionState);
};
```

**Network Debugging:**

1. Open DevTools → Network tab
2. Filter by XHR/Fetch or WS (WebSocket)
3. Click request to see headers, payload, response
4. Check timing and status codes

---

## Deployment

### Production Build

**Backend:**

```bash
# Activate virtual environment
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt

# Set production environment variables
export BROWSER_HEADLESS=true
export LOG_LEVEL=INFO

# Run with systemd or supervisor (recommended)
```

**Frontend:**

```bash
cd frontend

# Build for production
npm run build

# Output: frontend/dist/

# Serve with nginx or another web server
```

### Docker Deployment

**Build Images:**

```bash
# Build all services
docker-compose build

# Build specific service
docker build -t vpbank-voice-bot:latest .
```

**Run Containers:**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Docker Compose Configuration:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  browser-agent:
    build: .
    command: python main_browser_service.py
    ports:
      - "7863:7863"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - BROWSER_HEADLESS=true
    volumes:
      - ./logs:/app/logs

  voice-bot:
    build: .
    command: python main_voice.py
    ports:
      - "7860:7860"
    depends_on:
      - browser-agent
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - BROWSER_SERVICE_URL=http://browser-agent:7863

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - voice-bot
```

### AWS EC2 Deployment

**1. Launch EC2 Instance:**
- Instance type: t3.medium or larger
- Ubuntu 22.04 LTS
- Security group: Allow TCP 5173, 7860, 7863, 22, UDP 49152-65535

**2. Install Dependencies:**

```bash
# SSH into instance
ssh -i keypair.pem ubuntu@<instance-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**3. Deploy Application:**

```bash
# Clone repository
git clone https://github.com/yourusername/vpbank-voice-agent.git
cd vpbank-voice-agent

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium

# Setup environment variables
cp env .env
nano .env  # Edit with production values

# Setup frontend
cd frontend
npm install
npm run build
cd ..

# Start services with systemd
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable browser-agent voice-bot frontend
sudo systemctl start browser-agent voice-bot frontend
```

**4. Configure Nginx (Optional):**

```nginx
# /etc/nginx/sites-available/vpbank
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Voice Bot API
    location /api/ {
        proxy_pass http://localhost:7860;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

---

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          playwright install chromium

      - name: Run tests
        run: pytest tests/
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm install

      - name: Run tests
        run: |
          cd frontend
          npm test

      - name: Build
        run: |
          cd frontend
          npm run build

  deploy:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to EC2
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /home/ubuntu/vpbank-voice-agent
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            cd frontend && npm install && npm run build && cd ..
            sudo systemctl restart browser-agent voice-bot frontend
```

---

## Code Style & Standards

### Python Style Guide

Follow PEP 8 with these additions:

**Imports:**

```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import aiohttp
from loguru import logger

# Local
from src.browser_agent import browser_agent
from src.dynamodb_service import DynamoDBService
```

**Naming Conventions:**

```python
# Variables and functions: snake_case
user_message = "Hello"
def process_message():
    pass

# Classes: PascalCase
class BrowserAgentHandler:
    pass

# Constants: UPPER_CASE
MAX_RETRIES = 3
API_TIMEOUT = 300
```

**Docstrings:**

```python
def execute_workflow(user_message: str, session_id: str) -> dict:
    """
    Execute browser automation workflow.

    Args:
        user_message: Full conversation context
        session_id: Unique session identifier

    Returns:
        dict: Result with 'success', 'result', and optional 'error' keys

    Raises:
        ValueError: If user_message is empty
        TimeoutError: If execution exceeds 5 minutes
    """
    pass
```

**Type Hints:**

```python
from typing import Optional, List, Dict, Any

async def get_sessions(
    limit: int = 50,
    last_key: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Fetch sessions from DynamoDB."""
    pass
```

### TypeScript Style Guide

Follow Airbnb Style Guide with these additions:

**Naming Conventions:**

```typescript
// Variables and functions: camelCase
const userName = 'John';
function processMessage() {}

// Types and Interfaces: PascalCase
interface UserData {
  name: string;
  email: string;
}

// Constants: UPPER_CASE
const MAX_RETRIES = 3;
const API_URL = 'http://localhost:7860';
```

**Type Definitions:**

```typescript
// Always define types
interface Session {
  session_id: string;
  started_at: string;
  messages: Message[];
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// Use types for props
interface ChatPageProps {
  onDisconnect?: () => void;
}

export const ChatPage: FC<ChatPageProps> = ({ onDisconnect }) => {
  // ...
};
```

**Async/Await:**

```typescript
// Preferred over .then()
async function fetchSessions(): Promise<Session[]> {
  try {
    const response = await fetch(`${API_URL}/api/sessions`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    return data.sessions;
  } catch (error) {
    console.error('Failed to fetch sessions:', error);
    return [];
  }
}
```

### Code Formatting

**Python:**

```bash
# Install formatters
pip install black isort

# Format code
black .
isort .

# Check before commit
black --check .
isort --check-only .
```

**TypeScript:**

```bash
# Install ESLint and Prettier
npm install --save-dev eslint prettier

# Format code
npm run lint:fix

# Check before commit
npm run lint
```

### Git Commit Messages

Follow Conventional Commits:

```
feat: Add voice biometric authentication
fix: Resolve WebRTC connection timeout
docs: Update API documentation
refactor: Extract form filling logic
test: Add integration tests for browser agent
chore: Update dependencies
```

---

## Contributing

### Contribution Workflow

**1. Fork Repository**

```bash
# Fork on GitHub, then clone
git clone https://github.com/your-username/vpbank-voice-agent.git
cd vpbank-voice-agent

# Add upstream remote
git remote add upstream https://github.com/original/vpbank-voice-agent.git
```

**2. Create Feature Branch**

```bash
# Fetch latest changes
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/voice-biometric-auth
```

**3. Make Changes**

```bash
# Make changes, test locally
# Run tests: pytest tests/
# Run linters: black . && isort .

# Commit with conventional commits
git add .
git commit -m "feat: Add voice biometric authentication"
```

**4. Push and Create PR**

```bash
# Push to your fork
git push origin feature/voice-biometric-auth

# Create Pull Request on GitHub
# Fill in PR template with:
# - Description of changes
# - Related issue number
# - Testing performed
# - Screenshots (if UI changes)
```

**5. Code Review**

- Address review comments
- Update PR with requested changes
- Respond to reviewer questions

**6. Merge**

- Maintainer merges PR after approval
- Delete feature branch after merge

### Pull Request Checklist

- [ ] Code follows style guide
- [ ] Tests pass (`pytest tests/` and `npm test`)
- [ ] Documentation updated
- [ ] Commit messages follow Conventional Commits
- [ ] No merge conflicts with main
- [ ] Reviewed and approved by maintainer

---

## Troubleshooting

### Common Issues

**Issue: "Module not found" error**

```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

**Issue: Playwright browser not found**

```bash
# Solution: Reinstall browsers
playwright install chromium
playwright install-deps chromium  # Linux only
```

**Issue: Port already in use**

```bash
# Solution: Kill process on port
lsof -ti:7860 | xargs kill -9
lsof -ti:7863 | xargs kill -9
```

**Issue: WebRTC connection fails**

```bash
# Solution: Check firewall rules
sudo ufw allow 7860/tcp
sudo ufw allow 49152:65535/udp

# Or check AWS Security Group inbound rules
```

**Issue: "Cannot connect to Browser Service"**

```bash
# Solution: Start Browser Agent first!
python main_browser_service.py &
sleep 5
python main_voice.py
```

---

## Additional Resources

**Documentation:**
- [Pipecat AI Docs](https://docs.pipecat.ai)
- [browser-use Docs](https://github.com/browser-use/browser-use)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [React 19 Docs](https://react.dev)

**Community:**
- GitHub Discussions
- Slack Channel (internal)
- Stack Overflow (tag: vpbank-voice-agent)

**Support:**
- Email: dev-support@vpbank.com
- Internal Wiki: https://wiki.vpbank.com/voice-agent

---

**Last Updated:** November 7, 2025
**Version:** 1.0.0
**Maintainers:** VPBank Engineering Team
