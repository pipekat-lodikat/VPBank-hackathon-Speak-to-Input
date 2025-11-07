# API Documentation

VPBank Voice Agent - Complete API Reference for all services

## Table of Contents

- [Overview](#overview)
- [Service Architecture](#service-architecture)
- [Voice Bot Service APIs](#voice-bot-service-apis)
- [Browser Agent Service APIs](#browser-agent-service-apis)
- [WebSocket Connections](#websocket-connections)
- [Authentication APIs](#authentication-apis)
- [Session Management APIs](#session-management-apis)
- [Monitoring APIs](#monitoring-apis)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Overview

The VPBank Voice Agent system consists of three main services:

1. **Voice Bot Service** (Port 7860): WebRTC audio, STT, TTS, LLM conversation
2. **Browser Agent Service** (Port 7863): AI-powered browser automation
3. **Frontend** (Port 5173): React UI with WebRTC voice interface

All APIs use JSON format for request/response bodies unless otherwise specified.

---

## Service Architecture

```
Frontend (5173)
    ↓ WebRTC Audio
    ↓ WebSocket (Transcripts)
Voice Bot (7860)
    ↓ HTTP POST
Browser Agent (7863)
```

**Base URLs:**
- Voice Bot: `http://localhost:7860` or `http://<server-ip>:7860`
- Browser Agent: `http://localhost:7863` or `http://<server-ip>:7863`

---

## Voice Bot Service APIs

Base URL: `http://localhost:7860`

### POST /offer

Create WebRTC connection for voice communication.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "sdp": "v=0\r\no=- ...",
  "type": "offer"
}
```

**Response (200 OK):**
```json
{
  "sdp": "v=0\r\no=- ...",
  "type": "answer"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid offer"
}
```

**Response (429 Too Many Requests):**
```json
{
  "error": "Rate limit exceeded. Please wait X seconds."
}
```

**Description:**
- Establishes WebRTC peer connection for bidirectional audio streaming
- Initiates voice bot pipeline (STT → LLM → TTS)
- Returns SDP answer for WebRTC negotiation
- Rate limited: 10 requests per minute per IP

**Example:**
```javascript
const response = await fetch('http://localhost:7860/offer', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sdp: localDescription.sdp,
    type: 'offer'
  })
});
const answer = await response.json();
```

---

### GET /ws

WebSocket endpoint for real-time transcript streaming.

**Protocol:** WebSocket (ws://)

**Connection URL:**
```
ws://localhost:7860/ws
```

**Messages Received (Server → Client):**

**1. Transcript Message:**
```json
{
  "type": "transcript",
  "message": {
    "role": "user" | "assistant",
    "content": "Transcribed text or bot response",
    "timestamp": "2025-11-07T10:30:45.123Z"
  }
}
```

**2. Task Completion:**
```json
{
  "type": "task_completed",
  "result": "Form filled successfully",
  "message": "✅ Form filled successfully"
}
```

**3. Task Failed:**
```json
{
  "type": "task_failed",
  "error": "Error message",
  "message": "❌ Error: ..."
}
```

**Description:**
- Streams conversation transcripts in real-time
- Sends notifications when browser automation completes
- Auto-reconnects on connection loss

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:7860/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'transcript') {
    console.log(`[${data.message.role}]: ${data.message.content}`);
  }
};
```

---

### GET /metrics

Prometheus metrics endpoint for monitoring.

**Response (200 OK):**
```
# HELP webrtc_connections_total Total WebRTC connections
# TYPE webrtc_connections_total counter
webrtc_connections_total 42

# HELP webrtc_active_connections Active WebRTC connections
# TYPE webrtc_active_connections gauge
webrtc_active_connections 3

# HELP sessions_total Total sessions created
# TYPE sessions_total counter
sessions_total 38
```

**Content-Type:** `text/plain; version=0.0.4`

**Description:**
- Exposes metrics for Prometheus scraping
- Tracks WebRTC connections, sessions, auth requests
- Used for monitoring and alerting

---

## Browser Agent Service APIs

Base URL: `http://localhost:7863`

### POST /api/execute

Execute browser automation workflow.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_message": "Full conversation context including user instructions",
  "session_id": "session_20251107_103045"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "result": "Form filled successfully with customer data",
  "session_id": "session_20251107_103045"
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "user_message is required"
}
```

**Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": "Browser automation failed: ..."
}
```

**Description:**
- Executes AI-powered browser automation using OpenAI GPT-4
- Supports incremental form filling and one-shot form filling
- Handles 5 form types: Loan, CRM, HR, Compliance, Operations
- Timeout: 300 seconds (5 minutes)

**Form URLs:**
- Loan: `https://vpbank-shared-form-fastdeploy.vercel.app/`
- CRM: `https://case2-ten.vercel.app/`
- HR: `https://case3-seven.vercel.app/`
- Compliance: `https://case4-beta.vercel.app/`
- Operations: `https://case5-chi.vercel.app/`

**Example:**
```javascript
const response = await fetch('http://localhost:7863/api/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_message: "Tạo đơn vay cho khách hàng Nguyễn Văn An, CCCD 012345678901, vay 500 triệu",
    session_id: "session_20251107_103045"
  })
});
const result = await response.json();
```

---

### GET /api/health

Health check endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "browser-agent-service"
}
```

**Description:**
- Simple health check to verify service is running
- Returns immediately without heavy operations

---

### GET /api/live

Get current live browser URL (for monitoring).

**Response (200 OK):**
```json
{
  "live_url": "https://browser.events.browser-use.com/view/abc123def456"
}
```

**Response (200 OK - No active browser):**
```json
{
  "live_url": null
}
```

**Response (500 Internal Server Error):**
```json
{
  "live_url": null,
  "error": "Error message"
}
```

**Description:**
- Returns live browser view URL if available
- Used for debugging and monitoring browser sessions
- Only available when browser is active

---

## WebSocket Connections

### Voice Bot WebSocket (`/ws`)

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:7860/ws');
```

**Message Types:**

#### 1. Transcript Update
```json
{
  "type": "transcript",
  "message": {
    "role": "user",
    "content": "Tôi muốn vay 500 triệu",
    "timestamp": "2025-11-07T10:30:45.123Z"
  }
}
```

#### 2. Task Completed
```json
{
  "type": "task_completed",
  "result": "Đã điền thành công form đơn vay",
  "message": "✅ Đã điền thành công form đơn vay"
}
```

#### 3. Task Failed
```json
{
  "type": "task_failed",
  "error": "Timeout",
  "message": "❌ Browser Service không phản hồi (timeout)"
}
```

**Connection Management:**
- Auto-reconnect on disconnect
- Keep-alive ping/pong every 30 seconds
- Multiple clients can connect simultaneously

---

## Authentication APIs

Base URL: `http://localhost:7860`

All auth endpoints support CORS with `Access-Control-Allow-Origin: *`.

### POST /api/auth/login

Authenticate user with AWS Cognito.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "tokens": {
    "accessToken": "eyJraWQiOiJ...",
    "idToken": "eyJraWQiOiJ...",
    "refreshToken": "eyJjdHkiOiJ..."
  },
  "user": {
    "username": "user@example.com",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Incorrect username or password"
}
```

**Response (429 Too Many Requests):**
```json
{
  "success": false,
  "error": "Too many login attempts. Please wait X seconds."
}
```

**Rate Limits:**
- 5 login attempts per minute per IP
- Locked for 60 seconds after exceeding limit

---

### POST /api/auth/verify

Verify JWT access token.

**Request Body:**
```json
{
  "token": "eyJraWQiOiJ..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "username": "user@example.com",
    "email": "user@example.com",
    "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid token"
}
```

---

### POST /api/auth/register

Register new user in Cognito.

**Request Body:**
```json
{
  "username": "newuser",
  "password": "SecurePassword123!",
  "email": "newuser@example.com",
  "phone_number": "+84901234567",
  "name": "Nguyen Van A"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "userSub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Username already exists"
}
```

---

### POST /api/auth/forgot-password

Initiate password reset flow.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password reset code sent to your email"
}
```

---

### POST /api/auth/reset-password

Reset password with verification code.

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "NewSecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid verification code"
}
```

---

## Session Management APIs

Base URL: `http://localhost:7860`

### GET /api/sessions

List all conversation sessions from DynamoDB.

**Query Parameters:**
- `limit` (optional): Number of sessions to return (default: 50, max: 100)
- `last_key` (optional): Pagination key (JSON string from previous response)

**Response (200 OK):**
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "20251107_103045",
      "started_at": "2025-11-07T10:30:45.123Z",
      "ended_at": "2025-11-07T10:35:12.456Z",
      "messages": [
        {
          "role": "user",
          "content": "Tôi muốn vay 500 triệu",
          "timestamp": "2025-11-07T10:30:50.123Z"
        },
        {
          "role": "assistant",
          "content": "Dạ, tôi đã ghi nhận: 500 triệu. Đang xử lý...",
          "timestamp": "2025-11-07T10:30:52.456Z"
        }
      ],
      "workflow_executions": []
    }
  ],
  "count": 1,
  "last_evaluated_key": null
}
```

**Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": "Failed to list sessions: ..."
}
```

