# VPBank Voice Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Node Version](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

**Voice-powered banking form automation using AI-driven conversation and intelligent browser automation.**

> Fill Vietnamese banking forms through natural speech using WebRTC, PhoWhisper STT, Claude Sonnet 4, and autonomous browser agents.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture of Solution](#architecture-of-solution)
- [Workflows](#workflows)
- [Cost Breakdown](#cost-breakdown)
- [Team](#team)

---

## Quick Start

### Prerequisites

- **Python 3.11.x** (required)
- **Node.js 18+** and npm
- **AWS Account** with Bedrock access
- **OpenAI API Key** (GPT-4 + Whisper)
- **ElevenLabs API Key** (Vietnamese TTS)

### Run the Application

```bash
# 1. Clone and setup environment
git clone https://github.com/pipekat-lodikat/speak-to-input.git
cd speak-to-input
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium
cd frontend && npm install && cd ..

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Start services (3 terminals required)
# Terminal 1:
python main_browser_service.py

# Terminal 2:
python main_voice.py

# Terminal 3:
cd frontend && npm run dev -- --host 0.0.0.0

# 5. Open browser at http://localhost:5173
```

**Service Startup Order:** Browser Agent (7863) → Voice Bot (7860) → Frontend (5173)

---

## Architecture of Solution

### High-Level Architecture

![High-Level Architecture](/docs/images/Animation_Overview.gif)

The system consists of three main components working together:

1. **Pipecat Workflow (Left)** - Real-time voice processing
   - User Voice → Audio Processing → Speech to Text → LLM → Text to Speech → User

2. **LangGraph Workflow (Right)** - Multi-agent orchestration
   - Workflow Router Agent coordinates specialist agents (CRM, Loan, HR, Compliance)
   - Each agent connects to Browser-Use Execution Agent for form automation

3. **Integration Flow (Numbered Steps)**
   - **Step 1:** User speaks into microphone
   - **Step 2:** LLM processes transcribed text and sends to LangGraph
   - **Step 3:** Workflow Router Agent determines intent and routes to specialist agent
   - **Step 4:** Specialist agent (CRM/Loan/HR/Compliance) processes request
   - **Step 5:** Browser-Use Execution Agent fills target forms
   - **Step 6:** Results flow back to LLM for response generation
   - **Step 7:** TTS converts response to voice and plays back to user

---

### Detailed Architecture

![Detailed Architecture](/docs/images/image-2.png)

#### **React UI Layer**
- Voice microphone interface for audio input
- Browser display for real-time transcripts
- User authentication and session management

#### **Frontend Services**
- **Cognito** - User authentication
- **Cloudfront** - CDN for static assets
- **S3** - Voice AI UI hosting
- **API Gateway** - API routing and management

#### **Pipecat Workflow - Audio Processing Pipeline**

**Audio Processing Steps:**
1. **Silero VAD** - Voice activity detection
2. **Smart Turn** - Conversation turn management
3. **Fine-tuned PhoWhisper (STT)** - Vietnamese speech-to-text
4. **LLLM (Claude Sonnet 4)** - Intent understanding and data extraction
5. **ElevenLabs (TTS)** - Vietnamese voice synthesis

#### **LangGraph Workflow - Multi-Agent Banking Operations**

**Banking Operation Agents:**
- **LOS Agent** - Loan Origination System
- **CRM Agent** - Customer Relationship Management
- **HR Agent** - Human Resources
- **Compliance Agent** - Regulatory compliance

**Coordination & Processing:**
5. **External Regulation** - Optional regulatory documents
6. **ECS Pgvector** - Vector embeddings storage
6. **Amazon Bedrock Coordinator** - Multi-agent orchestration
6. **AWS Lambda** - Content validation and PDF extraction (optional)
7. **Amazon Bedrock Guardrails** - PII filtering
7. **Browser-Use Agent** - Form automation via Playwright

**Data Storage & Monitoring:**
- **DynamoDB** - Conversation history
- **CloudWatch** - Performance metrics
- **S3** - Banking forms and documents

---

## Workflows

### Overall Solution Workflow

![Overall Solution Workflow](/docs/images/image-3.png)

**Complete System Flow:**

1. **Client Side** - User provides voice input
2. **Audio Processing Layer** - Noise Canceling → Voice Activity Detector → Audio Turn Detector → STT Model
3. **LangGraph Coordination Layer** - Agent Registry → Supervisor Agent → Context Manager
4. **Processing Agents** - Loan Origination, CRM, Human Resources, Compliance Validation
5. **Decision Layer** - Decision Synthesis → Consensus Builder → Final Decision → Browser-use Agent
6. **Output Layer** - Banking Form → TTS Model → Audit Trail → User

---

### 1. Loan Origination & KYC Workflow

![Loan Submission Workflow](/docs/images/image-4.png)

**Purpose:** Process loan applications and customer onboarding

**Workflow Steps:**

1. **Client Side** - Loan applicant speaks into voice interface
2. **Audio Processing** - Noise Canceling → Voice Activity Detector → Audio Turn Detector → STT Model
3. **LangGraph Coordination** - Supervisor Agent routes to LOS Agent
4. **Processing Agents** - LOS Agent accesses Internal Bank Document and External Document
5. **Decision Layer** - Decision Synthesis → Consensus Builder → Final Decision → Browser-use Agent
6. **Output Layer** - Loan Submission Form filled → TTS Model responds → Audit Trail → Loan Applicant

**Form Fields:**
- Personal information (name, DOB, ID card)
- Employment details (occupation, income)
- Loan details (amount, term, purpose)
- Contact information

**Form URL:** [Case 1 - Loan Origination](https://vpbank-shared-form-fastdeploy.vercel.app/)

---

### 2. CRM Customer Update Workflow

![CRM Customer Update Workflow](/docs/images/image-5.png)

**Purpose:** Update customer relationship management data

**Workflow Steps:**

1. **Client Side** - Customer Service Officer provides voice input
2. **Audio Processing** - Noise Canceling → Voice Activity Detector → Audio Turn Detector → STT Model
3. **LangGraph Coordination** - Supervisor Agent routes to CRM Agent
4. **Processing Agents** - CRM Agent validates and updates customer data
5. **Decision Layer** - Decision Synthesis → Consensus Builder → Final Decision → Browser-use Agent
6. **Output Layer** - CRM Web updated → TTS Model responds → Audit Trail → Customer Service Officer

**Form Fields:**
- Customer ID lookup
- Contact details (address, phone, email)
- Relationship status
- Communication preferences

**Form URL:** [Case 2 - CRM Updates](https://case2-ten.vercel.app/)

---

### 3. HR Form Workflow

![HR Form Workflow](/docs/images/image-6.png)

**Purpose:** Manage employee data and HR operations

**Workflow Steps:**

1. **Client Side** - HR Officer provides employee information via voice
2. **Audio Processing** - Noise Canceling → Voice Activity Detector → Audio Turn Detector → STT Model
3. **LangGraph Coordination** - Supervisor Agent routes to HR Agent
4. **Processing Agents** - HR Agent processes employee data
5. **Decision Layer** - Decision Synthesis → Consensus Builder → Final Decision → Browser-use Agent
6. **Output Layer** - HR Form filled → TTS Model responds → Audit Trail → HR Office

**Form Fields:**
- Employee information (name, DOB, ID)
- Position and department
- Employment terms (start date, contract type)
- Compensation details

**Form URL:** [Case 3 - HR Workflows](https://case3-seven.vercel.app/)

---

### 4. Compliance Validation Workflow

![Compliance Validation Workflow](/docs/images/image-7.png)

**Purpose:** Submit regulatory compliance forms

**Workflow Steps:**

1. **Client Side** - Compliance Officer provides report details via voice
2. **Audio Processing** - Noise Canceling → Voice Activity Detector → Audio Turn Detector → STT Model
3. **Strands Coordination Layer** - Agent Registry → Supervisor Agent → Context Manager
4. **Processing Agents** - Compliance Validation Agent accesses Internal Bank Document and External Document
5. **Decision Layer** - Decision Synthesis → Consensus Builder → Final Decision → Browser-use Agent
6. **Output Layer** - Banking Form submitted → TTS Model responds → Audit Trail → Compliance Officer

**Form Fields:**
- Reporting period
- Transaction details
- Regulatory checkpoints
- Supporting documentation

**Form URL:** [Case 4 - Compliance Reporting](https://case4-beta.vercel.app/)

---

## Cost Breakdown

### Monthly Infrastructure Costs

The system is deployed on AWS with the following cost structure:

| Service Name | Monthly Cost | Properties |
|-------------|--------------|------------|
| **Amazon CloudFront** | $9.30 | Data transfer out to internet: 50 GB/month<br>Data transfer out to origin: 50 GB/month<br>HTTP requests: 250,000/month |
| **AWS Fargate** | $24.03 | Average duration: 2 hours<br>Tasks per day: 2 |
| **Workload 1** | $60.05 | Average requests per minute: 3 hours/day<br>Average input tokens per request: 500<br>Average output tokens per request: 1,500 |
| **Application Load Balancer** | $35.04 | Number of load balancers: 1 |
| **Amazon API Gateway** | $0.02 | HTTP API requests: millions<br>Average request size: 34 KB<br>Requests: 20,000/month |
| **S3 Standard** | $0.23 | S3 Standard storage: 10 GB/month |
| **NAT Gateway** | $35.10 | Number of NAT Gateways: 1 |
| **Amazon CloudWatch** | $25.23 | Standard Logs: Data ingested: 50 GB |
| **Amazon Elastic Container Registry** | $2.00 | Data stored: 20 GB/month |
| **Amazon Cognito** | $7.50 | Monthly active users (MAU): 100 |
| **Self-hosted Vector Database (pgvector)** | Free | Stores and retrieves vector embeddings<br>Self-hosted in AWS Fargate |
| **TOTAL** | **$198.50** | Estimated monthly cost for moderate usage |

---

## Team

**Pipekat Lodikat** - VPBank Tech Hack 2025

| Name | GitHub |
|------|--------|
| Bùi Hồ Ngọc Hân | [@lodi-bui](https://github.com/lodi-bui) |
| Phạm Nguyễn Hải Anh | [@PNg-HA](https://github.com/PNg-HA) |
| Lê Minh Nghĩa | [@minhnghia2k3](https://github.com/minhnghia2k3) |
| Nguyễn Đức Toàn | [@toannd021104](https://github.com/toannd021104) |
| Danh Hoàng Hiếu Nghị | [@ihatesea69](https://github.com/ihatesea69) |

---

## Acknowledgments

**Core Technologies:**
- [Pipecat AI](https://www.pipecat.ai/) - Voice conversation framework
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - Claude Sonnet 4 LLM
- [browser-use](https://github.com/browser-use/browser-use) - AI browser automation
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Multi-agent orchestration
- [Playwright](https://playwright.dev/) - Browser control
- [React](https://react.dev/) - Frontend framework

**AI Services:**
- [Anthropic Claude](https://www.anthropic.com/) - Natural language understanding
- [PhoWhisper](https://github.com/VinAIResearch/PhoWhisper) - Vietnamese STT
- [OpenAI GPT-4](https://openai.com/) - Browser automation planning
- [ElevenLabs](https://elevenlabs.io/) - Vietnamese TTS

**Special Thanks:**
- VPBank for Tech Hack 2025 opportunity
- AWS for Bedrock infrastructure
- Open-source community

---

**License:** MIT | **Built by:** Pipekat Lodikat | **For:** VPBank Tech Hack 2025

For issues or questions: [GitHub Issues](https://github.com/pipekat-lodikat/speak-to-input/issues)
