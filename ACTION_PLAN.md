# 🔧 ACTION PLAN - Đưa Product Lên Production-Ready

## 🎯 Mục tiêu: Đạt 9/10 Production Quality trong 3-5 ngày

---

## ⚡ PHASE 1: FIX IMMEDIATE ISSUES (4 giờ)

### Task 1.1: Install Missing Dependencies (30 phút)
```bash
cd /home/ubuntu/speak-to-input
source venv/bin/activate

# Add missing dependencies to requirements.txt
cat >> requirements.txt <<EOF

# API Documentation
aiohttp-swagger3==0.8.0

# YAML support for OpenAPI
PyYAML==6.0.1
EOF

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Verify installations
python -c "import pytest; import aiohttp_swagger3; print('✅ All dependencies OK')"
```

**Expected Result**: ✅ All imports successful

---

### Task 1.2: Fix Import Paths (1 giờ)

**Problem**: Một số imports có thể sai path

**Fix**:
```bash
# Test all imports
python -c "
from src.monitoring import initialize_service_info
from src.exceptions import BrowserExecutionError
from src.utils.logging_config import configure_logging
from src.utils.debouncer import RequestDebouncer
from src.cost.llm_cache import llm_cache
print('✅ All imports OK')
"
```

**If errors**: Fix import paths in affected files

---

### Task 1.3: Create Missing __init__.py Files (30 phút)

**Check**:
```bash
# Ensure all Python packages have __init__.py
find src/ -type d -exec test -f {}/__init__.py \; -print || echo "Missing __init__.py"
```

**Fix**: Create any missing __init__.py files

---

### Task 1.4: Run Simple Import Test (1 giờ)

```bash
# Test main_browser_service.py imports
python -c "
import sys
sys.path.insert(0, 'src')
from main_browser_service import create_app
print('✅ Browser service imports OK')
"

# Test main_voice_integrated.py imports  
python -c "
import sys
sys.path.insert(0, 'src')
exec(open('main_voice_integrated.py').read())
print('✅ Voice service imports OK')
"
```

**Expected**: No import errors

---

## ⚡ PHASE 2: RUN AND FIX TESTS (6 giờ)

### Task 2.1: Run Unit Tests (2 giờ)

```bash
source venv/bin/activate

# Run tests with verbose output
pytest tests/test_browser_agent.py -v --tb=short

# Expected: Some tests may fail - FIX THEM
# Common issues:
# - Mock không đúng
# - Import paths sai
# - Missing fixtures
```

**Goal**: Get at least 80% tests passing

---

### Task 2.2: Fix Failing Tests (2 giờ)

**Common fixes**:

```python
# Fix 1: Mock paths
# Wrong: @patch('browser_agent.ChatOpenAI')
# Right: @patch('src.browser_agent.ChatOpenAI')

# Fix 2: Add missing imports in tests
from src.browser_agent import BrowserAgentHandler

# Fix 3: Fix async test decorators
@pytest.mark.asyncio
async def test_something():
    pass
```

**Iterate until all tests pass**

---

### Task 2.3: Run Integration Tests (2 giờ)

```bash
# Start services in background
./scripts/start-integrated.sh &

# Wait for services to start
sleep 15

# Run integration tests
pytest tests/test_integration.py -v -m integration

# Stop services
pkill -f "python main_"
```

**Fix any failures**

---

## ⚡ PHASE 3: INTEGRATE FEATURES PROPERLY (8 giờ)

### Task 3.1: Integrate LLM Caching (3 giờ)

**Current**: LLM calls không có caching
**Need**: Wrap LLM service với cache layer

**File to modify**: `src/voice_bot.py`

```python
# Add at top
from src.cost.llm_cache import llm_cache
from src.monitoring import llm_cache_hits_total, llm_cache_misses_total

# Create cached LLM wrapper
class CachedLLMService:
    def __init__(self, llm_service):
        self.llm = llm_service
    
    async def generate(self, prompt, **kwargs):
        # Check cache first
        temperature = kwargs.get('temperature', 0.0)
        cached = llm_cache.get(prompt, model="claude", temperature=temperature)
        
        if cached:
            llm_cache_hits_total.labels(cache_type="response").inc()
            return cached
        
        llm_cache_misses_total.labels(cache_type="response").inc()
        
        # Call actual LLM
        response = await self.llm.generate(prompt, **kwargs)
        
        # Cache response
        llm_cache.put(prompt, response, model="claude", temperature=temperature)
        
        return response

# Use cached LLM
llm = AWSBedrockLLMService(...)
cached_llm = CachedLLMService(llm)
```

