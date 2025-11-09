#!/bin/bash
set -e

echo "🚀 Deploying to AWS US-East-1 Production..."

# Stop all services
pkill -f main_browser_service.py || true
pkill -f main_voice.py || true
sleep 2

# Pull latest code
git pull origin main

# Activate venv
source venv/bin/activate

# Install/update dependencies
pip install -q -r requirements.txt

# Create logs directory
mkdir -p logs

# Start Browser Agent (port 7863)
nohup python main_browser_service.py > logs/browser_agent.log 2>&1 &
BROWSER_PID=$!
echo "✅ Browser Agent started (PID: $BROWSER_PID)"

# Wait for browser agent to be ready
sleep 5
curl -s http://localhost:7863/api/health || echo "⚠️ Browser agent not ready"

# Start Voice Bot (port 7860)
nohup python main_voice.py > logs/voice_bot.log 2>&1 &
VOICE_PID=$!
echo "✅ Voice Bot started (PID: $VOICE_PID)"

# Wait for voice bot to be ready
sleep 5
curl -s http://localhost:7860 || echo "⚠️ Voice bot not ready"

echo ""
echo "🎉 Production deployment complete!"
echo "📊 Services:"
echo "   - Browser Agent: http://localhost:7863"
echo "   - Voice Bot: http://localhost:7860"
echo "   - Frontend: http://localhost:5173"
echo ""
echo "📝 Logs:"
echo "   - Browser: tail -f logs/browser_agent.log"
echo "   - Voice: tail -f logs/voice_bot.log"
