# VPBank Voice Agent

A production-ready voice-powered form automation system for banking operations. This system enables users to fill banking forms using natural Vietnamese speech through a multi-agent architecture.

## Overview

VPBank Voice Agent is a microservices-based system that combines speech recognition, natural language understanding, and browser automation to automate form filling for five banking use cases:

- Loan Origination & KYC
- CRM Updates
- HR Workflows
- Compliance Reporting
- Operations Validation

### Architecture

The system follows a microservices architecture with three independent services:

1. **Voice Bot Service** (Port 7860): Handles WebRTC audio streaming, speech-to-text, text-to-speech, and conversational AI
2. **Task Queue Service** (Port 7862): HTTP REST API for managing tasks between services
3. **Browser Worker Service**: Background service that executes multi-agent workflows and browser automation

Communication between services is handled via HTTP REST API through the Task Queue Service.

## Prerequisites

### System Requirements

- **Python**: 3.11.x (required, not 3.12 or 3.13)
- **Operating System**: Windows 10+, macOS, or Linux
- **Rust**: Required for building some Python dependencies

### Required Credentials

Before installation, ensure you have:

1. **AWS Account** with IAM user credentials:
   - Access to AWS Transcribe (Speech-to-Text)
   - Access to AWS Bedrock with Claude Sonnet 4 model enabled
   - Required permissions documented below

2. **OpenAI API Key**:
   - Account with billing enabled
   - API key with model access permissions

## Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd VPBankHackathon
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Install Rust (if not already installed)

Some Python dependencies require Rust to compile.

**Windows:**
```powershell
winget install Rustlang.Rustup
```

**Linux/macOS:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### Step 4: Install Playwright Browsers

```bash
playwright install chromium
playwright install-deps chromium  # Linux only
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and provide the following variables:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1

# AWS Bedrock Model ID
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Browser Agent Service URL (optional, default: http://localhost:7863)
BROWSER_SERVICE_URL=http://localhost:7863

# Form URLs (optional, defaults provided)
LOAN_FORM_URL=https://vpbank-shared-form-fastdeploy.vercel.app/
CRM_FORM_URL=https://case2-ten.vercel.app/
HR_FORM_URL=https://case3-seven.vercel.app/
COMPLIANCE_FORM_URL=https://case4-beta.vercel.app/
OPERATIONS_FORM_URL=https://case5-chi.vercel.app/
```

### Step 6: AWS IAM Setup

Create an IAM user with the following permissions:

**Required Policies:**
- `AmazonTranscribeFullAccess` (for Speech-to-Text)
- `AmazonBedrockFullAccess` (for Claude LLM)

**Or create a custom policy with least privilege:**

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

**Enable Bedrock Model Access:**
1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Select region: US East (N. Virginia) - us-east-1
3. Navigate to Model access
4. Enable: Anthropic Claude Sonnet 4

### Step 7: OpenAI Setup

