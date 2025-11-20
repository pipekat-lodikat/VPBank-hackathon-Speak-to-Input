# 🚀 Integrated Features Guide

## Quick Start với Integrated Version

### 1. Start All Services (Enhanced)
```bash
# Sử dụng script tích hợp đầy đủ
./scripts/start-integrated.sh
```

Script này sẽ start:
- ✅ Browser Agent với Prometheus metrics + Correlation IDs
- ✅ Voice Bot với LLM caching + Request debouncing  
- ✅ Frontend với dynamic configuration

> ⚙️ **Tùy chỉnh:** đặt `BROWSER_REQUEST_DEBOUNCE_SECONDS` trong `.env` (default `2.0`) để kiểm soát độ trễ đẩy request tới Browser Agent.

### 2. Xem Metrics Real-time

**Browser Agent Metrics:**
```bash
curl http://localhost:7863/metrics
```

**Voice Bot Metrics:**
```bash
curl http://localhost:7860/metrics
```

### 3. Test Features

#### A. Test Correlation ID Tracking
```bash
# Send request with correlation ID
curl -X POST http://localhost:7863/api/execute \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: test-123-456" \
  -d '{
    "user_message": "Test message",
    "session_id": "test-session"
  }'

# Check logs - correlation ID sẽ xuất hiện trong tất cả log entries
tail -f logs/browser_agent.log | grep "test-123-456"
```

#### B. Test Prometheus Metrics
```bash
# Check browser automation metrics
curl -s http://localhost:7863/metrics | grep vpbank_voice_agent_browser

# Check LLM metrics  
curl -s http://localhost:7860/metrics | grep vpbank_voice_agent_llm

# Check error metrics
curl -s http://localhost:7863/metrics | grep vpbank_voice_agent_errors
```

#### C. Test LLM Caching
```python
# Test trong Python
from src.cost.llm_cache import llm_cache

# First call - cache miss
response1 = llm_cache.get("xin chào")
print(f"First call: {response1}")  # None

# Cache the response
llm_cache.put("xin chào", "Xin chào! Tôi có thể giúp gì?")

# Second call - cache hit
response2 = llm_cache.get("xin chào")
print(f"Second call: {response2}")  # Cached response

# Check stats
stats = llm_cache.get_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")
print(f"Cost savings: ${stats['estimated_cost_savings_usd']}")
```

#### D. Test Request Debouncing
```bash
# Send multiple rapid requests - chỉ request cuối cùng sẽ được execute
for i in {1..5}; do
  curl -X POST http://localhost:7863/api/execute \
    -H "Content-Type: application/json" \
    -d "{\"user_message\": \"Test $i\", \"session_id\": \"test\"}" &
done

# Check logs - chỉ thấy 1 execution sau 2 seconds
```

#### E. Test Structured Exceptions
```bash
# Send invalid request
curl -X POST http://localhost:7863/api/execute \
  -H "Content-Type: application/json" \
  -d '{}'

# Response với structured error:
# {
#   "error": "MISSING_REQUIRED_FIELD",
#   "message": "Required field 'user_message' is missing",
#   "details": {"field": "user_message"}
# }
```

---

## 📊 Monitoring Dashboard Setup

### 1. Install Prometheus (Optional)
```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64/

# Create config
cat > prometheus.yml <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'voice-bot'
    static_configs:
      - targets: ['localhost:7860']
  
  - job_name: 'browser-agent'
    static_configs:
      - targets: ['localhost:7863']
EOF

# Start Prometheus
./prometheus --config.file=prometheus.yml
# Access: http://localhost:9090
```

### 2. Key Metrics to Monitor

**Performance:**
- `vpbank_voice_agent_http_request_duration_seconds` - Request latency
- `vpbank_voice_agent_browser_session_duration_seconds` - Browser automation time
- `vpbank_voice_agent_llm_request_duration_seconds` - LLM response time

**Cost Tracking:**
- `vpbank_voice_agent_llm_tokens_total` - Token consumption
- `vpbank_voice_agent_llm_cost_usd_total` - Estimated costs
- `vpbank_voice_agent_llm_cache_hits_total` - Cache savings

**Reliability:**
- `vpbank_voice_agent_errors_total` - Error count by type
- `vpbank_voice_agent_browser_sessions_total{status="failed"}` - Failed automations
- `vpbank_voice_agent_service_health` - Service health status

**Business Metrics:**
- `vpbank_voice_agent_forms_filled_total` - Forms completed
- `vpbank_voice_agent_forms_submitted_total` - Forms submitted
- `vpbank_voice_agent_voice_sessions_total` - Voice sessions

---

## 🔍 Debugging với Correlation IDs

### View Logs với Correlation ID
```bash
# Follow logs với correlation ID filter
tail -f logs/browser_agent.log | grep "correlation_id"

# Search specific correlation ID
grep "abc-123-def" logs/*.log

# View all logs for a request
grep "request_id: 550e8400" logs/*.log
```

### Trace Request Across Services
```bash
# 1. Send request với correlation ID
CORR_ID="trace-$(date +%s)"
curl -X POST http://localhost:7863/api/execute \
  -H "X-Correlation-ID: $CORR_ID" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Test", "session_id": "test"}'

# 2. Trace qua tất cả services
echo "=== Browser Agent Logs ==="
grep "$CORR_ID" logs/browser_agent.log

echo "=== Voice Bot Logs ==="
grep "$CORR_ID" logs/voice_bot.log
```

