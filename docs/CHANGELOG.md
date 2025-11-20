# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- MIT License
- Code of Conduct (Contributor Covenant 2.0)
- Contributing Guidelines
- Security Policy
- GitHub Issue Templates (Bug Report, Feature Request)
- Pull Request Template
- Citation file (CITATION.cff)
- Changelog file
- README badges and improved documentation

## [1.0.0] - 2025-01-09

### Added

#### Core Features
- Voice-powered banking form automation system
- Microservices architecture with three independent services
- Real-time speech recognition using AWS Transcribe (Vietnamese)
- Natural language understanding with Claude Sonnet 4 (AWS Bedrock)
- AI-powered browser automation using browser-use + GPT-4
- Text-to-speech using ElevenLabs (Vietnamese voice)
- WebRTC bidirectional audio streaming
- Real-time transcript streaming via WebSocket
- Session management with AWS DynamoDB
- User authentication via AWS Cognito

#### Services
- **Voice Bot Service** (Port 7860)
  - Pipecat AI framework for WebRTC/Voice pipeline
  - AWS Transcribe STT integration
  - AWS Bedrock Claude Sonnet 4 LLM
  - ElevenLabs TTS integration
  - Silero VAD for voice activity detection
  - HTTP client for Browser Agent communication

- **Browser Agent Service** (Port 7863)
  - aiohttp async HTTP server
  - browser-use library (v0.9.5) integration
  - Playwright browser automation
  - OpenAI GPT-4 for form filling intelligence
  - Session-aware multi-turn form filling

- **Frontend** (Port 5173)
  - React 19.1.1 with TypeScript 5.8.3
  - Vite 7.1.2 build system
  - Pipecat React UI Kit for WebRTC interface
  - TailwindCSS 4.1.13 for styling
  - Dynamic API URL detection for local/remote access
  - Real-time transcript display

#### Infrastructure
- Terraform configurations for AWS ECS deployment
- VPC with public/private subnets
- Application Load Balancer
- Auto-scaling policies
- CloudWatch monitoring
- Docker Compose orchestration
- Multi-region deployment support

#### Security Features
- PII masking in logs and transcripts
- Rate limiting for API endpoints
- Input validation and sanitization
- AWS Cognito authentication
- DynamoDB encrypted session storage
- Security group configurations
- WAF protection

#### Cost Management
- LLM response caching
- Cost tracking and analytics
- Usage monitoring dashboards
- Budget alerts configuration

#### Documentation
- Comprehensive README.md
- Architecture diagrams
- Deployment guides (AWS ECS, Docker)
- API reference documentation
- Troubleshooting guide
- CLAUDE.md for AI assistant guidance
- Five banking use case examples

#### Development Tools
- Deployment scripts (ECS, multi-region)
- Development start/stop scripts
- Health check endpoints
- Debug logging configuration
- Testing utilities

### Banking Use Cases

1. **Loan Origination & KYC** - Customer onboarding and loan applications
2. **CRM Updates** - Customer relationship management
3. **HR Workflows** - Employee data management
4. **Compliance Reporting** - Regulatory form submission
5. **Operations Validation** - Data verification

### Technical Stack

#### Backend
- Python 3.11
- Pipecat AI 0.0.91
- AWS Transcribe
- AWS Bedrock (Claude Sonnet 4)
- ElevenLabs API
- browser-use 0.9.5
- Playwright 1.55.0
- OpenAI API (GPT-4)
- LangChain & LangGraph
- aiohttp 3.12.15

#### Frontend
- React 19.1.1
- Vite 7.1.2
- TypeScript 5.8.3
- TailwindCSS 4.1.13
- Pipecat React UI Kit

#### AWS Services
- Transcribe (STT)
- Bedrock (LLM)
- Cognito (Auth)
- DynamoDB (Sessions)
- ECS Fargate (Compute)
- ALB (Load Balancing)
- ECR (Container Registry)
- CloudWatch (Monitoring)

### Fixed
- Service startup order dependencies
- WebRTC connection timeout issues on remote access
- Frontend API URL detection for remote deployments
- Browser automation retry logic
- Error handling and recovery mechanisms
- Security group configurations for WebRTC

### Changed
- Migrated from ALB to NLB for better WebRTC support
- Optimized browser automation speed
- Improved logging and monitoring
- Enhanced security measures
- Refactored cost tracking system

### Security
- Implemented PII masking
- Added rate limiting
- Enhanced input validation
- Configured AWS WAF
- Set up security monitoring

## Release Notes

### Version 1.0.0 - Initial Release

This is the first production-ready release of VPBank Voice Agent, developed for VPBank Tech Hack 2025. The system provides complete voice-powered form automation for five critical banking use cases.

**Key Highlights:**
- Full Vietnamese language support
- Enterprise-grade microservices architecture
- Production deployment on AWS ECS
- Comprehensive security and monitoring
- Cost-optimized operations

**Known Limitations:**
- Requires Python 3.11 (not 3.12 or 3.13)
- Browser automation requires stable internet connection
- WebRTC requires UDP ports open for remote access
- Initial cold start may take 10-15 seconds

**Migration Notes:**
- First release - no migration required

---

## Version Guidelines

### Version Numbers
We use Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

### Categories
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes/improvements

### Links
[Unreleased]: https://github.com/pipekat-lodikat/speak-to-input/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/pipekat-lodikat/speak-to-input/releases/tag/v1.0.0
