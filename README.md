# VPBank Multi-Agent Voice Bot - Automatic Form Filling via Voice Input

![License](https://img.shields.io/badge/License-MIT-blue.svg) ![Python](https://img.shields.io/badge/Python-3.11-blue.svg) ![AWS](https://img.shields.io/badge/AWS-Bedrock-orange.svg) ![LangGraph](https://img.shields.io/badge/LangGraph-1.0.1-green.svg) ![Playwright](https://img.shields.io/badge/Playwright-1.55.0-blue.svg) ![Pipecat](https://img.shields.io/badge/Pipecat-0.0.91-purple.svg) ![Status](https://img.shields.io/badge/Status-Production-green.svg)

**Voice bot system that automatically fills banking forms via Vietnamese speech input with Multi-Agent architecture, integrating AWS AI services and browser automation. Supports 5 main use cases: Loan Origination, CRM Update, HR Workflow, Compliance Reporting, and Operations Check.**

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Detailed Architecture](#detailed-architecture)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [References](#references)

---

## Architecture Overview

### Overall Architecture

The VPBank Multi-Agent Voice Bot system is built with a layered architecture, enabling real-time voice input processing and automatic form filling via browser automation.

**Frontend (React + TypeScript)**
- User interface with WebRTC audio streaming
- Real-time transcript display via WebSocket
- Voice input/output controls

**Backend (Python + aiohttp)**
- WebRTC server to receive audio stream
- Voice pipeline: STT → LLM → TTS
- Multi-Agent workflow with LangGraph
- Task queue system for async processing
- Browser automation with Playwright

**AI Services (AWS + OpenAI)**
- **AWS Transcribe**: Vietnamese Speech-to-Text
- **AWS Bedrock Claude**: Large Language Model
- **OpenAI TTS**: Text-to-Speech
- **Browser-Use**: AI-powered browser automation

### Processing Flow

```
User Voice Input
    ↓
WebRTC Audio Stream → AWS Transcribe (STT)
    ↓
Transcription Text → AWS Bedrock Claude (LLM)
    ↓
LLM Response → OpenAI TTS → Audio Output
    ↓
User Confirmation → Task Queue
    ↓
Workflow Worker → LangGraph Supervisor
    ↓
Specialist Agent (5 tools) → Browser Agent
    ↓
Playwright Automation → Form Filled
```

### Architecture Benefits

- **Multi-Agent Pattern**: Supervisor router + 5 specialist agents for each use case
- **Async Processing**: Decouple voice interaction from form filling workflow
- **Scalable**: Task queue enables processing multiple requests concurrently
- **Real-time**: WebRTC + WebSocket for low-latency voice interaction
- **Production Ready**: Integrated error handling, logging, and monitoring

---

## Features

### 5 Supported Use Cases

1. **Loan Origination & KYC**
   - Fill loan application with complete KYC information
   - 13 fields: Customer info, loan amount, term, purpose, income, etc.
   - Automatic validation and data formatting

2. **CRM Update**
   - Update customer information
   - 8 fields: Customer ID, interaction type, date, issue, solution, etc.
   - Track customer interactions

3. **HR Workflow**
   - Process HR requests (leave, training)
   - 8 fields: Employee info, request type, dates, reason, etc.
   - HR workflow automation

4. **Compliance Reporting**
   - Compliance and AML reporting
   - 8 fields: Report type, period, reporter, violations, risk level, etc.
   - Compliance tracking

5. **Operations Check**
   - Transaction verification and reconciliation
   - 11 fields: Transaction ID, date, amount, type, beneficiary, etc.
   - Transaction monitoring

### Core Features

- **Real-time Voice Processing**: WebRTC bidirectional audio streaming
- **Vietnamese STT**: AWS Transcribe with Vietnamese language model
- **Conversational AI**: Claude Sonnet 4 with customized system prompts
- **Natural TTS**: OpenAI TTS with "nova" voice
- **Smart Form Filling**: Browser-use AI agent automatically fills forms
- **Multi-Agent Workflow**: LangGraph supervisor + 5 specialist tools
- **Async Task Queue**: Background processing that doesn't block voice interaction
- **Transcript Streaming**: WebSocket real-time transcript for frontend
- **Error Handling**: Comprehensive error handling and retry logic
- **Session Management**: Track conversations and task status

---

## System Requirements

### Hardware

- **CPU**: 2+ cores (recommended 4 cores)
- **RAM**: 4GB+ (recommended 8GB)
- **Storage**: 10GB+ free space
- **Network**: Internet connection for AWS and OpenAI API

### Software

- **Python**: 3.11.x (REQUIRED - do not use 3.12 or 3.13)
- **Node.js**: 18.x or higher
- **OS**: Windows 10+ (with WSL2), macOS 12+, or Linux (Ubuntu 20.04+)
- **Rust**: To build some Python packages (optional, pre-built wheels available for Python 3.11)

### AWS Services

- **AWS Account** with access permissions:
  - AWS Transcribe (Speech-to-Text)
  - AWS Bedrock (Claude models)
- **AWS Region**: `us-east-1` (recommended) or regions supporting Bedrock
- **IAM User** with policies:
  - `AmazonTranscribeFullAccess`
  - `AmazonBedrockFullAccess`

### OpenAI Services

- **OpenAI API Key** with credits:
  - Text-to-Speech (TTS): ~$15/1M characters
  - Browser-Use Agent: ~$0.01-0.03 per task
- **Estimated Cost**: ~$50-120/month for moderate usage

---

## Quick Start

### Step 1: Clone Repository

```bash
git clone https://github.com/minhnghia2k3/Speak_To_Input.git
cd Speak_To_Input
```

### Step 2: Install WSL2 (Windows Only)

```powershell
# Open PowerShell as Administrator
wsl --install

# Restart computer
# Then open Ubuntu from Start Menu and setup username/password
```

### Step 3: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS/WSL
# or
venv\Scripts\activate  # Windows PowerShell

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium  # Linux/WSL only
```

### Step 4: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 5: Configure Environment Variables

```bash
# Copy template file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use other editor
```

**`.env` file content:**
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# AWS Bedrock Model
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Google Sheets URL (optional, for testing)
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
```

### Step 6: Run Application

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python main.py
```

Backend runs at: `http://localhost:7860`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Step 7: Access Application

1. Open browser: `http://localhost:5173`
2. Allow microphone access
3. Click "Connect" to start
4. Speak Vietnamese to fill forms

---

## Configuration

### AWS IAM Setup

**Option 1: Use AWS Managed Policies (Development)**
- Attach `AmazonTranscribeFullAccess`
- Attach `AmazonBedrockFullAccess`

**Option 2: Custom Policy (Production - Least Privilege)**

Create IAM policy with the following JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TranscribeAccess",
      "Effect": "Allow",
      "Action": [
        "transcribe:StartStreamTranscription",
        "transcribe:StartStreamTranscriptionWebSocket"
      ],
      "Resource": "*"
    },
    {
      "Sid": "BedrockAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-sonnet-4-20250514-v1:0",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude*"
      ]
    }
  ]
}
```

### AWS Bedrock Model Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Select region `us-east-1`
3. Go to **Model access** → **Manage model access**
4. Enable:
   - **Anthropic Claude 3.5 Sonnet**
   - **Anthropic Claude Sonnet 4**

### OpenAI API Key Setup

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create API key from [API Keys](https://platform.openai.com/api-keys)
3. Add credits (minimum $5, recommended $20-50 for testing)
4. Set usage limits to avoid exceeding costs

### Environment Variables Details

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS IAM Access Key | `AKIAXXXXXXXXXXXXXXXX` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM Secret Key | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `AWS_REGION` | AWS Region | `us-east-1` |
| `BEDROCK_MODEL_ID` | Claude Model ID | `us.anthropic.claude-sonnet-4-20250514-v1:0` |
| `OPENAI_API_KEY` | OpenAI API Key | `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `GOOGLE_SHEETS_URL` | Google Sheets URL (optional) | `https://docs.google.com/spreadsheets/d/...` |