**Test**: Verify cache hit rate >20% after 100 requests

---

### Task 3.2: Integrate Request Debouncing (3 giờ)

**Current**: Mỗi user message push ngay
**Need**: Debounce để reduce calls

**File to modify**: `src/voice_bot.py`

```python
# Add at top
from src.utils.debouncer import RequestDebouncer

# Initialize debouncer (global or in run_bot)
browser_debouncer = RequestDebouncer(delay_seconds=2.0)

# In transcript handler, replace:
# task = asyncio.create_task(push_to_browser_service(...))

# With:
await browser_debouncer.debounce(
    task_id=f"push-{session_id}",
    data=full_context,
    callback=lambda ctx: asyncio.create_task(
        push_to_browser_service(ctx, ws_connections, session_id, processing_task)
    )
)
```

**Test**: Verify rapid messages được debounce (chỉ execute 1 lần)

---

### Task 3.3: Add Metrics Tracking to Core Functions (2 giờ)

**Add metrics to**:
- `push_to_browser_service()` - Track HTTP calls
- `run_bot()` - Track session duration
- LLM calls - Track token usage
- STT/TTS calls - Track duration

```python
# Example
from src.monitoring import stt_requests_total, stt_request_duration_seconds
import time

# Before STT call
start = time.time()

# STT call
result = await stt.process(audio)

# After STT call
duration = time.time() - start
stt_requests_total.labels(provider="openai", language="vi", status="success").inc()
stt_request_duration_seconds.labels(provider="openai").observe(duration)
```

---

## ⚡ PHASE 4: VERIFICATION (8 giờ)

### Task 4.1: Manual E2E Testing (4 giờ)

**Test Cases**:

1. **Voice Conversation Flow**
   ```
   ✅ Start conversation
   ✅ Speak Vietnamese
   ✅ Get TTS response
   ✅ Transcript appears in real-time
   ✅ Session saved to DynamoDB
   ```

2. **Form Filling (All 5 Types)**
   ```
   ✅ Case 1: Loan application
   ✅ Case 2: CRM update
   ✅ Case 3: HR request
   ✅ Case 4: Compliance report
   ✅ Case 5: Operations validation
   ```

3. **Incremental Mode**
   ```
   ✅ Start form
   ✅ Fill field by field
   ✅ Submit form
   ✅ Verify completion
   ```

4. **One-Shot Mode**
   ```
   ✅ Provide all info at once
   ✅ Auto-fill all fields
   ✅ Verify accuracy
   ```

---

### Task 4.2: Metrics Verification (2 giờ)

```bash
# Start services
./scripts/start-integrated.sh

# Make some requests
# Then check metrics

# 1. Browser Agent metrics
curl http://localhost:7863/metrics | grep vpbank_voice_agent_browser

# Verify you see:
# vpbank_voice_agent_browser_sessions_total{form_type="loan",status="success"} 1.0
# vpbank_voice_agent_browser_session_duration_seconds_bucket{...} ...

# 2. Voice Bot metrics
curl http://localhost:7860/metrics | grep vpbank_voice_agent_voice

# 3. LLM cache metrics
curl http://localhost:7860/metrics | grep vpbank_voice_agent_llm_cache

# Should show hits and misses
```

**Expected**: All metrics updating correctly

---

### Task 4.3: Correlation ID Verification (1 giờ)

```bash
# Send request với correlation ID
curl -X POST http://localhost:7863/api/execute \
  -H "X-Correlation-ID: test-correlation-123" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Test", "session_id": "test"}'

# Check logs
grep "test-correlation-123" logs/browser_agent.log

# Expected: Thấy correlation ID trong mọi log entry liên quan
```

---

### Task 4.4: Performance Testing (1 giờ)

