# 📁 src/ - Backend Source Code

**VPBank Multi-Agent System - Core Implementation**

---

## 📊 STRUCTURE

```
src/
├── __init__.py               # Package marker (version 1.0.0)
├── bot_multi_agent.py        # Main WebRTC server + Voice Agent
├── task_queue.py             # Async task queue system
├── workflow_worker.py        # Background worker
├── browser_agent.py          # Browser automation handler
└── multi_agent/
    ├── __init__.py           # Package exports
    └── graph/
        ├── __init__.py       # Graph module exports
        ├── builder.py        # Supervisor workflow + 5 tools
        └── state.py          # LangGraph state definition
```

**Total:** 9 Python files (~1,573 lines)

---

## 📖 FILE DESCRIPTIONS

### 1. `bot_multi_agent.py` (408 lines)
**Purpose:** Main entry point - WebRTC server và Voice Agent

**Key Components:**
- WebRTC offer/answer handling
- Voice pipeline (STT → LLM → TTS)
- Transcript processor
- WebSocket server for frontend
- System prompt cho Voice Agent

**Entry Points:**
- `handle_offer()` - POST /offer
- `websocket_handler()` - GET /ws
- `run_bot()` - Voice pipeline
- `create_app()` - aiohttp app

**Dependencies:**
- Pipecat AI (WebRTC, STT, LLM, TTS)
- Task queue & workflow worker

---

### 2. `task_queue.py` (191 lines)
**Purpose:** Async task queue - decouples Voice Bot from Workflow

**Key Components:**
- `Task` dataclass - task representation
- `TaskType` enum - 5 use case types
- `TaskStatus` enum - lifecycle states
- `TaskQueue` class - queue management

**Public API:**
- `push(task)` - Add task to queue
- `pop()` - Get next task (blocking)
- `get_task(id)` - Lookup by ID
- `update_task(id, status, result)` - Update status
- `get_task_stats()` - Statistics

**Global Instance:**
```python
task_queue = TaskQueue(maxsize=100)
```

---

### 3. `workflow_worker.py` (174 lines)
**Purpose:** Background worker - processes tasks from queue

**Key Components:**
- `WorkflowWorker` class - background processing loop
- Lazy loading for LLM & workflow
- Task processing with error handling

**Lifecycle:**
```python
await worker.start()  # Continuous loop
  └─ while running:
      └─ task = await queue.pop()
      └─ await _process_task(task)
```

**Lazy Loading:**
- LLM loaded once on first task
- Workflow compiled once on first task
- Reused for all subsequent tasks

**Global Instance:**
```python
workflow_worker = WorkflowWorker()
```

---

### 4. `browser_agent.py` (180 lines)
**Purpose:** Browser automation với browser-use + Playwright

**Key Components:**
- `BrowserAgentHandler` class
- Form filling logic
- Task instruction generation

**Public API:**
- `fill_form(url, data, type)` - Fill form at URL
- `run_browser_task(task)` - Generic browser task

**Usage:**
```python
result = await browser_agent.fill_form(
    form_url="http://localhost:5173/vpbank-forms/...",
    form_data={"customerName": "Nguyễn Văn An", ...},
    form_type="loan"
)
```

**Global Instance:**
```python
browser_agent = BrowserAgentHandler()
```

---

### 5. `multi_agent/graph/builder.py` (518 lines)
**Purpose:** LangGraph Supervisor workflow với 5 tools

**Key Components:**

**5 Tools (Python functions với @tool decorator):**
1. `fill_loan_form(13 params)` - Use Case 1: Đơn vay vốn
2. `fill_crm_form(8 params)` - Use Case 2: CRM update
3. `fill_hr_form(8 params)` - Use Case 3: HR workflow
4. `fill_compliance_form(8 params)` - Use Case 4: Báo cáo tuân thủ
5. `fill_operations_form(11 params)` - Use Case 5: Kiểm tra giao dịch

