# API Documentation

**Base URL**: `http://localhost:7860`

---

## Endpoints

### 1. GET /

**200 OK**
```
VP Bank Sheets Filling Voice Agent is running! Use React UI to connect.
```

---

### 2. POST /offer

**Request Body**
```json
{
  "type": "offer",
  "sdp": "v=0\r\no=- 123456789..."
}
```

**200 OK**
```json
{
  "type": "answer",
  "sdp": "v=0\r\no=- 987654321..."
}
```

**400 BAD REQUEST**
```json
{
  "error": "Request body is empty"
}
```

```json
{
  "error": "Invalid JSON: <details>"
}
```

```json
{
  "error": "Invalid offer structure. Need 'sdp' and 'type' fields"
}
```

**500 INTERNAL SERVER ERROR**
```json
{
  "error": "<error_message>"
}
```

---

### 3. OPTIONS /offer

**200 OK** (CORS preflight)

---

### 4. GET /ws (WebSocket)

**Server → Client**
```json
{
  "type": "transcript",
  "message": {
    "role": "user",
    "content": "Tên tôi là Nguyễn Văn A",
    "timestamp": "2025-10-26T10:30:45.123Z"
  }
}
```

```json
{
  "type": "transcript",
  "message": {
    "role": "assistant",
    "content": "Dạ em đã lưu tên 'Nguyễn Văn A' rồi ạ.",
    "timestamp": "2025-10-26T10:30:46.456Z"
  }
}
```