---

## 🧪 Running Tests với Integrated Features

### Unit Tests
```bash
# Run all tests
pytest tests/ -v

# Run với coverage
pytest tests/ --cov=src --cov-report=html

# Test specific module
pytest tests/test_browser_agent.py -v
```

### Integration Tests
```bash
# Run integration tests only
pytest tests/test_integration.py -v -m integration

# Test with real services running
./scripts/start-integrated.sh &
sleep 10
pytest tests/test_integration.py -v
```

### Load Testing
```bash
# Simple load test
for i in {1..100}; do
  curl -X POST http://localhost:7863/api/execute \
    -H "Content-Type: application/json" \
    -d "{\"user_message\": \"Test $i\", \"session_id\": \"load-test\"}" &
done

# Monitor metrics during load
watch -n 1 'curl -s http://localhost:7863/metrics | grep vpbank_voice_agent_http_requests_total'
```

### Test 2: Request Debouncing
# Send 10 rapid requests (Debouncer default 2s, adjustable via BROWSER_REQUEST_DEBOUNCE_SECONDS)
for i in {1..10}; do
  curl -X POST http://localhost:7863/api/execute \
    -H "Content-Type: application/json" \
    -d "{\"user_message\": \"test\", \"session_id\": \"debounce-test\"}" &
done

# Expected: Only ~2-3 actual executions (rest được debounce)
```

---

## 📈 Performance Improvements Verification

### 1. Database Query Speed (GSI)
```python
from src.dynamodb_service_optimized import OptimizedDynamoDBService
import time

db = OptimizedDynamoDBService()

# Old way (scan) - slow
start = time.time()
# scan all records...
old_time = time.time() - start

# New way (GSI query) - fast
start = time.time()
sessions = db.get_sessions_by_user(user_id="test-user", limit=50)
new_time = time.time() - start

print(f"Speedup: {old_time/new_time:.1f}x faster")
```

### 2. LLM Cost Savings
```python
from src.cost.llm_cache import llm_cache

# Check savings
stats = llm_cache.get_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")
print(f"Total requests: {stats['total_requests']}")
print(f"Estimated savings: ${stats['estimated_cost_savings_usd']}")

# Expected: 30-40% cost reduction with good hit rate
```

### 3. Request Debouncing Effectiveness
```bash
# Monitor debouncing in logs
grep "Debounced:" logs/voice_bot.log | wc -l
grep "Executing debounced" logs/voice_bot.log | wc -l

# Ratio should show ~40% reduction in actual executions
```

---

## 🐛 Troubleshooting

### Issue: Metrics endpoint not working
```bash
# Check if metrics middleware is added
curl -v http://localhost:7863/metrics

# Should see:
# HTTP/1.1 200 OK
# Content-Type: text/plain; version=0.0.4; charset=utf-8
```

**Fix:**
```python
# In main_browser_service.py, verify:
from src.monitoring.middleware import setup_metrics_endpoint
setup_metrics_endpoint(app, path="/metrics")
```

### Issue: Correlation IDs not showing in logs
```bash
# Check log format
tail logs/browser_agent.log

# Should see format like:
# 2025-01-09 12:00:00.123 | INFO | abc-123-def | ...
```

**Fix:**
```python
# Verify logging configuration
from src.utils.logging_config import configure_logging
configure_logging(level="INFO", format_type="detailed")
```

### Issue: LLM cache not working
```python
# Test cache directly
from src.cost.llm_cache import llm_cache

# Should be initialized automatically
stats = llm_cache.get_stats()
print(stats)  # Should show cache stats
```

**Fix:**
```python
# Re-initialize if needed
from src.cost.llm_cache import init_common_responses
init_common_responses()
```

### Issue: Tests failing
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run with verbose output
pytest tests/ -vv --tb=short

# Check specific test
pytest tests/test_browser_agent.py::TestBrowserAgentHandler::test_initialization -vv
```

---

## 📚 Documentation Links

- **Main README**: `README.md` - Project overview
- **Improvements**: `IMPROVEMENTS.md` - Detailed improvements summary
- **Claude Guide**: `CLAUDE.md` - Development guidelines
- **API Docs**: http://localhost:7860/docs (when running)
- **Metrics**: http://localhost:7860/metrics

---

## ✅ Verification Checklist

Sau khi start services, verify:

- [ ] Browser Agent health check: `curl http://localhost:7863/api/health`
- [ ] Voice Bot health check: `curl http://localhost:7860/health`
- [ ] Browser metrics accessible: `curl http://localhost:7863/metrics`
- [ ] Voice Bot metrics accessible: `curl http://localhost:7860/metrics`
- [ ] Frontend accessible: http://localhost:5173
- [ ] Logs being written: `ls -lh logs/`
- [ ] Correlation IDs in logs: `grep "correlation_id" logs/*.log`
- [ ] No errors in console: `tail -f logs/*_console.log`

---

**Tất cả features đã được tích hợp và sẵn sàng sử dụng! 🎉**

