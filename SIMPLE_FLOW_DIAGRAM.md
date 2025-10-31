# 📊 SIMPLE FLOW DIAGRAM - VPBANK BACKEND

**Diagram đơn giản để hiểu nhanh**

---

## 🎯 3 LUỒNG CHÍNH

### Luồng 1: KHỞI ĐỘNG (1 lần duy nhất)
```
┌─────────────┐
│  main.py    │ ← Chạy python main.py
└──────┬──────┘
       │ import
       ↓
┌─────────────────────────┐
│  bot_multi_agent.py     │
│  create_app()           │ ← Tạo aiohttp app
└──────┬──────────────────┘
       │ web.run_app()
       ↓
┌─────────────────────────┐
│  Server Running         │
│  Port 7860              │
└─────────────────────────┘
```

---

### Luồng 2: VOICE CONVERSATION (Continuous)
```
┌──────────────┐
│  Frontend    │ User speaks
│  (React)     │
└──────┬───────┘
       │ POST /offer (WebRTC)
       ↓
┌────────────────────────────┐
│  handle_offer()            │ bot_multi_agent.py
│  - Create WebRTC           │
│  - Start run_bot()         │
└──────┬─────────────────────┘
       │ Background task
       ↓
┌────────────────────────────────────────┐
│  run_bot()  bot_multi_agent.py         │
│  ┌──────────────────────────────────┐  │
│  │  Voice Pipeline (CONTINUOUS)     │  │
│  │  Audio → STT → LLM → TTS → Audio │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  Transcript Handler              │  │
│  │  - Save messages                 │  │
│  │  - Send to WebSocket             │  │
│  │  - Detect "BẮT ĐẦU XỬ LÝ"       │  │
│  │    → push_task_to_queue()        │  │
│  └──────────────────────────────────┘  │
└────────────────┬───────────────────────┘
                 │
                 ↓
┌────────────────────────────┐
│  task_queue.push(task)     │ task_queue.py
│  - Add to asyncio.Queue    │
└────────────────────────────┘
```

---

### Luồng 3: WORKFLOW PROCESSING (Background Loop)
```
┌────────────────────────────┐
│  create_worker_task()      │ workflow_worker.py
│  Called by run_bot()       │
└──────┬─────────────────────┘
       │ Start background task
       ↓
┌─────────────────────────────────────┐
│  workflow_worker.start()            │
│  ┌───────────────────────────────┐  │
│  │  INFINITE LOOP:               │  │
│  │  while True:                  │  │
│  │    task = queue.pop() ←BLOCK │  │
│  │    _process_task(task)        │  │
│  └───────────────────────────────┘  │
└──────┬──────────────────────────────┘
       │
       ↓
┌────────────────────────────────────┐
│  _process_task(task)               │
│  ┌──────────────────────────────┐  │
│  │  _get_workflow()             │  │
│  │  → build_supervisor_workflow │  │
│  │    (lazy - compile once)     │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  workflow.ainvoke(state)     │  │
│  │  → LangGraph execution       │  │
│  └──────────────────────────────┘  │
└──────┬─────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  build_supervisor_workflow()  builder.py│
│  ┌───────────────────────────────────┐  │
│  │  Tools:                           │  │
│  │  - fill_loan_form                 │  │
│  │  - fill_crm_form                  │  │
│  │  - fill_hr_form                   │  │
│  │  - fill_compliance_form           │  │
│  │  - fill_operations_form           │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Supervisor Agent (LangGraph)     │  │
│  │  - Analyze conversation           │  │
│  │  - Extract info                   │  │
│  │  - Select tool                    │  │
│  │  - Call tool                      │  │
│  └───────────────────────────────────┘  │
└──────┬──────────────────────────────────┘
       │ Tool selected: fill_loan_form
       ↓
┌────────────────────────────────────┐
│  fill_loan_form(...)  builder.py  │
│  ┌──────────────────────────────┐  │
│  │  Map params → form_data      │  │
│  │  Get URL from env            │  │
│  │  Call browser_agent          │  │
│  └──────────────────────────────┘  │
└──────┬─────────────────────────────┘
       │
       ↓
┌────────────────────────────────────────┐
│  browser_agent.fill_form()             │
│  browser_agent.py                      │
│  ┌──────────────────────────────────┐  │
│  │  Create instruction              │  │
│  │  Get LLM (lazy load)             │  │
│  │  Agent(task, llm)                │  │
│  │  agent.run() ← AI automation     │  │
│  └──────────────────────────────────┘  │
└──────┬─────────────────────────────────┘
       │
       ↓
┌────────────────────────────────────┐
│  Browser-use Agent                 │
│  (External library)                │
│  ┌──────────────────────────────┐  │
│  │  Open Chromium               │  │
│  │  Navigate to S3 form         │  │
│  │  AI fills fields             │  │
│  │  Click submit                │  │
│  │  Return success              │  │
│  └──────────────────────────────┘  │
└──────┬─────────────────────────────┘
       │ {"success": True}
       ↓
┌────────────────────────────────────┐
│  Result propagation back:          │
│  Browser → Tool → Supervisor       │
│  → Workflow → Worker               │
│  → Update task status              │
└────────────────────────────────────┘
```

