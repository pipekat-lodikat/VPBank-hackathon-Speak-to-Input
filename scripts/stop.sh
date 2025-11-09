#!/bin/bash

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping all VPBank Voice AI services...${NC}\n"

# Stop processes by port
echo -e "${YELLOW}Stopping Frontend (port 5173)...${NC}"
lsof -ti:5173 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✓ Frontend stopped${NC}" || echo -e "${RED}✗ Frontend not running${NC}"

echo -e "${YELLOW}Stopping Voice Service (port 7860)...${NC}"
lsof -ti:7860 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✓ Voice Service stopped${NC}" || echo -e "${RED}✗ Voice Service not running${NC}"

echo -e "${YELLOW}Stopping Browser Service (port 7863)...${NC}"
lsof -ti:7863 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✓ Browser Service stopped${NC}" || echo -e "${RED}✗ Browser Service not running${NC}"

# Also kill any Python processes running the main scripts
pkill -f "python main_voice.py" 2>/dev/null
pkill -f "python main_browser_service.py" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null

echo -e "\n${GREEN}All services stopped!${NC}"
