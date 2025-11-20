# 🚀 QUICK REFERENCE - VPBank Voice Agent

## Services Status

```bash
# Check all services
curl http://localhost:7860/health  # Voice Bot
curl http://localhost:7863/api/health  # Browser Agent
curl http://localhost:5173  # Frontend

# Check metrics
curl http://localhost:7863/metrics | grep vpbank
```

## Start/Stop Services

```bash
# Start all (recommended)
./scripts/start-integrated.sh

# Or start individually
./venv/bin/python main_voice.py &
./venv/bin/python main_browser_service.py &
cd frontend && npm run dev &

# Stop all
pkill -f "python main_"
pkill -f "npm run dev"
```

## Test Browser Agent

```bash
# Simple test
curl -X POST http://localhost:7863/api/execute \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Open google.com", "session_id": "test-001"}'

# Test with form
curl -X POST http://localhost:7863/api/execute \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Fill loan form with name John Doe", "session_id": "test-002"}'
```

## Common Issues

### Issue: Browser timeout
**Solution**: Check BROWSER_HEADLESS=true in .env

### Issue: Rate limit
**Solution**: Wait 60s between requests or use different API key

### Issue: Import errors
**Solution**: 
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Key Files

- `src/browser_agent.py` - Browser automation
- `src/voice_bot.py` - Voice interaction
- `main_browser_service.py` - Browser service entry
- `main_voice.py` - Voice service entry
- `.env` - Configuration

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...

# Important
BROWSER_HEADLESS=true
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-...
```

## Logs

```bash
# View logs
tail -f logs/browser_agent.log
tail -f logs/voice_bot.log

# Check for errors
grep ERROR logs/browser_agent.log
```

## Testing

```bash
# Run test script
./venv/bin/python test_browser_use.py

# Run unit tests (when ready)
pytest tests/ -v

# Check coverage
pytest --cov=src --cov-report=html
```

## Quick Fixes

```bash
# Restart browser service
pkill -f main_browser_service
./venv/bin/python main_browser_service.py &

# Clear cache
rm -rf __pycache__ src/__pycache__

# Reinstall browser-use
pip uninstall browser-use -y
pip install browser-use==0.1.19
```

## Next Steps

1. Test loan form: See FINAL_STATUS.md
2. Test all 5 forms: See REQUIREMENTS_ANALYSIS.md
3. Prepare demo: See SUCCESS_SUMMARY.md
4. Full testing: See FINAL_RECOMMENDATIONS.md

## Support

- Documentation: README.md
- Requirements: REQUIREMENTS_ANALYSIS.md
- Status: FINAL_STATUS.md
- Success: SUCCESS_SUMMARY.md
