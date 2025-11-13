# 🚀 IMPLEMENTATION PLAN - Fix Critical Gaps

## 🎯 Objective
Đạt 100% yêu cầu đề bài trong 3-4 ngày

## 📋 Missing Features

### 1. File Upload Support ❌ CRITICAL
### 2. Search on Form ⚠️ HIGH  
### 3. Save Draft / Load Draft ⚠️ MEDIUM
### 4. Response Time Optimization ⚠️ MEDIUM

---

## DAY 1: Add File Upload & Search Tools

### Task 1.1: File Upload Tool (4 hours)

**File**: `src/multi_agent/graph/builder.py`

```python
@tool
async def upload_file_to_field(field_name: str, file_description: str = "") -> str:
    """
    Upload file vào field cụ thể (CCCD, hợp đồng, chứng từ)
    
    Args:
        field_name: Tên field upload (e.g., "idCardImage", "contractFile")
        file_description: Mô tả file (optional)
    
    Returns:
        Kết quả upload
    
    Example:
        User: "Upload ảnh CCCD"
        → upload_file_to_field("idCardImage", "Ảnh căn cước công dân")
    """
    global _current_session_id
    logger.info(f"📎 Upload file to field: {field_name}")
    
    if _current_session_id not in browser_agent.sessions:
        return "❌ Không có active session. Hãy start form trước."
    
    session = browser_agent.sessions[_current_session_id]
    agent = session["agent"]
    
    task = f"""
    Locate the file upload field with name or label matching "{field_name}".
    Click the upload button/input to trigger file picker.
    Wait for file to be selected by user (timeout 30s).
    Verify file name appears in the field.
    """
    
    agent.add_new_task(task)
    await agent.run(max_steps=5)
    
    return f"✅ Đã upload file vào field {field_name}"
```


### Task 1.2: Search Tool (3 hours)

```python
@tool
async def search_and_focus_field(search_query: str) -> str:
    """
    Tìm kiếm field trên form theo tên/label và focus vào field đầu tiên
    
    Args:
        search_query: Từ khóa tìm kiếm (e.g., "số điện thoại", "email", "địa chỉ")
    
    Returns:
        Kết quả tìm kiếm và focus
    
    Example:
        User: "Tìm field số điện thoại"
        → search_and_focus_field("số điện thoại")
    """
    global _current_session_id
    logger.info(f"🔍 Search field: {search_query}")
    
    if _current_session_id not in browser_agent.sessions:
        return "❌ Không có active session."
    
    session = browser_agent.sessions[_current_session_id]
    agent = session["agent"]
    
    task = f"""
    Search for input fields with label, placeholder, or name containing "{search_query}".
    List all matching fields found.
    Focus on the first matching field (scroll into view and highlight).
    Return the field name and label.
    """
    
    agent.add_new_task(task)
    await agent.run(max_steps=4)
    
    return f"✅ Đã tìm và focus vào field: {search_query}"
```

### Task 1.3: Update Supervisor Prompt (1 hour)

Add new tools to supervisor system prompt:

```python
# In build_supervisor_workflow()

tools = [
    # ... existing tools ...
    upload_file_to_field,  # NEW
    search_and_focus_field,  # NEW
]

# Update system prompt
supervisor_system_prompt = """
...
NEW TOOLS:
- upload_file_to_field(field_name, file_description): Upload file
- search_and_focus_field(search_query): Tìm và focus field

EXAMPLES:
- "Upload ảnh CCCD" → upload_file_to_field("idCardImage", "CCCD")
- "Tìm số điện thoại" → search_and_focus_field("số điện thoại")
"""
```

---

## DAY 2: Add Draft Management

### Task 2.1: Draft Save/Load Tools (4 hours)

```python
@tool
async def save_form_draft(draft_name: str = None) -> str:
    """
    Lưu nháp form hiện tại để tiếp tục sau
    
    Args:
        draft_name: Tên bản nháp (optional, auto-generate nếu không có)
    
    Returns:
        Kết quả lưu nháp
    """
    global _current_session_id
    from datetime import datetime
    
    if _current_session_id not in browser_agent.sessions:
        return "❌ Không có active session."
    
    session = browser_agent.sessions[_current_session_id]
    session_data = session["session_data"]
    
    # Auto-generate draft name if not provided
    if not draft_name:
        draft_name = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Save to DynamoDB with status="draft"
    draft_data = {
        "draft_id": draft_name,
        "session_id": _current_session_id,
        "form_type": session_data.get("type"),
        "fields_filled": session_data.get("fields_filled", []),
        "created_at": datetime.now().isoformat(),
        "status": "draft"
    }
    
    dynamodb_service.save_draft(draft_data)
    
    return f"✅ Đã lưu nháp: {draft_name}"


@tool
async def load_form_draft(draft_name: str) -> str:
    """
    Load lại bản nháp đã lưu
    
    Args:
        draft_name: Tên bản nháp cần load
    
    Returns:
        Kết quả load nháp
    """
    global _current_session_id
    
    # Load draft from DynamoDB
    draft_data = dynamodb_service.get_draft(draft_name)
    
    if not draft_data:
        return f"❌ Không tìm thấy bản nháp: {draft_name}"
    
    # Start new session with draft data
    form_type = draft_data.get("form_type")
    form_url = get_form_url(form_type)
    
    result = await browser_agent.start_form_session(form_url, form_type, _current_session_id)
    
    if not result.get("success"):
        return f"❌ Không thể mở form: {result.get('error')}"
    
    # Fill fields from draft
    fields = draft_data.get("fields_filled", [])
    for field in fields:
        await browser_agent.fill_field_incremental(
            field["field"], 
            field["value"], 
            _current_session_id
        )
    
    return f"✅ Đã load nháp: {draft_name} ({len(fields)} fields)"


@tool
async def list_saved_drafts() -> str:
    """
    Liệt kê tất cả bản nháp đã lưu
    
    Returns:
        Danh sách bản nháp
    """
    drafts = dynamodb_service.list_drafts()
    
    if not drafts:
        return "Chưa có bản nháp nào được lưu."
    
    draft_list = "\n".join([
        f"- {d['draft_id']} ({d['form_type']}, {len(d['fields_filled'])} fields)"
        for d in drafts
    ])
    
    return f"Các bản nháp đã lưu:\n{draft_list}"
```