---

## Usage

### Voice Commands

The system supports 5 use case types with trigger keywords:

#### 1. Loan Origination
```
"I want to borrow 500 million VND"
"Create loan application for customer Nguyen Van An"
"Fill KYC form"
```

#### 2. CRM Update
```
"Update customer information"
"CRM: update interaction with customer ID 12345"
```

#### 3. HR Workflow
```
"Request leave from day 1 to day 5"
"Register for training course"
```

#### 4. Compliance Reporting
```
"Compliance report for October"
"AML report for customer ID 67890"
```

#### 5. Operations Check
```
"Check transaction number 123456"
"Reconcile today's transactions"
```

### Interaction Flow

1. **User speaks request** → Bot asks for missing information
2. **Bot collects complete data** → Bot reads back for confirmation
3. **User confirms "Correct"** → Bot triggers: "I will START PROCESSING NOW"
4. **Task pushed to queue** → Background worker processes
5. **LangGraph supervisor** → Selects specialist agent
6. **Browser automation** → Automatically fills form
7. **Completed** → User receives result notification

### Complete Example

```
User: "I want to borrow 500 million"
Bot: "Sure, let me help you. Please provide:
      - Full name?
      - ID number?"
      
User: "Name Nguyen Van An, ID 001234567890"
Bot: "Let me confirm:
      - Full name: Nguyen Van An
      - ID: 001234567890
      - Loan amount: 500 million VND
      Is the above information CORRECT?"
      
User: "Correct"
Bot: "I will START PROCESSING NOW."
      [Form is automatically filled in background]
```

