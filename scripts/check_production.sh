#!/bin/bash

echo "🔍 Production Health Check (AWS US-East-1)"
echo "=========================================="

# Check Browser Agent
echo -n "Browser Agent (7863): "
if curl -s http://localhost:7863/api/health > /dev/null 2>&1; then
    echo "✅ HEALTHY"
else
    echo "❌ DOWN"
fi

# Check Voice Bot
echo -n "Voice Bot (7860): "
if curl -s http://localhost:7860 > /dev/null 2>&1; then
    echo "✅ HEALTHY"
else
    echo "❌ DOWN"
fi

# Check processes
echo ""
echo "📊 Running Processes:"
ps aux | grep -E "main_browser_service|main_voice" | grep -v grep || echo "No services running"

# Show recent logs
echo ""
echo "📝 Recent Logs (last 5 lines):"
echo "--- Browser Agent ---"
tail -5 logs/browser_agent.log 2>/dev/null || echo "No logs"
echo ""
echo "--- Voice Bot ---"
tail -5 logs/voice_bot.log 2>/dev/null || echo "No logs"
