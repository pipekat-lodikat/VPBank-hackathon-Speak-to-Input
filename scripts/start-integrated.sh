#!/bin/bash
# Start all services with integrated features
# Enhanced version with monitoring, logging, and performance optimizations

set -e

echo "🚀 Starting VPBank Voice Agent - Enhanced Edition"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3.11 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -q -r requirements.txt
pip install -q -r requirements-test.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Please create it from .env.example${NC}"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"
    jobs -p | xargs -r kill
    echo -e "${GREEN}✅ All services stopped${NC}"
}

trap cleanup EXIT INT TERM

# Start Browser Agent (port 7863)
echo -e "${GREEN}🌐 Starting Browser Agent Service (port 7863)...${NC}"
python main_browser_service.py > logs/browser_agent_console.log 2>&1 &
BROWSER_PID=$!
echo -e "   PID: $BROWSER_PID"
sleep 3

# Check if Browser Agent started successfully
if ! curl -sf http://localhost:7863/api/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Browser Agent health check failed, waiting longer...${NC}"
    sleep 5
    if ! curl -sf http://localhost:7863/api/health > /dev/null 2>&1; then
        echo -e "${YELLOW}❌ Browser Agent failed to start. Check logs/browser_agent_console.log${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}   ✅ Browser Agent ready${NC}"
echo -e "${BLUE}   📊 Metrics: http://localhost:7863/metrics${NC}"

# Start Voice Bot with integrations (port 7860)
echo -e "${GREEN}🎤 Starting Enhanced Voice Bot Service (port 7860)...${NC}"
python main_voice_integrated.py > logs/voice_bot_console.log 2>&1 &
VOICE_PID=$!
echo -e "   PID: $VOICE_PID"
sleep 5

# Check if Voice Bot started successfully
if ! curl -sf http://localhost:7860/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Voice Bot health check failed, waiting longer...${NC}"
    sleep 5
    if ! curl -sf http://localhost:7860/health > /dev/null 2>&1; then
        echo -e "${YELLOW}❌ Voice Bot failed to start. Check logs/voice_bot_console.log${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}   ✅ Voice Bot ready${NC}"
echo -e "${BLUE}   📊 Metrics: http://localhost:7860/metrics${NC}"

# Start Frontend (port 5173)
echo -e "${GREEN}🎨 Starting Frontend (port 5173)...${NC}"
cd frontend
npm run dev -- --host 0.0.0.0 > ../logs/frontend_console.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "   PID: $FRONTEND_PID"
sleep 3

echo ""
echo -e "${GREEN}=============================================="
echo -e "✅ All services started successfully!"
echo -e "==============================================

${NC}"
echo ""
echo -e "${BLUE}📋 Service URLs:${NC}"
echo -e "   🎨 Frontend:        http://localhost:5173"
echo -e "   🎤 Voice Bot:       http://localhost:7860"
echo -e "   🌐 Browser Agent:   http://localhost:7863"
echo ""
echo -e "${BLUE}📊 Monitoring Endpoints:${NC}"
echo -e "   Voice Bot Metrics:  http://localhost:7860/metrics"
echo -e "   Browser Metrics:    http://localhost:7863/metrics"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "   Voice Bot:          logs/voice_bot_console.log"
echo -e "   Browser Agent:      logs/browser_agent_console.log"
echo -e "   Frontend:           logs/frontend_console.log"
echo ""
echo -e "${YELLOW}💡 Enhanced Features Active:${NC}"
echo -e "   ✅ Prometheus metrics monitoring"
echo -e "   ✅ Correlation ID tracking"
echo -e "   ✅ LLM response caching (cost savings)"
echo -e "   ✅ Request debouncing (2s delay)"
echo -e "   ✅ Structured exception handling"
echo -e "   ✅ Advanced logging with rotation"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for all background jobs
wait

