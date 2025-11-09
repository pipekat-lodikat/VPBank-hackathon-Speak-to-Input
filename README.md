# VPBank Voice Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Node Version](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-19.1.1-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.3-blue.svg)](https://www.typescriptlang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Production-ready voice-powered banking form automation using AI-driven conversational interface and intelligent browser automation.**

> A microservices-based system that enables users to fill Vietnamese banking forms through natural speech, leveraging WebRTC, PhoWhisper STT, Claude Sonnet 4, and autonomous browser agents.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [License](#license)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [Citation](#citation)
- [Team](#team)
- [Acknowledgments](#acknowledgments)

---

## Overview

VPBank Voice Agent is an enterprise-grade voice automation platform designed for Vietnamese banking operations. The system combines cutting-edge speech recognition, natural language understanding, and AI-powered browser automation to streamline form filling across five critical banking use cases:

| Use Case | Description | Form URL |
|----------|-------------|----------|
| **Loan Origination & KYC** | Customer onboarding and loan application processing | [Case 1](https://vpbank-shared-form-fastdeploy.vercel.app/) |
| **CRM Updates** | Customer relationship management data entry | [Case 2](https://case2-ten.vercel.app/) |
| **HR Workflows** | Employee data management and HR operations | [Case 3](https://case3-seven.vercel.app/) |
| **Compliance Reporting** | Regulatory compliance form submission | [Case 4](https://case4-beta.vercel.app/) |
| **Operations Validation** | Operational data verification and validation | [Case 5](https://case5-chi.vercel.app/) |

---

## Key Features

### Voice Interface
- **Real-time Speech Recognition**: Vietnamese language support via PhoWhisper STT
- **Natural Language Understanding**: Powered by Claude Sonnet 4 (AWS Bedrock)
- **Conversational AI**: Context-aware dialogue management
- **Voice Synthesis**: High-quality Vietnamese TTS using ElevenLabs

### Intelligent Automation
- **AI-Powered Browser Automation**: Autonomous form filling using GPT-4 and Playwright
- **Multi-Agent Orchestration**: LangGraph-based agent coordination
- **Session Management**: AWS DynamoDB for persistent conversation history
- **Error Recovery**: Automatic retry and fallback mechanisms

### Enterprise-Ready
- **Microservices Architecture**: Independently scalable services
- **Authentication**: AWS Cognito integration
- **Monitoring**: Comprehensive logging and metrics
- **Security**: PII masking, rate limiting, input validation
- **Cost Optimization**: LLM response caching and efficient resource usage

### User Experience
- **WebRTC Audio**: Low-latency bidirectional audio streaming
- **Real-time Transcripts**: Live conversation display via WebSocket
- **React Frontend**: Modern, responsive web interface
- **Dynamic Configuration**: Auto-detection for local and remote deployments

---

## Architecture

The system follows a **microservices architecture** with three independent services communicating via HTTP REST APIs and WebSocket:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                      Port 5173 - Web UI                          │
│                                                                   │
│  • WebRTC Audio Streaming (bidirectional)                        │
│  • Real-time Transcript Display (WebSocket)                      │
│  • Session Management UI                                         │
└────────────────┬────────────────────────────────────────────────┘
                 │ WebRTC + WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Voice Bot Service                             │
│                      Port 7860                                   │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PhoWhisper   │  │Claude Sonnet4│  │ ElevenLabs   │          │
│  │    (STT)     │  │     (LLM)    │  │     (TTS)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  • Audio Processing Pipeline (Pipecat AI)                        │
│  • Conversation Management                                       │
│  • Authentication (AWS Cognito)                                  │
│  • Session Storage (AWS DynamoDB)                                │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTP POST
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Browser Agent Service                           │
│                      Port 7863                                   │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ browser-use  │  │   GPT-4      │  │  Playwright  │          │
│  │  (Agents)    │  │ (Planning)   │  │  (Browser)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  • AI-Powered Browser Automation                                 │
│  • Form Detection & Filling                                      │
│  • Multi-Step Workflow Execution                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Service Communication Flow

1. **User → Frontend**: User initiates voice conversation via web browser
2. **Frontend → Voice Bot**: WebRTC audio stream + WebSocket for transcripts
3. **Voice Bot Processing**:
   - PhoWhisper STT converts speech to text (Vietnamese)
   - Claude Sonnet 4 understands intent and extracts data
   - ElevenLabs synthesizes Vietnamese voice responses
4. **Voice Bot → Browser Agent**: HTTP POST with extracted form data
5. **Browser Agent Execution**:
   - GPT-4 plans browser actions
   - Playwright executes automation
   - Returns completion status
6. **Voice Bot → User**: Voice confirmation of task completion

### Multi-Agent System

The system implements a **Supervisor Pattern** for multi-agent orchestration using LangGraph, enabling intelligent conversation flow and form filling coordination.

**Architecture:**
- **Supervisor Agent**: Orchestrates conversation flow and delegates tasks to specialist agents
- **Specialist Agents**: Extract and validate specific data fields from user speech
- **Browser Executor**: Executes automated form filling tasks using AI-powered browser automation

**Key Features:**
- **Incremental Form Filling**: Users can fill forms field-by-field through natural conversation
- **Wizard Navigation**: Supports multi-step forms with automatic progression
- **Session Management**: Maintains browser sessions across multiple interactions
- **Error Recovery**: Handles validation errors and retries failed operations

**Reference:**
- Based on LangGraph [Supervisor Pattern](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)
- Implementation: `src/multi_agent/graph/builder.py`

---

## Quick Start

### Prerequisites

- **Python 3.11.x** (required - not 3.12 or 3.13)
- **Node.js 18+** and npm
- **Git**
- **AWS Account** with Bedrock access
- **OpenAI API Key** with GPT-4 and Whisper access
- **ElevenLabs API Key** for Vietnamese TTS

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/pipekat-lodikat/speak-to-input.git
cd speak-to-input

# 2. Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR: venv\Scripts\activate  # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install chromium
playwright install-deps chromium  # Linux only

# 5. Install frontend dependencies
cd frontend
npm install
cd ..

# 6. Configure environment
cp .env.example .env
# Edit .env with your AWS, OpenAI, and ElevenLabs credentials

# 7. Start services (3 terminals)
# Terminal 1: Browser Agent
python main_browser_service.py

# Terminal 2: Voice Bot
python main_voice.py

# Terminal 3: Frontend
cd frontend && npm run dev -- --host 0.0.0.0

# 8. Open browser
# Navigate to http://localhost:5173
```

**Quick Start Script** (starts all services):
```bash
./scripts/start-dev.sh
```

---

## Installation

### System Requirements

| Component | Requirement |
|-----------|------------|
| **Operating System** | Windows 10+, macOS 11+, or Linux (Ubuntu 20.04+) |
| **Python** | 3.11.x (required for Pipecat AI compatibility) |
| **Node.js** | 18.x or higher |
| **RAM** | 4GB minimum, 8GB recommended |
| **Disk Space** | 2GB for dependencies and browsers |
| **Network** | Stable internet for AWS/OpenAI APIs |

### Step 1: Python Environment

```bash
# Install Python 3.11 if not available
# Ubuntu/Debian:
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv

# macOS (with Homebrew):
brew install python@3.11

# Windows:
# Download from python.org/downloads/

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows PowerShell:
venv\Scripts\activate

# Windows Command Prompt:
venv\Scripts\activate.bat

# Verify Python version
python --version  # Should show Python 3.11.x
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Linux only: Install system dependencies for Playwright
playwright install-deps chromium
```

### Step 3: Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Build for production (optional)
npm run build

cd ..
```

### Step 4: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```bash
# AWS Credentials (for Bedrock only)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# AWS Bedrock Model
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# OpenAI API Key (for PhoWhisper STT and GPT-4 browser automation)
OPENAI_API_KEY=your_openai_api_key

# ElevenLabs TTS (Vietnamese Voice)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id

# AWS Cognito (Authentication)
COGNITO_USER_POOL_ID=your_pool_id
COGNITO_CLIENT_ID=your_client_id

# AWS DynamoDB (Session Storage)
DYNAMODB_TABLE_NAME=vpbank-sessions
DYNAMODB_ACCESS_KEY_ID=your_dynamodb_key
DYNAMODB_SECRET_ACCESS_KEY=your_dynamodb_secret
DYNAMODB_REGION=us-east-1

# Service URLs (defaults)
BROWSER_SERVICE_URL=http://localhost:7863

# Form URLs (defaults provided)
LOAN_FORM_URL=https://vpbank-shared-form-fastdeploy.vercel.app/
CRM_FORM_URL=https://case2-ten.vercel.app/
HR_FORM_URL=https://case3-seven.vercel.app/
COMPLIANCE_FORM_URL=https://case4-beta.vercel.app/
OPERATIONS_FORM_URL=https://case5-chi.vercel.app/
```

### Step 5: AWS Setup

#### Enable AWS Bedrock Access

1. Navigate to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Select region: **US East (N. Virginia) - us-east-1**
3. Go to **Model access**
4. Click **Enable specific models**
5. Enable: **Anthropic Claude Sonnet 4**

#### Configure IAM Permissions

Create an IAM user with Bedrock access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/us.anthropic.claude-sonnet-4-*"
    }
  ]
}
```

#### Setup OpenAI API

1. Create account at [OpenAI Platform](https://platform.openai.com/)
2. Generate API key from [API Keys](https://platform.openai.com/api-keys)
3. Ensure you have access to:
   - **Whisper API** (for speech-to-text)
   - **GPT-4** (for browser automation)

#### Setup Cognito User Pool

1. Create user pool in [AWS Cognito Console](https://console.aws.amazon.com/cognito/)
2. Configure app client
3. Note the **User Pool ID** and **Client ID**

#### Setup DynamoDB Table

```bash
aws dynamodb create-table \
    --table-name vpbank-sessions \
    --attribute-definitions AttributeName=session_id,AttributeType=S \
    --key-schema AttributeName=session_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

---

## Configuration

### Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key for Bedrock only | Yes | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for Bedrock | Yes | - |
| `AWS_REGION` | AWS region for Bedrock | Yes | `us-east-1` |
| `BEDROCK_MODEL_ID` | Claude model identifier | Yes | `us.anthropic.claude-sonnet-4-20250514-v1:0` |
| `OPENAI_API_KEY` | OpenAI API key for PhoWhisper STT & GPT-4 browser automation | Yes | - |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Yes | - |
| `ELEVENLABS_VOICE_ID` | Vietnamese voice ID | Yes | - |
| `COGNITO_USER_POOL_ID` | AWS Cognito user pool | Yes | - |
| `COGNITO_CLIENT_ID` | Cognito app client ID | Yes | - |
| `DYNAMODB_TABLE_NAME` | DynamoDB table name | Yes | `vpbank-sessions` |
| `BROWSER_SERVICE_URL` | Browser Agent URL | No | `http://localhost:7863` |

### Frontend Configuration

Frontend automatically detects API URL based on hostname:

```typescript
// frontend/src/config.ts
const hostname = window.location.hostname;

// Remote access: use server IP/domain
if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
  return `${protocol}//${hostname}:7860`;
}

// Local development: use localhost
return 'http://localhost:7860';
```

### Logging Configuration

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR)
export LOG_LEVEL=DEBUG

# Enable debug mode
export DEBUG=true
```

---

## Usage

### Running Services

**Important:** Always start services in this order:

1. **Browser Agent Service** (port 7863) - Must start first
2. **Voice Bot Service** (port 7860) - Depends on Browser Agent
3. **Frontend** (port 5173) - Depends on Voice Bot

#### Option 1: Manual Start (Recommended for Development)

**Terminal 1 - Browser Agent:**
```bash
python main_browser_service.py
```

Wait for:
```
🌐 Starting Browser Agent Service...
📡 Service runs on port 7863
✅ Browser automation ready
```

**Terminal 2 - Voice Bot:**
```bash
python main_voice.py
```

Wait for:
```
🎤 Starting Voice Bot Service...
📡 Service runs on port 7860
✅ Voice bot ready
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

Access at: `http://localhost:5173`

#### Option 2: Quick Start Script

```bash
./scripts/start-dev.sh
```

This script:
- Starts all services in correct order
- Opens browser automatically
- Handles process management

#### Option 3: Docker Compose

```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using the Application

1. **Open Frontend**: Navigate to `http://localhost:5173`
2. **Login**: Authenticate using AWS Cognito
3. **Start Conversation**: Click microphone icon to begin
4. **Speak Naturally**: Describe the form you want to fill in Vietnamese
5. **Confirm Data**: Review extracted information
6. **Auto-Fill**: System automatically fills the form
7. **Verify**: Check completed form in browser

### Health Checks

```bash
# Check Browser Agent
curl http://localhost:7863/api/health

# Check Voice Bot (requires browser)
open http://localhost:7860

# Check Frontend
curl http://localhost:5173
```

### Stopping Services

**Quick Stop Script:**
```bash
./scripts/stop.sh
```

**Manual Stop:**
```bash
# Find and kill processes
lsof -ti:7860,7863,5173 | xargs kill -9
```

---

## API Reference

### Browser Agent Service (Port 7863)

#### POST `/api/execute`

Execute browser automation workflow.

**Request:**
```json
{
  "user_message": "Fill loan application form with customer data",
  "session_id": "user-session-123"
}
```

**Response:**
```json
{
  "status": "success",
  "result": "Form filled successfully",
  "execution_time": 12.5
}
```

#### GET `/api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "browser-agent",
  "version": "1.0.0"
}
```

### Voice Bot Service (Port 7860)

#### POST `/offer`

WebRTC offer endpoint for audio streaming.

**Request:**
```json
{
  "sdp": "v=0...",
  "type": "offer"
}
```

**Response:**
```json
{
  "sdp": "v=0...",
  "type": "answer"
}
```

#### WebSocket `/ws`

Real-time transcript streaming.

**Message Format:**
```json
{
  "type": "transcript",
  "role": "user|assistant",
  "content": "Transcript text",
  "timestamp": "2025-01-09T12:00:00Z"
}
```

---

## Deployment

### Production Deployment (AWS ECS Fargate)

#### Prerequisites

- AWS CLI configured
- Docker installed
- Terraform installed (optional)

#### Step 1: Deploy Infrastructure

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan
```

This creates:
- VPC with public/private subnets
- ECS Cluster and Task Definitions
- Application Load Balancer
- Security Groups
- Auto-scaling policies

#### Step 2: Build and Push Docker Images

```bash
./scripts/deploy-ecs-fargate.sh
```

This script:
1. Builds Docker images
2. Pushes to AWS ECR
3. Updates ECS task definitions
4. Deploys to ECS cluster

#### Step 3: Configure DNS and HTTPS

See `docs/HTTPS_DEPLOYMENT_GUIDE.md` for detailed instructions.

### Environment-Specific Configuration

**Development:**
```bash
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG
```

**Production:**
```bash
export ENVIRONMENT=production
export LOG_LEVEL=WARNING
```

### Security Group Configuration

For remote access, allow these ports:

**TCP:**
- 5173 (Frontend)
- 7860 (Voice Bot)
- 7863 (Browser Agent)
- 443 (HTTPS)

**UDP:**
- 3478 (STUN)
- 49152-65535 (WebRTC media, or restricted range)

---

## Project Structure

```
speak-to-input/
├── infrastructure/              # Infrastructure as Code
│   └── terraform/              # Terraform configurations (ECS, VPC, ALB)
├── scripts/                    # Deployment and utility scripts
│   ├── deploy-ecs-fargate.sh  # ECS deployment script
│   ├── start-dev.sh           # Start all services
│   └── stop.sh                # Stop all services
├── docs/                       # Documentation
│   ├── requirements/          # Requirements, proposals, technical docs
│   └── images/                # Documentation images
├── src/                        # Backend Python source
│   ├── voice_bot.py           # WebRTC/STT/TTS/LLM pipeline
│   ├── browser_agent.py       # Browser automation handler
│   ├── dynamodb_service.py    # Session storage
│   ├── auth_service.py        # Cognito authentication
│   ├── llm_evaluator/         # LangSmith evaluation
│   ├── cost/                  # Cost tracking and analytics
│   ├── monitoring/            # Monitoring and observability
│   ├── prompts/               # LLM prompt templates
│   ├── security/              # Security utilities (PII masking, rate limiting)
│   └── verification/          # Verification and validation
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── config.ts          # Dynamic API URL configuration
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   └── hooks/             # React hooks
│   ├── package.json
│   └── vite.config.ts
├── tests/                      # Test suites
├── vpbank-forms/              # Form templates (5 cases)
├── main_voice.py              # Voice Bot entry point
├── main_browser_service.py    # Browser Agent entry point
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Container orchestration
├── Dockerfile                 # Container image definition
├── .env.example               # Environment variable template
├── .gitignore                 # Git ignore patterns
├── README.md                  # This file
└── CLAUDE.md                  # Claude Code instructions
```

---

## Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11 | Core runtime |
| **Pipecat AI** | 0.0.91 | WebRTC/Voice framework |
| **PhoWhisper STT** | - | Speech-to-text service (Vietnamese) |
| **AWS Bedrock** | - | Claude Sonnet 4 LLM |
| **ElevenLabs** | - | Text-to-speech (Vietnamese) |
| **browser-use** | 0.9.5 | AI browser automation |
| **Playwright** | 1.55.0 | Browser control |
| **OpenAI GPT-4** | - | Browser automation planning |
| **LangChain** | - | LLM orchestration |
| **LangGraph** | - | Multi-agent workflows ([Supervisor Pattern](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)) |
| **aiohttp** | 3.12.15 | Async HTTP server |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.1.1 | UI framework |
| **Vite** | 7.1.2 | Build tool |
| **TypeScript** | 5.8.3 | Type safety |
| **TailwindCSS** | 4.1.13 | Styling |
| **Pipecat React UI** | - | WebRTC components |

### OpenAI Services (via Pipecat)

- **PhoWhisper STT**: Real-time speech-to-text (Vietnamese optimized)
- **GPT-4**: Browser automation planning

### AWS Services

- **Bedrock**: Claude Sonnet 4 LLM inference (NOT used for STT)
- **Cognito**: User authentication
- **DynamoDB**: Session storage
- **ECS Fargate**: Container orchestration
- **ALB**: Application load balancing
- **ECR**: Container registry

### Communication Protocols

- **WebRTC**: Bidirectional audio streaming
- **WebSocket**: Real-time transcript updates
- **HTTP REST**: Service-to-service communication

---

## Development

### Code Style

**Python:**
```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
```

**TypeScript:**
```bash
cd frontend

# Lint
npm run lint

# Type check
npm run type-check

# Format
npm run format
```

### Running Tests

```bash
# Python tests
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Run with verbose output
python main_voice.py --verbose
```

### Development Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Run linters and formatters
4. Commit with conventional commits: `feat: add new feature`
5. Push and create pull request

---

## Troubleshooting

### Common Issues

#### "Module not found" or Import Error

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Must be 3.11.x
```

#### "Playwright browser not found"

**Solution:**
```bash
playwright install chromium
playwright install-deps chromium  # Linux only
```

#### "Network error" or "404: Not Found API"

**Causes:**
- Voice Bot not running on port 7860
- Browser Agent not started before Voice Bot
- Incorrect API URL configuration

**Solution:**
```bash
# Check services are running
curl http://localhost:7863/api/health  # Browser Agent
curl http://localhost:7860              # Voice Bot

# Restart in correct order
./scripts/stop.sh
./scripts/start-dev.sh
```

#### "WebRTC connection timeout"

**Cause:** UDP ports not open for WebRTC media

**Solution:**
```bash
# For remote access, ensure security group allows:
# - UDP 3478 (STUN)
# - UDP 49152-65535 (WebRTC media)

# Check frontend WebSocket in browser DevTools
```

#### "Address already in use"

**Solution:**
```bash
# Kill processes on ports
lsof -ti:7860 | xargs kill -9
lsof -ti:7863 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Or use stop script
./scripts/stop.sh
```

#### Browser Automation Fails

**Solutions:**
```bash
# Verify OpenAI API key
echo $OPENAI_API_KEY

# Check Playwright installation
playwright install chromium

# Review logs
tail -f logs/browser_agent.log
```

### Debug Checklist

- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip list`)
- [ ] `.env` file configured with valid credentials
- [ ] Playwright browsers installed
- [ ] Services started in correct order
- [ ] Ports 5173, 7860, 7863 available
- [ ] AWS credentials valid (`aws sts get-caller-identity`)
- [ ] OpenAI API key valid
- [ ] Network connectivity to AWS/OpenAI

---

## Security

### Best Practices

1. **Never commit `.env` file** to version control
2. **Rotate credentials regularly** (every 90 days)
3. **Use IAM roles** in production (not access keys)
4. **Enable MFA** on all AWS and API accounts
5. **Set API usage limits** to prevent cost overruns
6. **Monitor API usage** via CloudWatch and OpenAI dashboard
7. **Implement rate limiting** for production endpoints
8. **Validate all inputs** before processing
9. **Mask PII** in logs and transcripts

### Security Features

- **PII Masking**: Automatic redaction of sensitive data (`src/security/pii_masking.py`)
- **Rate Limiting**: Request throttling (`src/security/rate_limiter.py`)
- **Input Validation**: Sanitization of user inputs
- **Authentication**: AWS Cognito integration
- **Session Security**: Encrypted session storage in DynamoDB
- **HTTPS**: TLS encryption for all communications (production)

### Cost Management

**Estimated Monthly Costs** (moderate usage):

| Service | Unit Cost | Monthly Estimate |
|---------|-----------|------------------|
| PhoWhisper STT | $0.006/min | $5-10 |
| AWS Bedrock (Claude) | $0.003/1K tokens | $15-30 |
| ElevenLabs TTS | $15/1M chars | $10-20 |
| OpenAI GPT-4 | $0.01-0.03/task | $30-60 |
| **Total** | - | **$60-120** |

**Cost Optimization:**
- Enable LLM response caching (`src/cost/llm_cache.py`)
- Set API usage alerts in AWS Billing
- Monitor costs via CloudWatch dashboards
- Use reserved capacity for predictable workloads

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright © 2025 Pipekat Lodikat Team

---

## Contributing

We welcome contributions from the community! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows our [coding standards](CONTRIBUTING.md#coding-standards) and includes appropriate tests.

---

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## Citation

If you use this project in your research or work, please cite it as:

```bibtex
@software{vpbank_voice_agent_2025,
  author = {Bùi, Hồ Ngọc Hân and Phạm, Nguyễn Hải Anh and Lê, Minh Nghĩa and Nguyễn, Đức Toàn and Danh, Hoàng Hiếu Nghị},
  title = {VPBank Voice Agent: AI-Powered Banking Form Automation},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/pipekat-lodikat/speak-to-input}
}
```

See [CITATION.cff](CITATION.cff) for more citation formats.

---

## Team

**Pipekat Lodikat** - VPBank Tech Hack 2025

| Name | GitHub | Role |
|------|--------|------|
| Bùi Hồ Ngọc Hân | [@lodi-bui](https://github.com/lodi-bui) | Core Developer |
| Phạm Nguyễn Hải Anh | [@PNg-HA](https://github.com/PNg-HA) | Core Developer |
| Lê Minh Nghĩa | [@minhnghia2k3](https://github.com/minhnghia2k3) | Core Developer |
| Nguyễn Đức Toàn | [@toannd021104](https://github.com/toannd021104) | Core Developer |
| Danh Hoàng Hiếu Nghị | [@ihatesea69](https://github.com/ihatesea69) | Core Developer |

For detailed contributor information, see [AUTHORS](AUTHORS) and [CONTRIBUTORS.md](CONTRIBUTORS.md).

---

## Acknowledgments

This project was developed for **VPBank Tech Hack 2025** and builds upon several outstanding open-source projects:

### Core Technologies

- [Pipecat AI](https://www.pipecat.ai/) - Real-time voice conversation framework
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - Claude Sonnet 4 LLM access
- [browser-use](https://github.com/browser-use/browser-use) - AI-powered browser automation
- [Playwright](https://playwright.dev/) - Browser automation library
- [React](https://react.dev/) - Frontend framework
- [Vite](https://vitejs.dev/) - Build tool

### AI Services

- [Anthropic Claude](https://www.anthropic.com/) - Natural language understanding
- [PhoWhisper](https://github.com/VinAIResearch/PhoWhisper) - Vietnamese speech-to-text model
- [OpenAI GPT-4](https://openai.com/) - Browser automation planning
- [ElevenLabs](https://elevenlabs.io/) - Text-to-speech (Vietnamese)

### Special Thanks

- AWS for Bedrock access and cloud infrastructure
- VPBank for the Tech Hack 2025 opportunity
- All contributors and maintainers
- The open-source community

---

For questions, issues, or feature requests:

- **Issues**: [GitHub Issues](https://github.com/pipekat-lodikat/speak-to-input/issues)
- **Documentation**: See `/docs` directory
- **Technical Details**: See `CLAUDE.md`

---

**Built with ❤️ by Pipekat Lodikat for VPBank Tech Hack 2025**