---

### GET /api/sessions/{session_id}

Get details of a specific session.

**Path Parameters:**
- `session_id`: Session identifier (e.g., "20251107_103045")

**Response (200 OK):**
```json
{
  "success": true,
  "session": {
    "session_id": "20251107_103045",
    "started_at": "2025-11-07T10:30:45.123Z",
    "ended_at": "2025-11-07T10:35:12.456Z",
    "messages": [...],
    "workflow_executions": [...]
  }
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Session not found"
}
```

---

## Monitoring APIs

### GET /metrics (Voice Bot)

Prometheus-compatible metrics endpoint.

**Response (200 OK):**
```
# HELP webrtc_connections_total Total WebRTC connections created
# TYPE webrtc_connections_total counter
webrtc_connections_total 42

# HELP webrtc_active_connections Currently active WebRTC connections
# TYPE webrtc_active_connections gauge
webrtc_active_connections 3

# HELP sessions_total Total conversation sessions created
# TYPE sessions_total counter
sessions_total 38

# HELP auth_requests_total Total authentication requests
# TYPE auth_requests_total counter
auth_requests_total{status="success"} 25
auth_requests_total{status="failure"} 3

# HELP operation_duration_seconds Duration of operations in seconds
# TYPE operation_duration_seconds histogram
operation_duration_seconds_bucket{operation="login",le="0.5"} 20
operation_duration_seconds_bucket{operation="login",le="1.0"} 25
operation_duration_seconds_sum{operation="login"} 18.5
operation_duration_seconds_count{operation="login"} 25
```

