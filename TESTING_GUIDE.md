# 🧪 TESTING GUIDE - VPBank Voice Agent

**Purpose**: Comprehensive testing guide for all features  
**Date**: 2025-11-13

---

## 🎯 TESTING STRATEGY

### 1. Unit Tests (Automated)
### 2. Integration Tests (Automated)
### 3. Manual Tests (Human)
### 4. Performance Tests (Load)
### 5. Security Tests (Audit)

---

## 📋 UNIT TESTS

### Run All Unit Tests

```bash
# Activate environment
source venv/bin/activate

# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Browser agent tests
pytest tests/test_browser_agent.py -v

# New features tests
pytest tests/test_new_features.py -v

# DynamoDB tests
pytest tests/test_dynamodb_service.py -v

# Auth tests
pytest tests/test_auth_service.py -v
```

---

## 🔗 INTEGRATION TESTS

### Test Voice Bot → Browser Agent

```bash
# Start services
./venv/bin/python main_browser_service.py &
./venv/bin/python main_voice.py &

# Wait for startup
sleep 10

# Run integration tests
pytest tests/test_integration.py -v -m integration

# Stop services
pkill -f "python main_"
```

---

## 🎤 MANUAL TESTS

### Test Case 1: Basic Voice Interaction

**Objective**: Verify voice recognition and TTS

**Steps**:
1. Open http://localhost:5173
2. Click microphone icon
3. Say: "Xin chào"
4. Expected: Hear Vietnamese TTS response
5. Verify: Transcript appears in real-time

**Pass Criteria**:
- ✅ Voice recognized correctly
- ✅ TTS response clear
- ✅ Transcript accurate

---

### Test Case 2: Loan Form (Use Case 1)

**Objective**: Test complete loan application workflow

**Steps**:
```
1. Say: "Bắt đầu điền đơn vay"
   Expected: "Đã mở form loan"

2. Say: "Tên là Nguyễn Văn An"
   Expected: "Đã điền customerName"

3. Say: "Căn cước công dân 012345678901"
   Expected: "Đã điền customerId"

4. Say: "Số điện thoại 0901234567"
   Expected: "Đã điền phoneNumber"

5. Say: "Email test@vpbank.com"
   Expected: "Đã điền email"

6. Say: "Vay 500 triệu"
   Expected: "Đã điền loanAmount"

7. Say: "Kỳ hạn 24 tháng"
   Expected: "Đã điền loanTerm"

8. Say: "Submit form"
   Expected: "Form đã được submit thành công"
```

**Pass Criteria**:
- ✅ All fields filled correctly
- ✅ Form submitted successfully
- ✅ No errors

---

### Test Case 3: File Upload

**Objective**: Test file upload functionality

**Steps**:
```
1. Say: "Bắt đầu điền đơn vay"
2. Say: "Upload ảnh CCCD"
3. Expected: File picker opens
4. Select a file
5. Expected: "Đã upload file vào field idCardImage"
```

**Pass Criteria**:
- ✅ File picker triggered
- ✅ File uploaded successfully
- ✅ Filename displayed

---

### Test Case 4: Search Field

**Objective**: Test field search functionality

**Steps**:
```
1. Say: "Bắt đầu điền đơn vay"
2. Say: "Tìm field số điện thoại"
3. Expected: "Tìm thấy và focus vào field: phoneNumber"
4. Verify: Field is highlighted/focused
```

**Pass Criteria**:
- ✅ Field found correctly
- ✅ Field focused
- ✅ Visual feedback

---

### Test Case 5: Draft Management

**Objective**: Test save and load draft

**Steps**:
```
1. Say: "Bắt đầu điền đơn vay"
2. Say: "Tên là Nguyễn Văn An"
3. Say: "SĐT 0901234567"
4. Say: "Lưu nháp tên là 'Đơn vay An'"
5. Expected: "Đã lưu nháp với 2 fields"

[New session]
6. Say: "Bắt đầu điền đơn vay"
7. Say: "Load nháp 'Đơn vay An'"
8. Expected: "Đã load nháp với 2 fields"
9. Verify: Fields are filled
```

**Pass Criteria**:
- ✅ Draft saved to DynamoDB
- ✅ Draft loaded correctly
- ✅ Fields restored

---

### Test Case 6: Regional Accents

**Objective**: Test accent understanding

**Steps**:
```
1. Giọng Bắc: "Tôi muốn vay năm trăm triệu đồng"
   Expected: Understand "500,000,000"

2. Giọng Nam: "Tui muốn vay năm trăm triệu đồng"
   Expected: Understand "500,000,000"

3. Giọng Trung: "Tôi muốn vay năm trăm triệu đồng"
   Expected: Understand "500,000,000"

4. Giọng Huế: "Tui muốn vay năm trăm triệu đồng"
   Expected: Understand "500,000,000"
```

**Pass Criteria**:
- ✅ All accents recognized
- ✅ Same result for all
- ✅ No errors

---

### Test Case 7: Error Correction

**Objective**: Test correction commands

**Steps**:
```
1. Say: "Số điện thoại 0901234567"
   Expected: "Đã điền phoneNumber"

2. Say: "Không, là 0987654321"
   Expected: "Đã sửa phoneNumber"

3. Verify: Field updated to 0987654321
```

**Pass Criteria**:
- ✅ Correction understood
- ✅ Field updated
- ✅ No duplicate entries

---

### Test Case 8: Pronoun Understanding

**Objective**: Test pronoun resolution