### Task 2.2: DynamoDB Draft Methods (2 hours)

**File**: `src/dynamodb_service.py`

```python
def save_draft(self, draft_data: dict):
    """Save draft to DynamoDB"""
    try:
        self.table.put_item(Item=draft_data)
        logger.info(f"💾 Saved draft: {draft_data['draft_id']}")
    except Exception as e:
        logger.error(f"Error saving draft: {e}")
        raise

def get_draft(self, draft_id: str) -> dict:
    """Get draft from DynamoDB"""
    try:
        response = self.table.get_item(Key={"draft_id": draft_id})
        return response.get("Item")
    except Exception as e:
        logger.error(f"Error getting draft: {e}")
        return None

def list_drafts(self, limit: int = 10) -> list:
    """List all drafts"""
    try:
        response = self.table.query(
            IndexName="status-created_at-index",
            KeyConditionExpression="status = :status",
            ExpressionAttributeValues={":status": "draft"},
            Limit=limit,
            ScanIndexForward=False  # Newest first
        )
        return response.get("Items", [])
    except Exception as e:
        logger.error(f"Error listing drafts: {e}")
        return []
```

---

## DAY 3: Response Time Optimization

### Task 3.1: Integrate LLM Caching (3 hours)

**File**: `src/voice_bot.py`

```python
# Current (line ~328):
llm = AWSBedrockLLMService(...)

# Change to:
from src.cost.llm_cache import llm_cache
from src.monitoring import llm_cache_hits_total, llm_cache_misses_total

class CachedAWSBedrockLLMService(AWSBedrockLLMService):
    """Cached LLM service"""
    
    async def generate(self, prompt, **kwargs):
        temperature = kwargs.get('temperature', 0.0)
        
        # Check cache
        cached = llm_cache.get(prompt, model="claude", temperature=temperature)
        if cached:
            llm_cache_hits_total.labels(cache_type="response").inc()
            return cached
        
        llm_cache_misses_total.labels(cache_type="response").inc()
        
        # Call LLM
        response = await super().generate(prompt, **kwargs)
        
        # Cache response
        llm_cache.put(prompt, response, model="claude", temperature=temperature)
        
        return response

# Use cached LLM
llm = CachedAWSBedrockLLMService(...)
```

### Task 3.2: Parallel Processing (3 hours)

```python
# Process STT and intent detection in parallel

async def process_audio_parallel(audio_chunk):
    # Run STT and VAD in parallel
    stt_task = asyncio.create_task(stt.process(audio_chunk))
    vad_task = asyncio.create_task(vad.analyze(audio_chunk))
    
    text, is_speech = await asyncio.gather(stt_task, vad_task)
    
    return text, is_speech
```

### Task 3.3: Streaming TTS (2 hours)

```python
# Stream TTS chunks instead of waiting for full response

async def stream_tts_response(text: str):
    # Split text into sentences
    sentences = text.split('. ')
    
    for sentence in sentences:
        # Generate TTS for each sentence
        audio_chunk = await tts.synthesize(sentence)
        
        # Stream immediately
        await transport.send_audio(audio_chunk)
```

---

## DAY 4: Testing & Demo Preparation

### Task 4.1: Unit Tests (3 hours)

```python
# tests/test_new_features.py

@pytest.mark.asyncio
async def test_upload_file():
    """Test file upload tool"""
    result = await upload_file_to_field("idCardImage", "CCCD")
    assert "✅" in result

@pytest.mark.asyncio
async def test_search_field():
    """Test search tool"""
    result = await search_and_focus_field("số điện thoại")
    assert "✅" in result

@pytest.mark.asyncio
async def test_save_load_draft():
    """Test draft management"""
    # Save draft
    save_result = await save_form_draft("test_draft")
    assert "✅" in save_result
    
    # Load draft
    load_result = await load_form_draft("test_draft")
    assert "✅" in load_result
```

### Task 4.2: Integration Testing (3 hours)

```bash
# Start all services
./scripts/start-integrated.sh

# Test scenarios
1. Upload file workflow
2. Search and fill workflow
3. Save draft and load workflow
4. Response time measurement
```

### Task 4.3: Demo Script (2 hours)

Create comprehensive demo script covering all features.

---

## 📊 TIMELINE SUMMARY

| Day | Tasks | Hours | Status |
|-----|-------|-------|--------|
| Day 1 | File Upload + Search | 8h | 🔴 TODO |
| Day 2 | Draft Management | 6h | 🔴 TODO |
| Day 3 | Response Time Optimization | 8h | 🔴 TODO |
| Day 4 | Testing + Demo Prep | 8h | 🔴 TODO |
| **Total** | **All Features** | **30h** | **3-4 days** |

---

## ✅ ACCEPTANCE CRITERIA

- [ ] File upload tool working
- [ ] Search tool working
- [ ] Draft save/load working
- [ ] Response time <0.2s (target <0.1s)
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Demo script ready
- [ ] Documentation updated

---

## 🚀 NEXT STEPS

1. **Start Day 1 tasks immediately**
2. **Test each feature as you build**
3. **Update documentation**
4. **Prepare demo**

Ready to implement? 🚀