---

## 📋 FILE-BY-FILE BREAKDOWN

### File 1: `main.py` (24 lines)
**Role:** Entry point  
**Calls:** `bot_multi_agent.create_app()`  
**Called by:** User (python main.py)

---

### File 2: `bot_multi_agent.py` (512 lines)
**Role:** WebRTC server + Voice Agent  

**Functions:**
1. `push_task_to_queue(msg, session)` - Line 57
   - **Calls:** `Task()`, `task_queue.push()`
   - **Called by:** `handle_transcript_update()`

2. `run_bot(webrtc, ws)` - Line 96
   - **Calls:** STT/LLM/TTS services, `create_worker_task()`
   - **Called by:** `handle_offer()`

3. `handle_offer(request)` - Line 373
   - **Calls:** `SmallWebRTCConnection.initialize()`, `run_bot()`
   - **Called by:** Frontend POST /offer

4. `websocket_handler(request)` - Line 451
   - **Calls:** WebSocket operations
   - **Called by:** Frontend WS /ws

5. `create_app()` - Line 475
   - **Calls:** web.Application()
   - **Called by:** main.py

**Global vars:**
- `ws_connections` = set()
- `ice_servers` = [...]
- `routes` = RouteTableDef()

---

### File 3: `task_queue.py` (190 lines)
**Role:** Async task queue (producer-consumer pattern)

**Classes:**
1. `TaskType(Enum)` - Line 14: LOAN, CRM, HR, COMPLIANCE, OPERATIONS
2. `TaskStatus(Enum)` - Line 23: PENDING, PROCESSING, COMPLETED, FAILED
3. `Task` - Line 31: Dataclass with task info
4. `TaskQueue` - Line 62: Queue manager

**Methods:**
- `push(task)` - Line 80: Add task
- `pop()` - Line 97: Get task (blocking)
- `update_task(...)` - Line 126: Update status

**Global instance:**
```python
task_queue = TaskQueue(maxsize=100)  # Line 190
```

**Called by:**
- `bot_multi_agent.py`: push()
- `workflow_worker.py`: pop(), update_task()

---

### File 4: `workflow_worker.py` (174 lines)
**Role:** Background worker - process tasks

**Class:** `WorkflowWorker`

**Methods:**
1. `__init__()` - Line 21: Initialize
2. `_get_llm()` - Line 28: Lazy load LLM
3. `_get_workflow()` - Line 45: Lazy compile workflow
   - **Calls:** `build_supervisor_workflow(llm)`
4. `start()` - Line 52: Start infinite loop
   - **Calls:** `task_queue.pop()`, `_process_task()`
5. `_process_task(task)` - Line 84: Execute workflow
   - **Calls:** `_get_workflow()`, `workflow.ainvoke()`

**Global instance:**
```python
workflow_worker = WorkflowWorker()  # Line 149
```

**Function:**
```python
def create_worker_task():  # Line 157
    return asyncio.create_task(workflow_worker.start())
```

**Called by:**
- `bot_multi_agent.run_bot()`: create_worker_task()

---

### File 5: `browser_agent.py` (239 lines)
**Role:** Browser automation handler

**Class:** `BrowserAgentHandler`

**Methods:**
1. `__init__()` - Line 20: Initialize
2. `_get_llm()` - Line 26: Lazy load Bedrock LLM
3. `fill_form(url, data, type)` - Line 40: Main method
   - **Calls:** `_create_task_instruction()`, `Agent()`
4. `_create_task_instruction(...)` - Line 92: Build prompt

**Global instance:**
```python
browser_agent = BrowserAgentHandler()  # Line 198
```

**Called by:**
- All 5 tools in `builder.py`: `browser_agent.fill_form()`

---

### File 6: `multi_agent/graph/builder.py` (723 lines)
**Role:** LangGraph Supervisor + 5 Tools

**Tools (Functions với @tool decorator):**
1. `fill_loan_form(...)` - Line 27-114
2. `fill_crm_form(...)` - Line 117-218
3. `fill_hr_form(...)` - Line 221-315
4. `fill_compliance_form(...)` - Line 318-517
5. `fill_operations_form(...)` - Line 520-681