**Main Function:**
```python
def build_supervisor_workflow(llm):
    """Build LangGraph với Supervisor pattern"""
    # Create supervisor with 5 tools
    supervisor = create_react_agent(
        model=llm,
        tools=[fill_loan_form, fill_crm_form, ...],
        prompt="GỌI TOOL NGAY với placeholders..."
    )
    
    # Build graph
    workflow = StateGraph(MultiAgentState)
    workflow.add_node("supervisor", supervisor)
    workflow.add_edge(START, "supervisor")
    workflow.add_edge("supervisor", END)
    
    return workflow.compile()
```

**Tool Example:**
```python
@tool
def fill_loan_form(
    customer_name: str,
    customer_id: str,
    loan_amount: int,
    ...  # 10 more params
) -> str:
    """Điền form đơn vay"""
    # Map to HTML fields
    form_data = {...}
    
    # Call browser agent
    result = await browser_agent.fill_form(url, form_data)
    
    return "✅ Success" or "❌ Error"
```

---

### 6. `multi_agent/graph/state.py` (102 lines)
**Purpose:** LangGraph state definition

**Key Components:**
- `MultiAgentState` - extends `MessagesState`
- `create_initial_state()` - helper function

**State Fields:**
```python
class MultiAgentState(MessagesState):
    extracted_data: Dict[str, Any]
    is_valid: bool
    validation_errors: List[str]
    form_url: str
    form_type: FormType
    execution_status: ExecutionStatus
    session_id: str
    # ... more fields
```

---

## 🔄 EXECUTION FLOW

```
1. User speaks → WebRTC → bot_multi_agent.py
                              ↓
2. Voice pipeline: STT → LLM → TTS → Audio out
                              ↓
3. Transcript handler → Push to task_queue.py
                              ↓
4. workflow_worker.py pops task → Execute workflow
                              ↓
5. builder.py: Supervisor analyzes → Calls tool
                              ↓
6. Tool calls browser_agent.py → Fill form
                              ↓
7. Result → Update task status → Complete
```

---

## 🎯 IMPORT RULES

### ✅ ĐÚNG - Relative Imports:
```python
# Trong src/bot_multi_agent.py
from .task_queue import task_queue
from .workflow_worker import workflow_worker

# Trong src/workflow_worker.py
from .task_queue import task_queue
from .multi_agent.graph.builder import build_supervisor_workflow

# Trong src/multi_agent/graph/builder.py
from .state import MultiAgentState
```

### ❌ SAI - Absolute Imports:
```python
from task_queue import task_queue  # ❌ Missing dot
```

---

## 🧪 TESTING

### Run main.py:
```bash
python main.py
```

### Expected Output:
```
🚀 Starting VPBank Multi-Agent Bot Server...
🎯 Multi-agent system: Router + 5 Specialists + Browser Executor
📋 Supporting 5 use cases: Loan, CRM, HR, Compliance, Operations
======== Running on http://0.0.0.0:7860 ========
```

### Test Voice Input:
```
User: "Vay 500 triệu"
  ↓
Expected logs:
  ✅ Task pushed to queue
  ⚡ Task popped from queue
  ⚙️  Processing task
  🔨 Building workflow
  ✅ Workflow built
  🔄 Executing workflow
  🏦 Filling LOAN form
  ✅ Task completed
```

---

## 📝 NOTES

### Lazy Loading:
- LLM chỉ load 1 lần khi task đầu tiên
- Workflow chỉ compile 1 lần
- Sau đó reuse cho all tasks → FAST!

### Error Handling:
- Mỗi layer handle errors riêng
- Worker continues nếu 1 task fails
- Voice pipeline continues độc lập

### Async Best Practices:
- Không blocking operations
- Safe asyncio handling trong tools
- Event loop management đúng cách

---

**Version:** 1.0  
**Last Updated:** October 29, 2025  
**Status:** ✅ Production Ready

