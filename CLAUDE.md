# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VPBank Voice Agent is a production-ready voice-powered banking form automation system using a microservices architecture. The system enables users to fill Vietnamese banking forms through natural speech using WebRTC, speech recognition, LLM conversation, and AI-powered browser automation.

## Architecture

The system follows a **microservices architecture** with three independent services:

1. **Voice Bot Service** (Port 7860)
   - Entry point: `main_voice.py`
   - Handles WebRTC audio streaming (bidirectional)
   - PhoWhisper STT for speech-to-text (Vietnamese language)
   - AWS Bedrock Claude Sonnet 4 for conversational AI
   - ElevenLabs for Vietnamese TTS
   - Sends HTTP POST requests to Browser Agent Service
   - WebSocket for real-time transcript streaming to frontend
   - Auth via AWS Cognito
   - Session management via AWS DynamoDB

2. **Browser Agent Service** (Port 7863)
   - Entry point: `main_browser_service.py`
   - HTTP REST API server (aiohttp)
   - Executes AI-powered browser automation using `browser-use` library
   - Uses Playwright + OpenAI GPT-4 for form filling
   - Returns results to Voice Bot via HTTP response

3. **Frontend** (Port 5173)
   - React 19 + Vite + TypeScript
   - Pipecat React UI Kit for WebRTC voice interface
   - TailwindCSS for styling
   - Dynamic API URL detection (supports remote access)

**Critical Service Dependencies:**
- Browser Agent must start FIRST (port 7863)
- Voice Bot starts second and connects to Browser Agent (port 7860)
- Frontend connects to Voice Bot via WebRTC and WebSocket

**Inter-Service Communication:**
- Voice Bot → Browser Agent: HTTP POST to `/api/execute`
- Frontend → Voice Bot: WebRTC for audio, WebSocket for transcripts
- All services communicate via HTTP REST APIs

## Environment Setup

### Python Environment (Backend)

```bash
# Create and activate virtual environment
python3.11 -m venv venv  # MUST use Python 3.11, not 3.12 or 3.13
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium  # Linux only
```

**Important:** This project requires Python 3.11.x specifically due to dependency constraints.

### Frontend Environment

```bash
cd frontend
npm install
```

### Required Environment Variables

Create `.env` file in project root (NOT in frontend/). Use `.env.example` as a template:

```bash
cp .env.example .env
```

Required variables:
- `AWS_ACCESS_KEY_ID` - AWS credentials for Bedrock only
- `AWS_SECRET_ACCESS_KEY` - AWS secret key for Bedrock
- `AWS_REGION` - Default: us-east-1
- `BEDROCK_MODEL_ID` - Claude model: us.anthropic.claude-sonnet-4-20250514-v1:0
- `OPENAI_API_KEY` - For PhoWhisper STT and GPT-4 browser automation
- `ELEVENLABS_API_KEY` - For Vietnamese TTS
- `ELEVENLABS_VOICE_ID` - Voice model ID
- `BROWSER_SERVICE_URL` - Default: http://localhost:7863
- `COGNITO_USER_POOL_ID` - AWS Cognito user pool
- `COGNITO_CLIENT_ID` - AWS Cognito app client
- `DYNAMODB_TABLE_NAME` - Session storage table
- Auth credentials: `AUTH_AWS_ACCESS_KEY_ID`, `AUTH_AWS_SECRET_ACCESS_KEY`
- DynamoDB credentials: `DYNAMODB_AWS_ACCESS_KEY_ID`, `DYNAMODB_AWS_SECRET_ACCESS_KEY`

## Running the Application

### Development Mode (Recommended)

**Terminal 1 - Browser Agent Service:**
```bash
python main_browser_service.py
```
Wait for: `🌐 Starting Browser Agent Service...` on port 7863

**Terminal 2 - Voice Bot Service:**
```bash
python main_voice.py
```
Wait for: `🎤 Starting Voice Bot Service...` on port 7860

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev -- --host 0.0.0.0
```
Access at: `http://localhost:5173` or `http://<server-ip>:5173`

**Service Health Checks:**
- Browser Agent: `http://localhost:7863/api/health`
- Voice Bot: Open `http://localhost:7860` in browser
- Frontend: `http://localhost:5173`

### Production Deployment

For remote access (AWS EC2), ensure:
1. Frontend uses dynamic API URL via `src/config.ts` (auto-detects hostname)
2. AWS Security Group allows inbound traffic on ports:
   - TCP: 5173 (Frontend), 7860 (Voice Bot), 7863 (Browser Agent)
   - UDP: 3478 (STUN), 49152-65535 (WebRTC media, or restricted range)
3. Services run with `--host 0.0.0.0` to listen on all interfaces

### Docker Compose

```bash
docker-compose up --build
docker-compose logs -f
docker-compose down
```

## Key Technical Details

### WebRTC Audio Pipeline (Voice Bot)

The voice bot uses Pipecat AI framework with this pipeline:
- SmallWebRTC Transport for bidirectional audio
- PhoWhisper STT (Vietnamese language)
- AWS Bedrock Claude Sonnet 4 LLM
- ElevenLabs TTS (Vietnamese voice)
- Silero VAD for voice activity detection
- Real-time transcript streaming via WebSocket

### Browser Automation (Browser Agent)

Uses `browser-use` library (v0.9.5) which wraps:
- Playwright for browser control
- OpenAI GPT-4 for AI-powered form filling
- Custom speed optimization prompts
- Session management for multi-turn form filling

### Frontend Dynamic Configuration