**Steps**:
```
1. Say: "Tên là Nguyễn Văn An"
2. Say: "Anh ấy sinh năm 1990"
   Expected: Understand "Nguyễn Văn An sinh năm 1990"

3. Say: "Điền số điện thoại"
4. Say: "Nó là 0901234567"
   Expected: Understand "phoneNumber là 0901234567"
```

**Pass Criteria**:
- ✅ Pronouns resolved correctly
- ✅ Context maintained
- ✅ Fields filled correctly

---

### Test Case 9: Date Parsing

**Objective**: Test Vietnamese date formats

**Steps**:
```
1. Say: "Ngày sinh 15 tháng 3 năm 1990"
   Expected: Parse to "15/03/1990"

2. Say: "Ngày sinh 15/3/90"
   Expected: Parse to "15/03/1990"

3. Say: "Sinh ngày 15-03-1990"
   Expected: Parse to "15/03/1990"
```

**Pass Criteria**:
- ✅ All formats parsed
- ✅ Correct date values
- ✅ No errors

---

### Test Case 10: All 5 Form Types

**Objective**: Verify all use cases work

**Forms to Test**:
1. ✅ Loan Application (Use Case 1)
2. ⏳ CRM Update (Use Case 2)
3. ⏳ HR Workflow (Use Case 3)
4. ⏳ Compliance Reporting (Use Case 4)
5. ⏳ Operations Validation (Use Case 5)

**For Each Form**:
- Start form
- Fill all required fields
- Submit form
- Verify success

---

## ⚡ PERFORMANCE TESTS

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:7863/api/health

# Expected:
# - Requests per second: >100
# - Mean response time: <100ms
# - No failures
```

### Stress Testing

```bash
# Test with concurrent requests
for i in {1..50}; do
  curl -X POST http://localhost:7863/api/execute \
    -H "Content-Type: application/json" \
    -d "{\"user_message\": \"test $i\", \"session_id\": \"stress-$i\"}" &
done

# Monitor:
# - CPU usage
# - Memory usage
# - Response times
# - Error rate
```

### Response Time Testing

```bash
# Measure end-to-end response time
time curl -X POST http://localhost:7863/api/execute \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Open loan form", "session_id": "perf-test"}'

# Target: <2s
```

---

## 🔒 SECURITY TESTS

### Input Validation

```bash
# Test SQL injection
curl -X POST http://localhost:7863/api/execute \
  -d '{"user_message": "'; DROP TABLE sessions; --", "session_id": "test"}'

# Expected: Sanitized, no error

# Test XSS
curl -X POST http://localhost:7863/api/execute \
  -d '{"user_message": "<script>alert(1)</script>", "session_id": "test"}'

# Expected: Sanitized, no execution
```

### Authentication

```bash
# Test without auth token
curl http://localhost:7860/api/sessions

# Expected: 401 Unauthorized

# Test with invalid token
curl -H "Authorization: Bearer invalid" \
  http://localhost:7860/api/sessions

# Expected: 401 Unauthorized
```

### Rate Limiting

```bash
# Send 100 requests rapidly
for i in {1..100}; do
  curl http://localhost:7863/api/health &
done

# Expected: Some requests rate-limited
```

---

## 📊 TEST RESULTS TEMPLATE

### Test Execution Report

```markdown
## Test Run: [Date]

### Summary
- Total Tests: X
- Passed: Y
- Failed: Z
- Skipped: W
- Coverage: XX%

### Unit Tests
- test_browser_agent.py: PASS/FAIL
- test_new_features.py: PASS/FAIL
- test_dynamodb_service.py: PASS/FAIL

### Integration Tests
- test_integration.py: PASS/FAIL

### Manual Tests
- Loan form: PASS/FAIL
- CRM form: PASS/FAIL
- HR form: PASS/FAIL
- Compliance form: PASS/FAIL
- Operations form: PASS/FAIL

### Performance Tests
- Load test: PASS/FAIL
- Stress test: PASS/FAIL
- Response time: X.XXs

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
1. [Recommendation]
2. [Recommendation]
```

---

## 🎯 ACCEPTANCE CRITERIA

### For Demo
- [ ] All core features demonstrated
- [ ] At least 3 form types working
- [ ] No critical bugs
- [ ] Response time acceptable
- [ ] Audience impressed

### For Production
- [ ] All 5 form types working
- [ ] All tests passing (>85% coverage)
- [ ] Performance <2s (p95)
- [ ] Security audit passed
- [ ] Load test passed (100+ users)
- [ ] Monitoring configured
- [ ] Documentation complete

---

## 📞 SUPPORT

### If Tests Fail

1. **Check logs**: `tail -f logs/browser_agent.log`
2. **Check services**: `curl http://localhost:7863/api/health`
3. **Restart services**: `pkill -f "python main_" && ./scripts/start-integrated.sh`
4. **Check environment**: `grep -v "^#" .env | grep -v "^$"`
5. **Review documentation**: Check relevant .md files

### Common Issues

**Issue**: Tests fail with import errors  
**Solution**: `pip install -r requirements-test.txt`

**Issue**: Browser timeout  
**Solution**: Check `BROWSER_HEADLESS=true` in .env

**Issue**: Rate limit errors  
**Solution**: Wait 60s between tests or use different API key

---

## 🚀 NEXT STEPS

1. **Run unit tests**: `pytest tests/ -v`
2. **Fix any failures**: Debug and fix
3. **Run integration tests**: `pytest -m integration`
4. **Manual testing**: Follow test cases above
5. **Performance testing**: Load and stress tests
6. **Security testing**: Vulnerability scan
7. **Create test report**: Document results

---

**Status**: ✅ READY FOR TESTING  
**Timeline**: 2-3 days for complete testing  
**Confidence**: 95%