1. Create account at [OpenAI Platform](https://platform.openai.com/)
2. Add payment method and credits
3. Create API key from [API Keys](https://platform.openai.com/api-keys)
4. Set usage limits (recommended for production)

## Running the Application

### Prerequisites

Đảm bảo đã:
1. Activate virtual environment: `venv\Scripts\activate` (Windows) hoặc `source venv/bin/activate` (Linux/macOS)
2. Install dependencies: `pip install -r requirements.txt`
3. Config `.env` file với AWS và OpenAI credentials
4. Install Playwright browsers: `playwright install chromium`

### Quick Start

Run both services separately (recommended):

#### Step 1: Start Browser Agent Service

Open Terminal 1:

```bash
python main_browser_service.py
```

Service starts on `http://localhost:7863`

You should see:
```
🌐 Starting Browser Agent Service...
📡 Service runs on port 7863
🔗 Endpoints:
   POST   /api/execute - Execute workflow
   GET    /api/health - Health check
✅ Workflow initialized (model: ...)
```

#### Step 2: Start Voice Bot Service

Open Terminal 2:

```bash
# Windows PowerShell:
python main_voice.py

# Linux/macOS:
python main_voice.py
```

**Note:** Nếu Browser Service chạy trên port/ host khác, set environment variable:
```bash
# Windows PowerShell:
$env:BROWSER_SERVICE_URL="http://localhost:7863"
python main_voice.py

# Linux/macOS:
export BROWSER_SERVICE_URL="http://localhost:7863"
python main_voice.py
```

Service starts on `http://localhost:7860`

You should see:
```
🎤 Starting Voice Bot Service...
📡 Service runs on port 7860
🚀 Voice bot ready - workflow will execute directly when needed
```

### How It Works

1. **Voice Bot** receives voice input from user
2. User confirms → Voice Bot sends HTTP POST to Browser Service
3. **Browser Service** executes multi-agent workflow → browser automation
4. Browser Service returns result → Voice Bot notifies user via WebSocket

### Important Notes

1. **Service Order**: 
   - Always start Browser Agent Service first
   - Then start Voice Bot Service
   - Voice Bot will push requests to Browser Service

2. **Environment Variable `BROWSER_SERVICE_URL`**: 
   - Default: `http://localhost:7863`
   - Set this if Browser Service runs on different host/port

3. **Service Health**: 
   - Check Browser Service: `curl http://localhost:7863/api/health`
   - Check Voice Bot: Open `http://localhost:7860` in browser

### Docker Compose (Optional)

Build and run all services using Docker:

```bash
docker-compose up --build
```

View logs:
```bash
docker-compose logs -f
```

Stop services:
```bash
docker-compose down
```

## API Endpoints

### Browser Agent Service (Port 7863)

- `POST /api/execute` - Execute workflow (takes user_message and session_id)
- `GET /api/health` - Health check endpoint

### Voice Bot Service (Port 7860)

- `POST /offer` - WebRTC offer endpoint
- `GET /ws` - WebSocket endpoint for transcript streaming

## Configuration

### Environment Variables

All services share the same `.env` file. Key variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `AWS_ACCESS_KEY_ID` | AWS IAM user access key | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM user secret key | Yes |
| `AWS_REGION` | AWS region (default: us-east-1) | Yes |
| `BEDROCK_MODEL_ID` | Bedrock model identifier | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `BROWSER_SERVICE_URL` | Browser Agent Service URL (microservices mode) | No (default: http://localhost:7863) |

### Logging

Logs are output to console with structured formatting using `loguru`. Set log level via:

```bash
export LOG_LEVEL=DEBUG  # Linux/macOS
$env:LOG_LEVEL="DEBUG"  # Windows PowerShell
```

## Project Structure

```
VPBankHackathon/
├── src/                          # Backend source code
│   ├── voice_bot.py             # Voice bot service (WebRTC/STT/TTS/LLM)
│   ├── browser_agent.py         # Browser automation handler
│   └── multi_agent/              # Multi-agent system
│       └── graph/
│           ├── builder.py        # Supervisor workflow builder
│           └── state.py          # LangGraph state definition
├── main_voice.py                 # Voice bot service entry point
├── main_browser_service.py       # Browser agent service entry point (HTTP API)
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Docker orchestration
├── Dockerfile                     # Docker image definition
└── .env                           # Environment variables (not in git)
```

## Technology Stack

### Backend

- **Python 3.11**: Core runtime
- **Pipecat AI 0.0.91**: Voice AI framework (WebRTC, STT, TTS)
- **AWS Transcribe**: Speech-to-text (Vietnamese)
- **AWS Bedrock**: Claude Sonnet 4 LLM
- **OpenAI TTS**: Text-to-speech
- **LangGraph 1.0.1**: Multi-agent orchestration
- **browser-use 0.1.40**: AI-powered browser automation
- **Playwright 1.55.0**: Browser automation runtime
- **aiohttp 3.11.12**: Async HTTP server

### Communication

- **WebRTC**: Bidirectional audio streaming
- **WebSocket**: Real-time transcript streaming
- **HTTP REST API**: Inter-service communication

## Development

### Running Tests

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Run specific tests (if available)
python -m pytest tests/
```

### Code Formatting

```bash
# Format Python code
black src/
isort src/

# Type checking
mypy src/
```

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

## Troubleshooting

### Common Issues

**Error: Module not found**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Error: Playwright browser not found**
```bash
playwright install chromium
playwright install-deps chromium  # Linux only
```

**Error: AWS credentials invalid**
- Verify `.env` file has correct credentials
- Test with: `aws sts get-caller-identity`
- Ensure IAM user has required permissions

**Error: Docker Desktop not running**
- Start Docker Desktop application
- Or use manual setup instead

**Error: Service connection failed**
- Verify Task Queue Service is running: `curl http://localhost:7862/api/health`
- Check `TASK_QUEUE_SERVICE_URL` environment variable is set correctly

**Error: Browser automation timeout**
- Check form URLs are accessible
- Verify Playwright browsers are installed
- Review browser automation logs for details

## Security Considerations

1. **Never commit `.env` file** to version control
2. **Rotate API keys** regularly (every 3-6 months)
3. **Use IAM roles** in production (instead of access keys when possible)
4. **Enable MFA** on AWS and OpenAI accounts
5. **Set usage limits** on OpenAI API keys
6. **Monitor costs** via AWS Cost Explorer and OpenAI usage dashboard

## Cost Estimation

Approximate monthly costs for moderate usage:

- **AWS Transcribe**: ~$0.024 per minute of audio
- **AWS Bedrock (Claude Sonnet 4)**: ~$0.003 per 1K input tokens
- **OpenAI TTS**: $15 per 1M characters
- **browser-use (GPT-4)**: ~$0.01-0.03 per task

**Estimated monthly cost**: $50-120 for moderate usage (100 conversations/day, 100 tasks/day)

## License

[Specify license here]

## Contributing

[Contributing guidelines if applicable]

## Support

For issues and questions, please open an issue in the repository.