---

## Detailed Architecture

### Directory Structure

```
speak-to-input/
├── main.py                      # Entry point
├── requirements.txt              # Python dependencies
├── package.json                 # Node.js dependencies (Playwright)
├── README.md                    # This file
├── TEST_CASES.md                # Test cases for 5 use cases
├── src/                         # Backend source code
│   ├── __init__.py
│   ├── bot_multi_agent.py       # WebRTC server + Voice pipeline
│   ├── task_queue.py            # Async task queue
│   ├── workflow_worker.py       # Background worker
│   ├── browser_agent.py         # Browser automation
│   └── multi_agent/             # Multi-agent system
│       ├── __init__.py
│       └── graph/
│           ├── __init__.py
│           ├── builder.py       # LangGraph supervisor + 5 tools
│           └── state.py         # State definition
└── frontend/                    # React frontend (not included in this repo)
```

### Components Details

#### 1. `bot_multi_agent.py` - Voice Pipeline

**Functionality:**
- WebRTC server to receive audio stream
- AWS Transcribe STT service
- AWS Bedrock LLM service
- OpenAI TTS service
- Transcript processor
- WebSocket server for frontend

**API Endpoints:**
- `POST /offer` - WebRTC offer/answer
- `GET /ws` - WebSocket transcript streaming
- `GET /health` - Health check

#### 2. `task_queue.py` - Task Queue System

**Functionality:**
- Async task queue (max 100 tasks)
- Task lifecycle management
- Task status tracking
- Statistics and monitoring

**Task Types:**
- `TaskType.LOAN`
- `TaskType.CRM`
- `TaskType.HR`
- `TaskType.COMPLIANCE`
- `TaskType.OPERATIONS`

#### 3. `workflow_worker.py` - Background Worker

**Functionality:**
- Continuous loop processing tasks from queue
- Lazy loading LLM and workflow (load once)
- Error handling and retry logic
- Task status updates

#### 4. `browser_agent.py` - Browser Automation

**Functionality:**
- Browser-use AI agent with Playwright
- Form filling automation
- Screenshot capture
- Error handling

#### 5. `multi_agent/graph/builder.py` - LangGraph Workflow

**Functionality:**
- Supervisor agent with 5 specialist tools
- Tool selection logic
- Workflow orchestration
- State management

**5 Specialist Tools:**
1. `fill_loan_form()` - 13 parameters
2. `fill_crm_form()` - 8 parameters
3. `fill_hr_form()` - 8 parameters
4. `fill_compliance_form()` - 8 parameters
5. `fill_operations_form()` - 11 parameters

### Execution Flow

