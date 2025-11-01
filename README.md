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

# Task Queue Service URL (for microservices mode)
TASK_QUEUE_SERVICE_URL=http://localhost:7862

# Form URLs (optional, defaults provided)
LOAN_FORM_URL=http://use-case-1-loan-origination.s3-website-us-west-2.amazonaws.com
CRM_FORM_URL=http://use-case-2-crm-update.s3-website-us-west-2.amazonaws.com
HR_FORM_URL=http://use-case-3-hr-workflow.s3-website-us-west-2.amazonaws.com
COMPLIANCE_FORM_URL=http://use-case-4-compliance-reporting.s3-website-us-west-2.amazonaws.com
OPERATIONS_FORM_URL=http://use-case-5-operations-validation.s3-website-us-west-2.amazonaws.com
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

### Option 1: Monolithic Mode (Single Process)

Run all services in a single process:

```bash
python main.py
```

The server will start on `http://localhost:7860`

### Option 2: Microservices Mode (Recommended for Production)

Run services separately for better scalability and fault isolation.

#### Terminal 1: Task Queue Service

```bash
python services/task_queue_service/main.py
```

Service starts on `http://localhost:7862`

#### Terminal 2: Voice Bot Service

```bash
# Windows PowerShell:
$env:TASK_QUEUE_SERVICE_URL="http://localhost:7862"
python main_voice.py

# Linux/macOS:
export TASK_QUEUE_SERVICE_URL="http://localhost:7862"
python main_voice.py
```

Service starts on `http://localhost:7860`

#### Terminal 3: Browser Worker Service

```bash
# Windows PowerShell:
$env:TASK_QUEUE_SERVICE_URL="http://localhost:7862"
python main_worker.py

# Linux/macOS:
export TASK_QUEUE_SERVICE_URL="http://localhost:7862"
python main_worker.py
```

Service runs in background, polling tasks from Task Queue Service.

### Option 3: Docker Compose

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

### Task Queue Service (Port 7862)

- `POST /api/tasks/push` - Push a new task to queue
- `GET /api/tasks/pop` - Pop next task (long polling, 30s timeout)
- `PATCH /api/tasks/{task_id}` - Update task status
- `GET /api/tasks/{task_id}` - Get task by ID
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
| `TASK_QUEUE_SERVICE_URL` | Task queue service URL (microservices mode) | No |

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
│   ├── bot_multi_agent.py        # Voice bot service (WebRTC/STT/TTS/LLM)
│   ├── workflow_worker.py       # Browser worker service
│   ├── browser_agent.py          # Browser automation handler
│   ├── task_queue.py             # Task queue implementation
│   └── multi_agent/              # Multi-agent system
│       └── graph/
│           ├── builder.py        # Supervisor workflow builder
│           └── state.py          # LangGraph state definition
├── services/                      # Microservices
│   ├── task_queue_service/       # Task queue HTTP API server
│   │   └── main.py
│   └── shared/                   # Shared utilities
│       ├── task_queue_api.py    # HTTP API client
│       └── task_queue_wrapper.py # Wrapper (local/API modes)
├── main.py                       # Monolithic entry point
├── main_voice.py                 # Voice bot service entry point
├── main_worker.py                # Browser worker entry point
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