**Content-Type:** `text/plain; version=0.0.4`

**Metrics Available:**
- `webrtc_connections_total`: Counter - Total WebRTC connections
- `webrtc_active_connections`: Gauge - Active connections
- `sessions_total`: Counter - Total sessions
- `auth_requests_total`: Counter (labeled by status) - Auth requests
- `operation_duration_seconds`: Histogram - Operation durations

---

## Error Handling

All APIs follow consistent error response format:

### Standard Error Response

```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

### HTTP Status Codes

- **200 OK**: Request succeeded
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication failed
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server-side error

### Common Error Messages

**Voice Bot:**
- `"Invalid offer"`: WebRTC SDP offer is malformed
- `"Rate limit exceeded. Please wait X seconds."`: Too many requests
- `"Session not found"`: Session ID doesn't exist
- `"Missing credentials"`: Username or password not provided

**Browser Agent:**
- `"user_message is required"`: Request body missing user_message
- `"Browser automation failed: ..."`: Browser operation error
- `"Timeout"`: Operation exceeded 5 minute timeout

**Authentication:**
- `"Incorrect username or password"`: Invalid credentials
- `"Username already exists"`: Registration conflict
- `"Invalid token"`: JWT token expired or malformed
- `"Invalid verification code"`: Password reset code incorrect

---

## Rate Limiting

Rate limits protect services from abuse and ensure fair usage.

### Voice Bot Rate Limits

**WebRTC Offers (`POST /offer`):**
- Limit: 10 requests per minute per IP
- Window: 60 seconds sliding window
- Response: 429 with wait time

**Auth Login (`POST /api/auth/login`):**
- Limit: 5 requests per minute per IP
- Window: 60 seconds sliding window
- Lockout: 60 seconds after exceeding limit
- Response: 429 with wait time

### Rate Limit Response

```json
{
  "success": false,
  "error": "Rate limit exceeded. Please wait 45 seconds."
}
```

**Headers:**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 45
```

### Best Practices

1. **Implement exponential backoff** when retrying failed requests
2. **Cache authentication tokens** instead of re-authenticating frequently
3. **Reuse WebRTC connections** instead of creating new ones
4. **Handle 429 responses gracefully** with retry logic

