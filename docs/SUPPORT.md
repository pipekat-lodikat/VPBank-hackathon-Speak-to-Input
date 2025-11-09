# Support

Thank you for using VPBank Voice Agent! This document provides information on how to get help with the project.

## Getting Help

### Documentation

Before asking for help, please check our documentation:

- **[README.md](README.md)** - Project overview, installation, and usage
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines and technical details
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[docs/](docs/)** - Detailed technical documentation

### Frequently Asked Questions (FAQ)

#### Installation & Setup

**Q: What Python version do I need?**
A: Python 3.11.x is required. Python 3.12 and 3.13 are not compatible due to dependency constraints.

**Q: Why do I get "Module not found" errors?**
A: Ensure your virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

**Q: Playwright browsers are not found?**
A: Install Playwright browsers:
```bash
playwright install chromium
playwright install-deps chromium  # Linux only
```

#### Service Issues

**Q: Services won't start - "Address already in use"?**
A: Kill existing processes:
```bash
lsof -ti:7860,7863,5173 | xargs kill -9
```

**Q: Frontend shows "Network error" or "404 Not Found"?**
A: Ensure services are started in the correct order:
1. Browser Agent (port 7863) - Must start first
2. Voice Bot (port 7860)
3. Frontend (port 5173)

**Q: WebRTC connection timeout on remote access?**
A: Ensure AWS Security Group allows UDP ports:
- 3478 (STUN)
- 49152-65535 (WebRTC media, or restricted range)

#### Environment & Configuration

**Q: Where do I put my API keys?**
A: Create a `.env` file in the project root (NOT in `frontend/`). Use `.env.example` as a template.

**Q: What AWS permissions do I need?**
A: You need permissions for:
- AWS Transcribe (StartStreamTranscription)
- AWS Bedrock (InvokeModel for Claude Sonnet 4)
- AWS Cognito (user authentication)
- AWS DynamoDB (session storage)

#### Development

**Q: How do I run tests?**
A: Run Python tests with pytest:
```bash
pytest tests/
```

**Q: How do I format my code?**
A: Use black for Python and prettier for JavaScript:
```bash
black src/
cd frontend && npm run format
```

## Support Channels

### GitHub Issues

For bug reports and feature requests, please use [GitHub Issues](https://github.com/pipekat-lodikat/speak-to-input/issues).

**Before creating an issue:**
1. Search existing issues to avoid duplicates
2. Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide
3. Review the documentation

**When creating an issue:**
- Use our issue templates
- Provide a clear, descriptive title
- Include reproduction steps for bugs
- Specify your environment (OS, Python version, etc.)
- Include relevant logs or error messages

### GitHub Discussions

For questions, ideas, and general discussions, use [GitHub Discussions](https://github.com/pipekat-lodikat/speak-to-input/discussions).

**Discussion categories:**
- **Q&A**: Ask questions and get help from the community
- **Ideas**: Share and discuss new feature ideas
- **Show and Tell**: Share your projects or use cases
- **General**: General discussions about the project

### Security Issues

**Do NOT report security vulnerabilities in public issues.**

Please report security vulnerabilities privately by:
1. Emailing: buihongochan.lodi@gmail.com
2. Using GitHub Security Advisories

See our [Security Policy](SECURITY.md) for more information.

## Community Guidelines

When seeking support, please:

1. **Be Respectful**: Follow our [Code of Conduct](CODE_OF_CONDUCT.md)
2. **Be Clear**: Provide enough context and details
3. **Be Patient**: Maintainers and contributors are often volunteers
4. **Search First**: Check if your question has been answered before
5. **Give Back**: Help others when you can

## Contributing

Found a bug or want to add a feature? We welcome contributions!

See our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Code style and standards
- Pull request process
- Development workflow
- Testing requirements

## Commercial Support

For commercial support, consulting, or custom development services, please contact:

**Pipekat Lodikat Team**
- Email: buihongochan.lodi@gmail.com
- Team Lead: Bùi Hồ Ngọc Hân

## Response Times

We aim to respond to issues and questions within:

- **Critical bugs**: 24-48 hours
- **Bug reports**: 2-5 days
- **Feature requests**: 1-2 weeks
- **Questions**: 3-7 days

Please note that response times may vary depending on:
- Issue complexity
- Maintainer availability
- Number of open issues

## Helpful Resources

### External Documentation

- [Python Documentation](https://docs.python.org/3.11/)
- [React Documentation](https://react.dev/)
- [Pipecat AI Documentation](https://docs.pipecat.ai/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Transcribe Documentation](https://docs.aws.amazon.com/transcribe/)
- [Playwright Documentation](https://playwright.dev/python/)

### Related Projects

- [browser-use](https://github.com/browser-use/browser-use) - AI browser automation
- [Pipecat AI](https://github.com/pipecat-ai/pipecat) - Real-time voice framework

### Community

- **GitHub Repository**: [github.com/pipekat-lodikat/speak-to-input](https://github.com/pipekat-lodikat/speak-to-input)
- **Documentation**: [/docs](docs/)
- **Issue Tracker**: [GitHub Issues](https://github.com/pipekat-lodikat/speak-to-input/issues)

## Improvement Suggestions

Have suggestions for improving this support document? Please:

1. Open an issue or discussion
2. Submit a pull request with improvements
3. Contact the maintainers

Thank you for using VPBank Voice Agent! 🎉