```
1. User Voice → WebRTC → bot_multi_agent.py
   ↓
2. STT (AWS Transcribe) → Text
   ↓
3. LLM (AWS Bedrock) → Response
   ↓
4. TTS (OpenAI) → Audio Output
   ↓
5. User Confirmation → push_task_to_queue()
   ↓
6. workflow_worker.py pops task
   ↓
7. LangGraph supervisor analyzes
   ↓
8. Calls appropriate specialist tool
   ↓
9. browser_agent.py fills form
   ↓
10. Task status → COMPLETED
```

---

## Troubleshooting

### Common Issues

#### Pods Not Starting (Docker)

```bash
# Check logs
docker logs <container-id>

# Check environment variables
docker exec <container-id> env | grep AWS
docker exec <container-id> env | grep OPENAI

# Restart container
docker restart <container-id>
```

#### AWS Credentials Invalid

```bash
# Test AWS credentials
aws sts get-caller-identity --profile default

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Check Transcribe access
# (No CLI command, only test via app)
```

#### OpenAI API Key Invalid

```bash
# Test OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### Browser Automation Timeout

```bash
# Check Playwright installation
playwright --version

# Reinstall browsers
playwright install chromium

# Test browser launch
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); p.chromium.launch()"
```

#### Frontend Cannot Connect to Backend

```bash
# Check if backend is running
curl http://localhost:7860/health

# Check CORS settings
# (Backend has auto CORS config)

# Check WebSocket connection
# (Browser DevTools → Network → WS tab)
```

#### Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Debug Mode

```bash
# Backend with debug logs
export PIPECAT_LOG_LEVEL=DEBUG
python main.py

# Frontend with verbose logs
cd frontend
npm run dev -- --debug
```

### Performance Tuning

```bash
# Increase task queue size (in task_queue.py)
TaskQueue(maxsize=200)  # Default: 100

# Increase worker timeout (in workflow_worker.py)
TIMEOUT_SECONDS = 300  # Default: 180

# Browser timeout (in browser_agent.py)
timeout=60000  # Default: 30000
```

---

## Development

### Development Setup

```bash
# Clone and setup
git clone https://github.com/minhnghia2k3/Speak_To_Input.git
cd Speak_To_Input

# Install development dependencies
pip install -r requirements.txt
pip install black flake8 mypy pytest

# Setup pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Testing

```bash
# Run unit tests (if available)
pytest tests/

# Run integration tests
python test_stable_config.py
python test_google_sheets.py
```

### Building

```bash
# Frontend production build
cd frontend
npm run build

# Preview production build
npm run preview
```

### Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Structure Guidelines

- **Imports**: Use relative imports within package
- **Async**: All I/O operations must be async
- **Error Handling**: Wrap in try-except with logging
- **Type Hints**: Use type hints for all functions
- **Documentation**: Docstrings for all public functions

---

## References

### Official Documentation

- [Pipecat AI Framework](https://github.com/pipecat-ai/pipecat)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AWS Transcribe](https://docs.aws.amazon.com/transcribe/)
- [AWS Bedrock](https://docs.aws.amazon.com/bedrock/)
- [OpenAI API](https://platform.openai.com/docs)
- [Playwright](https://playwright.dev/python/)

### Related Projects

- [browser-use](https://github.com/browser-use/browser-use) - AI-powered browser automation
- [LangChain](https://python.langchain.com/) - LLM application framework
- [Small WebRTC](https://github.com/pipecat-ai/smallwebrtc) - WebRTC transport

### Learning Resources

- [Multi-Agent Systems](https://www.python.langchain.com/docs/modules/multi_agent/) - LangChain multi-agent guide
- [Voice AI Best Practices](https://github.com/pipecat-ai/pipecat/wiki) - Pipecat wiki
- [AWS Bedrock Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models.html) - Available models

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Version Information

- **Version**: 1.0.0
- **Python**: 3.11.x
- **Pipecat AI**: 0.0.91
- **LangGraph**: 1.0.1
- **Playwright**: 1.55.0
- **Last Updated**: October 29, 2025

---

**Deployment Type**: Local Development / Production  
**License**: MIT License  
**Multi-Use Case Support**: 5 use cases (Loan, CRM, HR, Compliance, Operations)
