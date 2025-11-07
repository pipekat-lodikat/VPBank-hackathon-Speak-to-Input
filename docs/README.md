# VPBank Voice Agent - Documentation

Welcome to the VPBank Voice Agent documentation. This folder contains comprehensive guides for users, developers, and architects.

## Documentation Index

### 1. [API Documentation](./API_DOCUMENTATION.md)
**For:** Frontend/Backend Developers, API Consumers

Complete API reference for all services:
- Voice Bot Service APIs (WebRTC, WebSocket, Auth, Sessions)
- Browser Agent Service APIs (Form automation)
- Request/Response formats
- Error handling
- Rate limiting
- Integration examples

**Key Topics:**
- REST API endpoints
- WebSocket connections
- Authentication flow
- Session management
- Monitoring & metrics

---

### 2. [User Guide](./USER_GUIDE.md)
**For:** End Users, Customer Support

Step-by-step guide for using the voice-powered banking system:
- Getting started
- Voice command examples
- Supported form types (5 types)
- Best practices for voice recognition
- Troubleshooting
- FAQ

**Key Topics:**
- ONE-SHOT vs INCREMENTAL modes
- Voice command reference
- Pronunciation guide (Vietnamese)
- Common issues & solutions

---

### 3. [Developer Guide](./DEVELOPER_GUIDE.md)
**For:** Software Engineers, DevOps

Comprehensive guide for developers working on the codebase:
- Development environment setup
- Project structure
- Backend development (Python)
- Frontend development (React/TypeScript)
- Testing strategies
- Debugging techniques
- Deployment guides
- CI/CD pipeline

**Key Topics:**
- Adding new form types
- Modifying LLM behavior
- Creating React components
- Docker deployment
- AWS EC2 deployment

---

### 4. [Architecture Documentation](./ARCHITECTURE.md)
**For:** Architects, Senior Engineers, Tech Leads

System architecture and technical design:
- High-level architecture diagrams
- Component architecture
- Data flow diagrams
- Technology stack & rationale
- Design patterns
- Scalability strategies
- Security architecture
- Technical decisions (ADRs)

**Key Topics:**
- Microservices architecture
- Voice processing pipeline
- Browser automation stack
- AWS integration
- Performance optimization

---

## Quick Start

**For Users:**
1. Read [Getting Started](./USER_GUIDE.md#getting-started) section
2. Learn [Voice Commands](./USER_GUIDE.md#voice-command-examples)
3. Try [ONE-SHOT Mode](./USER_GUIDE.md#1-one-shot-mode-quick-method)

**For Developers:**
1. Setup [Development Environment](./DEVELOPER_GUIDE.md#development-environment-setup)
2. Understand [Project Structure](./DEVELOPER_GUIDE.md#project-structure)
3. Run [Services Locally](./DEVELOPER_GUIDE.md#running-services-locally)

**For Architects:**
1. Review [System Overview](./ARCHITECTURE.md#system-overview)
2. Study [Architecture Diagram](./ARCHITECTURE.md#architecture-diagram)
3. Read [Technical Decisions](./ARCHITECTURE.md#technical-decisions)

---

## Documentation Statistics

| Document | Size | Pages (est.) | Target Audience |
|----------|------|--------------|-----------------|
| API Documentation | 20KB | ~15 | Developers |
| User Guide | 16KB | ~12 | End Users |
| Developer Guide | 36KB | ~27 | Engineers |
| Architecture | 61KB | ~45 | Architects |
| **Total** | **133KB** | **~99** | All |

---

## Document Status

| Document | Version | Last Updated | Status |
|----------|---------|--------------|--------|
| API Documentation | 1.0.0 | Nov 7, 2025 | ✅ Complete |
| User Guide | 1.0.0 | Nov 7, 2025 | ✅ Complete |
| Developer Guide | 1.0.0 | Nov 7, 2025 | ✅ Complete |
| Architecture | 1.0.0 | Nov 7, 2025 | ✅ Complete |

---

## Contributing to Documentation

To update documentation:

1. Edit the appropriate `.md` file in `docs/` folder
2. Follow Markdown best practices
3. Update version number and "Last Updated" date
4. Run markdown linter: `npm run lint:docs` (if configured)
5. Create pull request with clear description

**Style Guide:**
- Use clear, concise language
- Include code examples where helpful
- Add diagrams for complex concepts (ASCII art preferred)
- Keep sections focused and scannable
- Use consistent formatting

---

## Additional Resources

**External Documentation:**
- [Pipecat AI Docs](https://docs.pipecat.ai)
- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [React 19 Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)

**Project Links:**
- Main README: [../README.md](../README.md)
- CLAUDE.md: [../CLAUDE.md](../CLAUDE.md) (AI assistant instructions)
- GitHub Issues: [Report issues](https://github.com/yourusername/vpbank-voice-agent/issues)

---

## Support

For documentation questions or suggestions:
- Email: docs@vpbank.com
- GitHub Issues: [Documentation label](https://github.com/yourusername/vpbank-voice-agent/issues?q=is%3Aissue+label%3Adocumentation)
- Slack: #vpbank-voice-agent-docs (internal)

---

**Last Updated:** November 7, 2025
**Maintained by:** VPBank Engineering Team
