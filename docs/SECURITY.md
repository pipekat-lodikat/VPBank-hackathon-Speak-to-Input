# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of VPBank Voice Agent seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: buihongochan.lodi@gmail.com

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., XSS, SQL injection, authentication bypass)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it
- Any potential mitigations you've identified

### What to Expect

After you submit a vulnerability report, we will:

1. **Confirm receipt** within 48 hours
2. **Assess the vulnerability** and determine its severity and impact
3. **Develop a fix** for the vulnerability
4. **Release a patch** as soon as possible
5. **Credit you** in the security advisory (if desired)

### Security Update Process

1. Security vulnerability is reported privately
2. Maintainers confirm and assess the issue
3. Fix is developed in a private repository
4. Patch is tested thoroughly
5. Security advisory is prepared
6. Patch is released with security advisory
7. CVE is requested (if applicable)

## Security Best Practices for Contributors

When contributing to this project, please follow these security guidelines:

### General Security

- Never commit sensitive data (API keys, passwords, credentials)
- Use environment variables for all secrets
- Validate and sanitize all user inputs
- Implement proper authentication and authorization
- Use secure communication protocols (HTTPS, WSS)
- Keep dependencies up to date

### Code Security

#### Input Validation

```python
# ✅ Good - Validate and sanitize input
def process_user_input(user_input: str) -> str:
    # Validate input
    if not user_input or len(user_input) > 1000:
        raise ValueError("Invalid input")

    # Sanitize input
    sanitized = html.escape(user_input)
    return sanitized

# ❌ Bad - Direct use without validation
def process_user_input(user_input: str) -> str:
    return user_input
```

#### SQL Injection Prevention

```python
# ✅ Good - Use parameterized queries
def get_user(user_id: str):
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))

# ❌ Bad - String concatenation
def get_user(user_id: str):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

#### XSS Prevention

```typescript
// ✅ Good - Sanitize before rendering
import DOMPurify from 'dompurify';

const SafeComponent = ({ userContent }: { userContent: string }) => {
  const sanitized = DOMPurify.sanitize(userContent);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
};

// ❌ Bad - Direct rendering
const UnsafeComponent = ({ userContent }: { userContent: string }) => {
  return <div dangerouslySetInnerHTML={{ __html: userContent }} />;
};
```

#### Command Injection Prevention

```python
# ✅ Good - Use subprocess with list
import subprocess

def run_command(filename: str):
    # Validate filename
    if not is_valid_filename(filename):
        raise ValueError("Invalid filename")

    # Use list to prevent injection
    subprocess.run(["cat", filename], check=True)

# ❌ Bad - Shell injection vulnerability
def run_command(filename: str):
    os.system(f"cat {filename}")
```

### Authentication & Authorization

- Use AWS Cognito for user authentication
- Implement proper session management
- Use secure session tokens
- Implement rate limiting
- Use HTTPS for all API communications
- Validate JWT tokens properly

```python
# ✅ Good - Verify JWT token
from jose import jwt, JWTError

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience="your-client-id"
        )
        return payload
    except JWTError:
        raise UnauthorizedError("Invalid token")
```

### Data Protection

- Encrypt sensitive data at rest
- Use TLS/SSL for data in transit
- Implement proper key management
- Follow AWS security best practices
- Implement data retention policies
- Securely delete sensitive data when no longer needed

### Dependencies

- Regularly update dependencies
- Use `pip audit` or `npm audit` to check for vulnerabilities
- Pin dependency versions in production
- Review security advisories for dependencies
- Use dependabot or similar tools for automated updates

```bash
# Check Python dependencies for vulnerabilities
pip install pip-audit
pip-audit

# Check npm dependencies for vulnerabilities
npm audit

# Fix vulnerabilities automatically
npm audit fix
```

### Environment Variables

```bash
# ✅ Good - Use .env file (never commit to git)
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here

# Add .env to .gitignore
echo ".env" >> .gitignore
```

### AWS Security

- Use IAM roles with least privilege principle
- Enable MFA for AWS accounts
- Use AWS Secrets Manager for sensitive data
- Enable CloudTrail for audit logging
- Implement proper VPC security groups
- Use AWS WAF for application protection
- Enable S3 bucket encryption
- Review AWS Security Hub recommendations

### WebRTC Security

- Implement proper STUN/TURN server authentication
- Use secure WebSocket connections (WSS)
- Validate WebRTC signaling messages
- Implement proper CORS policies
- Use encrypted media streams

## Known Security Considerations

### Current Implementation

1. **Authentication:** AWS Cognito with JWT tokens
2. **Data Storage:** AWS DynamoDB with encryption at rest
3. **API Security:** Rate limiting and input validation
4. **WebRTC:** Secure signaling via WSS
5. **Browser Automation:** Sandboxed Playwright execution

### Areas of Ongoing Improvement

- Enhanced rate limiting
- Additional input validation
- Security monitoring and alerting
- Automated security testing
- Penetration testing

## Security Checklist for Deployments

Before deploying to production:

- [ ] All secrets in environment variables (not in code)
- [ ] HTTPS/WSS enabled for all communications
- [ ] AWS security groups configured properly
- [ ] Database encryption enabled
- [ ] Backup and disaster recovery plan in place
- [ ] Security monitoring and alerting configured
- [ ] Dependencies updated to latest secure versions
- [ ] Security audit completed
- [ ] Penetration testing performed (if applicable)
- [ ] Incident response plan documented

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [Python Security Guidelines](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [WebRTC Security Architecture](https://www.w3.org/TR/webrtc-security/)

## Disclosure Policy

We believe in responsible disclosure and will work with security researchers to address vulnerabilities quickly and responsibly.

### Our Commitment

- We will respond to security reports within 48 hours
- We will provide regular updates on our progress
- We will credit researchers who report vulnerabilities (if desired)
- We will not take legal action against researchers who follow this policy

### Researcher Guidelines

- Do not access or modify user data beyond what is necessary to demonstrate the vulnerability
- Do not perform destructive testing (DoS, spam, etc.)
- Do not publicly disclose the vulnerability before we've had a chance to fix it
- Make a good faith effort to avoid privacy violations and disruption to our services

## Security Hall of Fame

We recognize and thank security researchers who have helped make VPBank Voice Agent more secure:

<!-- Contributors will be listed here -->

## Contact

For security concerns, please contact: buihongochan.lodi@gmail.com

For general questions, please use GitHub issues or discussions.

---

Last updated: 2025-01-09
