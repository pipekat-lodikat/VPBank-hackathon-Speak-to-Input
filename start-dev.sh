#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down all services...${NC}"
    if [ ! -z "$FRONTEND_PID" ]; then kill $FRONTEND_PID 2>/dev/null; fi
    if [ ! -z "$VOICE_PID" ]; then kill $VOICE_PID 2>/dev/null; fi
    if [ ! -z "$BROWSER_PID" ]; then kill $BROWSER_PID 2>/dev/null; fi
    exit
}

trap cleanup SIGINT SIGTERM

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Starting VPBank Voice AI Services${NC}"
echo -e "${GREEN}======================================${NC}\n"

# Create log directory
mkdir -p "$PROJECT_ROOT/logs"

# Start Frontend
echo -e "${BLUE}[1/3] Starting Frontend...${NC}"
(cd "$PROJECT_ROOT/frontend" && npm run dev 2>&1 | while IFS= read -r line; do echo -e "${CYAN}[Frontend]${NC} $line"; done) &
FRONTEND_PID=$!
sleep 2

# Start Voice Service
echo -e "${BLUE}[2/3] Starting Voice Service...${NC}"
(cd "$PROJECT_ROOT" && source venv/bin/activate && python main_voice.py 2>&1 | while IFS= read -r line; do echo -e "${GREEN}[Voice]${NC} $line"; done) &
VOICE_PID=$!
sleep 2

# Start Browser Service
echo -e "${BLUE}[3/3] Starting Browser Service...${NC}"
(cd "$PROJECT_ROOT" && source venv/bin/activate && python main_browser_service.py 2>&1 | while IFS= read -r line; do echo -e "${YELLOW}[Browser]${NC} $line"; done) &
BROWSER_PID=$!

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}All services starting!${NC}"
echo -e "${GREEN}======================================${NC}"
echo -e "Frontend:        ${BLUE}http://localhost:5173${NC}"
echo -e "Voice Service:   ${BLUE}http://localhost:7860${NC}"
echo -e "Browser Service: ${BLUE}http://localhost:7863${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"
echo -e "${GREEN}======================================${NC}\n"

# Wait for all background processes
wait