```bash
# Test 1: LLM Cache Effectiveness
# Make 100 requests with same prompt
for i in {1..100}; do
  curl -X POST http://localhost:7860/api/test-llm \
    -H "Content-Type: application/json" \
    -d '{"prompt": "xin chào"}'
done

# Check cache stats
curl http://localhost:7860/metrics | grep llm_cache_hits

# Expected: ~80-90% hit rate for repeated prompts

# Test 2: Request Debouncing
# Send 10 rapid requests
for i in {1..10}; do
  curl -X POST http://localhost:7863/api/execute \
    -d '{"user_message": "test", "session_id": "debounce-test"}' &
done

# Expected: Chỉ ~2-3 actual executions (rest được debounce)

# Test 3: Response Time
ab -n 100 -c 10 http://localhost:7863/api/health

# Expected: <100ms avg response time
```

---

## ⚡ PHASE 5: PRODUCTION PREP (8 giờ)

### Task 5.1: Deploy DynamoDB GSI (2 giờ)

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan GSI deployment
terraform plan -target=aws_dynamodb_table.vpbank_sessions_optimized

# Apply (creates table with GSI)
terraform apply -target=aws_dynamodb_table.vpbank_sessions_optimized

# Wait for GSI to be active (~5-10 minutes)

# Switch to optimized service
# In voice_bot.py:
# from src.dynamodb_service_optimized import OptimizedDynamoDBService
# dynamodb_service = OptimizedDynamoDBService()
```

---

### Task 5.2: Setup Monitoring Stack (4 giờ)

**Option 1: Docker Compose với Prometheus + Grafana**

```yaml
# Add to docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

**Create prometheus.yml**:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'voice-bot'
    static_configs:
      - targets: ['voice-bot:7860']
  
  - job_name: 'browser-agent'
    static_configs:
      - targets: ['browser-agent:7863']
```

**Start**:
```bash
docker-compose up prometheus grafana -d

# Access Grafana: http://localhost:3000
# Login: admin/admin
# Add Prometheus datasource
# Import dashboards
```

---

### Task 5.3: Security Hardening (2 giờ)

```bash
# 1. Run security scans
pip install bandit safety

# Bandit security scan
bandit -r src/ -f json -o security-report.json

# Safety check for vulnerable dependencies
safety check --json

# 2. Fix any critical issues found

# 3. Update secrets management (move from .env to AWS Secrets Manager)
```

---

## ⚡ PHASE 6: FINAL VALIDATION (4 giờ)

### Validation Checklist

```bash
# 1. All services start successfully
./scripts/start-integrated.sh
# Wait 30 seconds
curl http://localhost:7863/api/health  # Should return 200
curl http://localhost:7860/health      # Should return 200  
curl http://localhost:5173             # Should return HTML

# 2. Metrics endpoints working
curl http://localhost:7863/metrics | grep vpbank  # Should show metrics
curl http://localhost:7860/metrics | grep vpbank  # Should show metrics

# 3. Tests passing
pytest tests/ -v
# Expected: >85% pass rate

# 4. Voice conversation working
# Open http://localhost:5173
# Click microphone
# Say "Xin chào"
# Should hear Vietnamese TTS response

# 5. Form filling working
# Say "Tạo đơn vay cho khách hàng Nguyễn Văn An..."
# Should see form being filled

# 6. Monitoring working
# Check Grafana dashboards
# Verify metrics updating

# 7. Correlation IDs working
grep correlation_id logs/browser_agent.log | wc -l
# Should be > 0

# 8. LLM caching working
# Make same request twice
# Check cache hit rate increased

# 9. Error handling working
# Send invalid request
curl -X POST http://localhost:7863/api/execute -d '{}'
# Should get structured error response