**Main Function:**
```python
def build_supervisor_workflow(llm):  # Line 593-723
    tools = [fill_loan_form, ...]
    supervisor = create_react_agent(llm, tools, prompt)
    workflow = StateGraph(...).compile()
    return workflow
```

**Called by:**
- `workflow_worker._get_workflow()`

**Calls:**
- `browser_agent.fill_form()` (from all 5 tools)

---

### File 7: `multi_agent/graph/state.py` (102 lines)
**Role:** LangGraph state definition

**Classes:**
- `MultiAgentState(MessagesState)` - Line 21: State structure
- `create_initial_state(msg, session)` - Line 63: Helper

**Called by:**
- `builder.py`: Import MultiAgentState
- `workflow_worker.py`: Import MultiAgentState

**Không có function gọi khác - chỉ type definitions**

---

### File 8 & 9: `__init__.py` files
**Role:** Package markers & exports

**multi_agent/__init__.py:**
```python
from .graph import build_supervisor_workflow, MultiAgentState, create_initial_state
```

**multi_agent/graph/__init__.py:**
```python
from .builder import build_supervisor_workflow
from .state import MultiAgentState, create_initial_state
```

**Không được import trực tiếp - chỉ export symbols**

---

## 🔄 CALL STACK (Từ User Click → Form Filled)

```
1. User clicks "Connect" on frontend
     ↓
2. Frontend: POST /offer
     ↓
3. handle_offer() ← bot_multi_agent.py
     ↓
4. asyncio.create_task(run_bot(...))
     ↓
5. run_bot() starts ← bot_multi_agent.py
   ├─ Parallel: Voice pipeline (STT → LLM → TTS)
   └─ Parallel: create_worker_task() ← workflow_worker.py
         ↓
6. workflow_worker.start() LOOPS FOREVER
     ↓
7. User speaks: "Vay 50 triệu..."
     ↓
8. Voice pipeline: Audio → Text → LLM → Audio
     ↓
9. Transcript handler detects "BẮT ĐẦU XỬ LÝ"
     ↓
10. push_task_to_queue(conversation) ← bot_multi_agent.py
     ↓
11. task_queue.push(task) ← task_queue.py
     ↓
12. workflow_worker.pop() gets task ← Was BLOCKING, now has task!
     ↓
13. _process_task(task) ← workflow_worker.py
     ↓
14. _get_workflow() → build_supervisor_workflow() ← builder.py (1st time only)
     ↓
15. workflow.ainvoke(state) ← LangGraph execution
     ↓
16. Supervisor analyzes → Selects fill_loan_form
     ↓
17. fill_loan_form(params...) ← builder.py
     ↓
18. browser_agent.fill_form(url, data) ← browser_agent.py
     ↓
19. Agent.run() ← browser-use library
     ├─ Open browser
     ├─ Navigate
     ├─ Fill fields
     └─ Submit
     ↓
20. Return success
     ↓
21. Propagate back: Tool → Workflow → Worker
     ↓
22. task_queue.update_task(COMPLETED)
     ↓
23. Loop back to step 12 (wait for next task)
```

---

## ❓ CÂU HỎI THƯỜNG GẶP

### Q: File nào là entry point?
**A:** `main.py` → gọi `bot_multi_agent.create_app()`

### Q: File nào chứa Voice Agent logic?
**A:** `bot_multi_agent.run_bot()` - Voice pipeline + transcript handler

### Q: File nào handle form filling?
**A:** `browser_agent.py` - Browser automation với browser-use

### Q: File nào điều phối 5 use cases?
**A:** `builder.py` - Supervisor Agent với 5 tools

### Q: File nào connect Voice với Form Filling?
**A:** `task_queue.py` - Queue decouples 2 components

### Q: Có file dư không?
**A:** KHÔNG! Tất cả 9 files đều được dùng

### Q: Voice bot có block khi fill form không?
**A:** KHÔNG! Queue + background worker → Non-blocking

### Q: Làm sao thêm use case mới?
**A:** Thêm 1 tool mới vào `builder.py`, add vào tools list

---

## 📊 MODULE DEPENDENCIES

```
main.py
  |
  v
bot_multi_agent.py
  |
  +---> task_queue.py (shared)
  |       ^
  |       |
  +---> workflow_worker.py
          |
          +---> task_queue.py (same instance!)
          |
          +---> multi_agent/graph/builder.py
                  |
                  +---> browser_agent.py
                  |
                  +---> multi_agent/graph/state.py
```

**Không có circular imports!** ✅

---

*Simplified by: Claude AI*  
*For: Quick Understanding*