---

## CORS Configuration

All API endpoints support Cross-Origin Resource Sharing (CORS):

**Allowed Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

**Preflight Requests:**
All endpoints support `OPTIONS` method for CORS preflight.

Example preflight:
```
OPTIONS /api/auth/login HTTP/1.1
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
```

Response:
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## WebRTC Configuration

### ICE Servers

The Voice Bot uses the following ICE servers for NAT traversal:

```javascript
[
  {
    urls: "stun:stun.l.google.com:19302"
  },
  {
    urls: "turn:openrelay.metered.ca:80",
    username: "openrelayproject",
    credential: "openrelayproject"
  }
]
```

### Media Constraints

**Audio:**
- Sample rate: 16 kHz (AWS Transcribe requirement)
- Channels: 1 (mono)
- Echo cancellation: Enabled
- Noise suppression: Enabled

---

## Security Considerations

### Authentication
- All passwords hashed with AWS Cognito (bcrypt)
- JWT tokens expire after 1 hour
- Refresh tokens valid for 30 days
- PII data masked in logs using regex patterns

### Rate Limiting
- IP-based rate limiting on auth and WebRTC endpoints
- Configurable limits per endpoint
- Automatic lockout on repeated failures

### Data Protection
- Session data encrypted in DynamoDB
- WebRTC media encrypted (DTLS-SRTP)
- HTTPS recommended for production
- Environment variables for secrets

### Network Security
- CORS enabled for frontend access
- AWS Security Groups for EC2 instances
- UDP ports for WebRTC media (49152-65535)

---

## Integration Examples

### JavaScript/TypeScript (Frontend)

```javascript
// 1. WebRTC Connection
const pc = new RTCPeerConnection({
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' }
  ]
});

const offer = await pc.createOffer();
await pc.setLocalDescription(offer);

const response = await fetch('http://localhost:7860/offer', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(offer)
});
const answer = await response.json();
await pc.setRemoteDescription(answer);

// 2. WebSocket Transcript
const ws = new WebSocket('ws://localhost:7860/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Transcript:', data);
};

// 3. Authentication
const loginResponse = await fetch('http://localhost:7860/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password123'
  })
});
const { tokens } = await loginResponse.json();
```

### Python (Backend Integration)

```python
import aiohttp
import asyncio

async def execute_workflow(user_message: str, session_id: str):
    """Execute browser workflow"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:7863/api/execute',
            json={
                'user_message': user_message,
                'session_id': session_id
            },
            timeout=aiohttp.ClientTimeout(total=300)
        ) as response:
            result = await response.json()
            return result

# Usage
result = await execute_workflow(
    "Tạo đơn vay 500 triệu cho Nguyễn Văn An",
    "session_123"
)
print(result['result'])
```

### cURL (Testing)

```bash
# WebRTC Offer (requires valid SDP)
curl -X POST http://localhost:7860/offer \
  -H "Content-Type: application/json" \
  -d '{"sdp":"v=0...", "type":"offer"}'

# Browser Execution
curl -X POST http://localhost:7863/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Tạo đơn vay 500 triệu",
    "session_id": "test_session"
  }'

# Health Check
curl http://localhost:7863/api/health

# Authentication
curl -X POST http://localhost:7860/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password123"
  }'

# List Sessions
curl "http://localhost:7860/api/sessions?limit=10"

# Metrics
curl http://localhost:7860/metrics
```

---

## Changelog

### Version 1.0.0 (Current)

**Voice Bot Service:**
- WebRTC voice communication
- Real-time transcript streaming via WebSocket
- AWS Cognito authentication
- DynamoDB session storage
- Prometheus metrics

**Browser Agent Service:**
- AI-powered form automation
- Support for 5 form types
- Incremental and one-shot filling modes
- Live browser URL monitoring
- 5-minute timeout for operations

**Security:**
- Rate limiting on auth and WebRTC endpoints
- PII masking in logs
- JWT token authentication
- CORS support for cross-origin requests

---

## Support

For API issues or questions:
- GitHub Issues: https://github.com/yourusername/vpbank-voice-agent/issues
- Email: support@vpbank.com
- Documentation: https://docs.vpbank.com/voice-agent

---

**Last Updated:** November 7, 2025
**API Version:** 1.0.0