# 10. Documentation accessible
# Open http://localhost:7860/docs (if Swagger setup)
```

---

## 📋 ACCEPTANCE CRITERIA

### Must Pass (Blocking)
- [ ] All services start without errors
- [ ] Health checks return 200
- [ ] Voice conversation works end-to-end
- [ ] At least 3/5 form types working
- [ ] Metrics endpoints accessible
- [ ] Logs written with correlation IDs
- [ ] No critical security vulnerabilities
- [ ] >80% unit tests passing

### Should Pass (High Priority)
- [ ] All 5 form types working
- [ ] LLM cache showing hits
- [ ] Debouncing reducing calls
- [ ] Prometheus scraping successful
- [ ] >85% unit tests passing
- [ ] Integration tests passing
- [ ] Performance acceptable (<2s response time)

### Nice to Have (Optional)
- [ ] Grafana dashboards configured
- [ ] CI/CD pipeline passing
- [ ] Swagger UI working
- [ ] DynamoDB GSI deployed
- [ ] 90%+ test coverage

---

## 🚨 KNOWN ISSUES TO FIX

### Issue 1: pytest Not Installed
**Status**: 🔴 Blocking  
**Fix**:
```bash
pip install -r requirements-test.txt
```

### Issue 2: LLM Caching Not Wired Up
**Status**: 🔴 Blocking  
**Fix**: Modify voice_bot.py LLM calls (see Task 3.1 above)

### Issue 3: Request Debouncing Not Used
**Status**: 🟡 Medium  
**Fix**: Wire up in transcript handler (see Task 3.2 above)

### Issue 4: Swagger Dependencies Missing
**Status**: 🟡 Medium  
**Fix**: Install aiohttp-swagger3

### Issue 5: Some Tests May Have Wrong Mocks
**Status**: 🟡 Medium  
**Fix**: Update mocks based on actual API

---

## 📅 TIMELINE

### Day 1: Fix Critical Issues
- [ ] AM: Install dependencies + fix imports (2h)
- [ ] PM: Run and fix unit tests (4h)

### Day 2: Integration
- [ ] AM: Integrate LLM caching (3h)
- [ ] PM: Integrate request debouncing (3h)

### Day 3: Testing & Verification
- [ ] AM: Manual E2E testing all features (4h)
- [ ] PM: Performance testing + metrics verification (4h)

### Day 4: Monitoring & Documentation
- [ ] AM: Setup Prometheus + Grafana (3h)
- [ ] PM: Update documentation, create runbooks (3h)

### Day 5: Final Validation
- [ ] AM: Security audit (2h)
- [ ] PM: Final testing + sign-off (2h)

**Total**: ~30 hours = 3-5 working days

---

## 🎯 SUCCESS CRITERIA

Product sẽ đạt **9/10 Production-Ready** khi:

1. ✅ All tests passing (>85% coverage)
2. ✅ All 5 form types working
3. ✅ Metrics verified and monitoring setup
4. ✅ LLM caching reducing costs by 20-30%
5. ✅ Request debouncing reducing calls by 30-40%
6. ✅ No critical security issues
7. ✅ Performance acceptable (<2s avg response)
8. ✅ Documentation complete
9. ✅ CI/CD pipeline working
10. ✅ Team trained on deployment

---

## 🚀 QUICK START (Right Now)

### Immediate Actions (Next 2 hours)

```bash
# 1. Install missing dependencies
cd /home/ubuntu/speak-to-input
source venv/bin/activate
pip install aiohttp-swagger3 PyYAML
pip install -r requirements-test.txt

# 2. Run simple import test
python -c "from src.monitoring import initialize_service_info; print('OK')"

# 3. Run one unit test
pytest tests/test_browser_agent.py::TestBrowserAgentHandler::test_initialization -v

# 4. Start services and test health
./scripts/start-integrated.sh &
sleep 15
curl http://localhost:7863/api/health
curl http://localhost:7860/health

# 5. View metrics
curl http://localhost:7863/metrics | head -50

# 6. Stop services
pkill -f "python main_"
```

---

## 💡 RECOMMENDATION

**Câu trả lời cho "Product đạt yêu cầu chưa?"**

### Hiện tại: **7/10 - CHƯA ĐẠT 100%** ⚠️

**Lý do**:
- Core features OK nhưng new improvements chưa integrate thật
- Tests chưa run pass
- Monitoring chưa verify
- Cần 3-5 ngày để đạt production-ready thực sự

**Sau khi complete ACTION PLAN**: **9/10 - PRODUCTION-READY** ✅

**Khuyến nghị**:
1. 🔴 KHÔNG deploy production ngay
2. 🟡 Dành 3-5 ngày fix và test
3. 🟢 Deploy staging trước
4. ✅ Production sau khi pass acceptance criteria

---

**Next Step**: Bắt đầu Phase 1 ngay bây giờ?

