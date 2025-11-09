#!/bin/bash
set -e

echo "🚀 Starting VPBank Voice Agent - Production Mode"
echo "================================================"

cd /home/ubuntu/speak-to-input

# Activate virtual environment
source venv/bin/activate

# Stop existing services
echo "▶ Stopping existing services..."
./scripts/stop.sh 2>/dev/null || true

# Create logs directory
mkdir -p logs

# Start Browser Agent
echo "▶ Starting Browser Agent (port 7863)..."
nohup python main_browser_service.py > logs/browser_agent.log 2>&1 &
BROWSER_PID=$!
echo "  Browser Agent PID: $BROWSER_PID"

# Wait for Browser Agent to be ready
sleep 3
if ! curl -s http://localhost:7863/api/health > /dev/null; then
    echo "❌ Browser Agent failed to start"
    exit 1
fi
echo "  ✅ Browser Agent ready"

# Start Voice Bot
echo "▶ Starting Voice Bot (port 7860)..."
nohup python main_voice.py > logs/voice_bot.log 2>&1 &
VOICE_PID=$!
echo "  Voice Bot PID: $VOICE_PID"

# Wait for Voice Bot to be ready
sleep 3
if ! curl -s http://localhost:7860 > /dev/null; then
    echo "❌ Voice Bot failed to start"
    exit 1
fi
echo "  ✅ Voice Bot ready"

# Start Frontend (production build)
echo "▶ Starting Frontend (port 5173)..."
cd frontend
nohup npm run preview -- --host 0.0.0.0 --port 5173 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "  Frontend PID: $FRONTEND_PID"

sleep 2
echo ""
echo "✅ All services started successfully!"
echo ""
echo "Services:"
echo "  - Browser Agent: http://localhost:7863"
echo "  - Voice Bot:     http://localhost:7860"
echo "  - Frontend:      http://localhost:5173"
echo ""
echo "Logs:"
echo "  - Browser Agent: logs/browser_agent.log"
echo "  - Voice Bot:     logs/voice_bot.log"
echo "  - Frontend:      logs/frontend.log"
echo ""
echo "To stop: ./scripts/stop.sh"