`frontend/src/config.ts` auto-detects API URL:
```typescript
// If accessing via IP/domain (not localhost), use that hostname
if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
  return `${protocol}//${hostname}:7860`;
}
return 'http://localhost:7860';  // Local development
```

This allows the same build to work locally and on remote servers.

### Authentication & Session Management

- AWS Cognito for user authentication
- AWS DynamoDB for session storage
- Separate AWS credentials for auth/DynamoDB vs. Transcribe/Bedrock
- Sessions include transcript history and metadata

## Code Structure

```
/
├── src/                          # Backend Python source
│   ├── voice_bot.py             # WebRTC/STT/TTS/LLM pipeline
│   ├── browser_agent.py         # Browser automation handler
│   ├── dynamodb_service.py      # Session storage
│   ├── auth_service.py          # Cognito authentication
│   ├── llm_evaluator/           # LangSmith evaluation
│   ├── cost/                    # Cost tracking and analytics
│   ├── monitoring/              # Monitoring and observability
│   ├── prompts/                 # LLM prompt templates
│   ├── security/                # Security utilities
│   └── verification/            # Verification and validation
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── config.ts            # Dynamic API URL configuration
│   │   ├── pages/               # Page components
│   │   ├── components/          # Reusable components
│   │   └── hooks/               # React hooks
│   └── package.json
├── infrastructure/               # Infrastructure as Code
│   └── terraform/               # Terraform configurations (ECS, VPC, ALB)
├── scripts/                      # Deployment and utility scripts
│   ├── deploy-ecs-fargate.sh   # ECS deployment script
│   ├── start-dev.sh            # Start all services
│   └── stop.sh                 # Stop all services
├── docs/                        # Documentation
│   ├── requirements/            # Requirements, proposals, technical docs
│   └── images/                  # Documentation images
├── tests/                       # Test suites
├── vpbank-forms/                # Form templates (5 cases)
├── main_voice.py                # Voice Bot entry point
├── main_browser_service.py      # Browser Agent entry point
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Container orchestration
├── Dockerfile                   # Container image definition
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore patterns
├── README.md                    # Project documentation
└── CLAUDE.md                    # Claude Code instructions
```

## Common Development Commands

### Backend Development

```bash
# Start individual services
python main_browser_service.py  # Start Browser Agent first
python main_voice.py             # Then start Voice Bot

# Enable debug logging
export LOG_LEVEL=DEBUG

# Reinstall dependencies after changes
pip install -r requirements.txt

# Reinstall Playwright browsers if needed
playwright install chromium
```

### Frontend Development

```bash
cd frontend

# Development server (local only)
npm run dev

# Development server (allow remote connections)
npm run dev -- --host 0.0.0.0

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Testing

```bash
# Test Browser Agent endpoint
curl http://localhost:7863/api/health

# Test Voice Bot (requires browser)
open http://localhost:7860

# Check running services
lsof -ti:7860,7863,5173
netstat -tlnp | grep -E ':(5173|7860|7863)'
```

## Debugging Common Issues

### "Module not found" or "Import error"
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (must be 3.11.x)

### "Playwright browser not found"
```bash
playwright install chromium
playwright install-deps chromium  # Linux only
```

### "Network error" or "404: Not Found API" in frontend
- Check Voice Bot service is running on port 7860
- Verify frontend's API URL detection: Check browser Console
- Restart Voice Bot service if it was started before Browser Agent
- For remote access, ensure AWS Security Group allows TCP 7860

### "WebRTC connection timeout" or "ICE connection failed"
- For remote access, AWS Security Group must allow UDP ports:
  - 3478 (STUN/TURN)
  - 49152-65535 (or restricted range like 49152-49252)
- Check frontend WebSocket connection in browser DevTools

### Service won't start or "Address already in use"
```bash
# Find and kill processes on ports
lsof -ti:7860 | xargs kill -9
lsof -ti:7863 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### Browser automation fails
- Verify `OPENAI_API_KEY` is set and valid
- Check Playwright browsers installed: `playwright install chromium`
- Review Browser Agent logs for automation errors
- Ensure form URLs are accessible

## Important Notes

1. **Service Startup Order Matters:** Always start Browser Agent (7863) before Voice Bot (7860)

2. **Multiple AWS Credentials:** The system uses separate AWS credentials for:
   - Bedrock only (main credentials, NOT for STT)
   - Cognito authentication (AUTH_* credentials)
   - DynamoDB sessions (DYNAMODB_* credentials)

3. **Frontend API URL:** The frontend auto-detects the API URL based on `window.location.hostname`. No hardcoded URLs needed.

4. **WebRTC Ports:** For production/remote access, UDP ports must be open for WebRTC media transmission.

5. **Python Version:** Must use Python 3.11.x due to dependency compatibility (Pipecat AI + browser-use).

6. **Environment File:** The `.env` file must exist in project root, not in `frontend/`. Copy from `.env.example` if needed.

## Technology Stack

**Backend:**
- Python 3.11
- Pipecat AI 0.0.91 (WebRTC/Voice framework)
- aiohttp 3.12.15 (HTTP server)
- PhoWhisper STT (speech-to-text for Vietnamese)
- AWS Bedrock Claude Sonnet 4 (LLM)
- ElevenLabs (TTS)
- browser-use 0.9.5 (AI browser automation)
- Playwright 1.55.0 (browser control)
- OpenAI GPT-4 (browser automation planning)
- LangChain + LangGraph (multi-agent) - [Supervisor Pattern](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)

**Frontend:**
- React 19.1.1
- Vite 7.1.2
- TypeScript 5.8.3
- Pipecat React UI Kit
- TailwindCSS 4.1.13

**AWS Services:**
- Bedrock (Claude Sonnet 4 LLM only, NOT for STT)
- Cognito (Authentication)
- DynamoDB (Session Storage)
