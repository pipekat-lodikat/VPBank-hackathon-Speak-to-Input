# Contributing to VPBank Voice Agent

Thank you for your interest in contributing to VPBank Voice Agent! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to buihongochan.lodi@gmail.com.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11.x (required)
- Node.js 18+ and npm
- Git
- AWS Account (for cloud services)
- OpenAI API key
- ElevenLabs API key

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/speak-to-input.git
   cd speak-to-input
   ```

2. **Set up Python environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Set up Frontend:**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run the services:**
   ```bash
   # Terminal 1 - Browser Agent
   python main_browser_service.py

   # Terminal 2 - Voice Bot
   python main_voice.py

   # Terminal 3 - Frontend
   cd frontend
   npm run dev -- --host 0.0.0.0
   ```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- Clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, browser, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- Clear and descriptive title
- Detailed description of the proposed feature
- Rationale for why this enhancement would be useful
- Possible implementation approach (optional)
- Examples or mockups (if applicable)

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:

- `good first issue` - Good for newcomers
- `help wanted` - Issues that need community help
- `bug` - Something isn't working
- `enhancement` - New feature or request

## Coding Standards

### Python Code

- Follow PEP 8 style guide
- Use type hints for function arguments and return values
- Write docstrings for all public functions and classes
- Avoid using `any` or `unknown` types
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Single-responsibility principle for functions

**Example:**
```python
from typing import Dict, List, Optional

async def process_transcript(
    transcript: str,
    session_id: str,
    metadata: Optional[Dict[str, str]] = None
) -> Dict[str, any]:
    """
    Process transcript and extract form data.

    Args:
        transcript: The user's speech transcript
        session_id: Unique session identifier
        metadata: Additional session metadata

    Returns:
        Dictionary containing extracted form data
    """
    # Implementation here
    pass
```

### TypeScript/React Code

- Follow project's ESLint configuration
- Use TypeScript strict mode
- Avoid `any` type - use proper typing
- Prefer functional components with hooks
- Use meaningful component and variable names
- Extract reusable logic into custom hooks

**Example:**
```typescript
interface VoiceSessionProps {
  sessionId: string;
  onTranscriptUpdate: (transcript: string) => void;
}

export const VoiceSession: React.FC<VoiceSessionProps> = ({
  sessionId,
  onTranscriptUpdate
}) => {
  // Implementation here
};
```

### General Principles

- **Security First:** Avoid XSS, SQL injection, command injection
- **No Hard-coding:** Use environment variables and configuration files
- **Error Handling:** Implement comprehensive error handling
- **Logging:** Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- **Performance:** Optimize API responses and database queries
- **Testing:** Write unit and integration tests for new features
- **Documentation:** Update docs when making changes

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without changing functionality
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build, etc.)
- `ci`: CI/CD pipeline changes
- `revert`: Reverting previous commits

### Examples

```bash
feat(voice-bot): add support for multiple languages

- Add language detection
- Update STT service to support Vietnamese and English
- Add language selection in UI

Closes #123

fix(browser-agent): resolve form submission timeout

The browser automation was timing out on slow connections.
Increased timeout and added retry logic.

Fixes #456

docs(readme): update installation instructions

- Add Python 3.11 requirement
- Clarify environment variable setup
- Add troubleshooting section

refactor(auth): simplify Cognito integration

- Extract auth logic into separate service
- Remove duplicate code
- Improve error messages
```

## Pull Request Process

1. **Update your branch:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Ensure all tests pass:**
   ```bash
   # Run Python tests
   pytest

   # Run frontend tests
   cd frontend
   npm test
   ```

3. **Update documentation:**
   - Update README.md if needed
   - Update CHANGELOG.md
   - Add docstrings/comments for new code

4. **Create Pull Request:**
   - Use a clear and descriptive title
   - Reference related issues (e.g., "Fixes #123")
   - Describe your changes in detail
   - Include screenshots for UI changes
   - List breaking changes (if any)

5. **Review Process:**
   - Address review comments promptly
   - Keep discussions professional and constructive
   - Update PR based on feedback
   - Ensure CI/CD checks pass

6. **Merging:**
   - PRs require approval from at least one maintainer
   - All CI/CD checks must pass
   - No merge conflicts
   - Squash commits if requested

## Testing

### Python Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_voice_bot.py

# Run specific test
pytest tests/test_voice_bot.py::test_transcript_processing
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e
```

### Manual Testing

Before submitting PR, manually test:

1. Start all services (Browser Agent → Voice Bot → Frontend)
2. Test voice recording and transcription
3. Test form filling with different scenarios
4. Test error handling and edge cases
5. Check browser console for errors
6. Verify responsive design on different screen sizes

## Documentation

### Code Documentation

- **Python:** Use Google-style docstrings
- **TypeScript:** Use JSDoc comments
- **Complex Logic:** Add inline comments explaining why, not what

### Project Documentation

When adding new features or making significant changes, update:

- `README.md` - User-facing documentation
- `CLAUDE.md` - Development guidelines for AI assistants
- `docs/` - Detailed technical documentation
- `CHANGELOG.md` - Version history

### API Documentation

For new API endpoints, document:

- Endpoint path and method
- Request/response format
- Authentication requirements
- Error codes and messages
- Example requests/responses

## Questions?

If you have questions or need help:

1. Check existing documentation
2. Search existing issues
3. Ask in discussions
4. Create a new issue with `question` label

## License

By contributing to VPBank Voice Agent, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:

- `CONTRIBUTORS.md` file
- Project README
- Release notes

Thank you for contributing! 🎉
