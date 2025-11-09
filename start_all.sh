#!/bin/bash
# VPBank Voice Agent - Start All Services

set -e

echo "🚀 Starting VPBank Voice Agent..."

# Navigate to project directory
cd /home/ubuntu/speak-to-input

# Activate virtual environment
source venv/bin/activate

# Kill existing processes
echo "🔄 Stopping existing services..."
pkill -f "main_browser_service.py" 2>/dev/null || true
pkill -f "main_voice.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 2

# Start Browser Agent
echo "🌐 Starting Browser Agent (port 7863)..."
nohup python main_browser_service.py > /tmp/browser.log 2>&1 &
sleep 3

# Start Voice Bot
echo "🎤 Starting Voice Bot (port 7860)..."
nohup python main_voice.py > /tmp/voice.log 2>&1 &
sleep 3

# Start Frontend
echo "💻 Starting Frontend (port 5173)..."
cd frontend
nohup npm run dev -- --host 0.0.0.0 > /tmp/frontend.log 2>&1 &
sleep 3

# Check services
echo ""
echo "✅ Services Status:"
curl -s http://localhost:7863/api/health | jq -r '"Browser Agent: " + .status' 2>/dev/null || echo "Browser Agent: Starting..."
curl -s -o /dev/null -w "Voice Bot: %{http_code}\n" http://localhost:7860/
curl -s -o /dev/null -w "Frontend: %{http_code}\n" http://localhost:5173/

echo ""
echo "🎯 Access URLs:"
echo "   Frontend: http://52.221.76.226:5173"
echo "   Voice Bot: http://52.221.76.226:7860"
echo "   Browser Agent: http://52.221.76.226:7863"
echo ""
echo "📋 Logs:"
echo "   tail -f /tmp/browser.log"
echo "   tail -f /tmp/voice.log"
echo "   tail -f /tmp/frontend.log"
