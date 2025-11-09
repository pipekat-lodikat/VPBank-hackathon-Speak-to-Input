#!/bin/bash
# Filter production logs to show only legitimate traffic
# Filters out malicious requests, health checks, and noise

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SERVICE="${1:-voice-bot}"
HOURS="${2:-1}"
OUTPUT_FILE="${3:-}"

echo -e "${BLUE}=== Production Log Filter ===${NC}"
echo "Service: $SERVICE"
echo "Time range: Last ${HOURS} hour(s)"
echo ""

# Determine log group
if [ "$SERVICE" == "voice-bot" ]; then
    LOG_GROUP="/ecs/vpbank-voice-agent/voice-bot"
elif [ "$SERVICE" == "browser-agent" ]; then
    LOG_GROUP="/ecs/vpbank-voice-agent/browser-agent"
else
    echo -e "${RED}Error: Invalid service. Use 'voice-bot' or 'browser-agent'${NC}"
    exit 1
fi

echo -e "${YELLOW}Fetching logs from $LOG_GROUP...${NC}"

# Fetch and filter logs
aws logs tail "$LOG_GROUP" --since "${HOURS}h" --format short 2>&1 | \
    grep -v "Error handling request from 172.31.78.80" | \
    grep -v "BadHttpMethod" | \
    grep -v "BadHttpMessage" | \
    grep -v "Invalid method encountered" | \
    grep -v "Expected HTTP/, RTSP/ or ICE/" | \
    grep -v "ELB-HealthChecker" | \
    grep -v "GET /api/health" | \
    grep -v "curl/8.14.1" > /tmp/filtered_logs.txt || true

# Count events
TOTAL_LINES=$(wc -l < /tmp/filtered_logs.txt)

echo -e "${GREEN}✓ Filtered logs ready${NC}"
echo "Total legitimate log entries: $TOTAL_LINES"
echo ""

# Extract key metrics
echo -e "${BLUE}=== Key Metrics ===${NC}"

# WebRTC sessions
SESSIONS=$(grep -c "Starting voice bot" /tmp/filtered_logs.txt || echo "0")
echo -e "${GREEN}WebRTC Sessions Started: $SESSIONS${NC}"

# Session completions
COMPLETED=$(grep -c "Session completed" /tmp/filtered_logs.txt || echo "0")
echo -e "${GREEN}Sessions Completed: $COMPLETED${NC}"

# WebSocket connections
WS_CONNECTED=$(grep -c "WebSocket connected" /tmp/filtered_logs.txt || echo "0")
WS_DISCONNECTED=$(grep -c "WebSocket disconnected" /tmp/filtered_logs.txt || echo "0")
echo -e "${GREEN}WebSocket Connections: $WS_CONNECTED${NC}"
echo -e "${YELLOW}WebSocket Disconnections: $WS_DISCONNECTED${NC}"

# Errors (excluding malicious requests)
ERRORS=$(grep -c "ERROR" /tmp/filtered_logs.txt || echo "0")
WARNINGS=$(grep -c "WARNING" /tmp/filtered_logs.txt || echo "0")
echo -e "${RED}Errors: $ERRORS${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"

# DynamoDB operations
DYNAMODB_SAVES=$(grep -c "Saved session.*to DynamoDB" /tmp/filtered_logs.txt || echo "0")
echo -e "${GREEN}DynamoDB Saves: $DYNAMODB_SAVES${NC}"

echo ""
echo -e "${BLUE}=== Recent Legitimate Activity ===${NC}"

# Show recent user sessions
echo -e "${YELLOW}User Sessions:${NC}"
grep -E "(Starting voice bot|Session completed|Saved session)" /tmp/filtered_logs.txt | tail -10

echo ""
echo -e "${YELLOW}WebRTC Connection Events:${NC}"
grep -E "(WebRTC connection|ICE connection|Received WebRTC offer)" /tmp/filtered_logs.txt | tail -10

echo ""
echo -e "${YELLOW}Recent Errors (excluding malicious requests):${NC}"
grep -E "(ERROR|CRITICAL)" /tmp/filtered_logs.txt | tail -10

echo ""
echo -e "${YELLOW}Recent Warnings:${NC}"
grep "WARNING" /tmp/filtered_logs.txt | tail -10

# Save to file if specified
if [ -n "$OUTPUT_FILE" ]; then
    cp /tmp/filtered_logs.txt "$OUTPUT_FILE"
    echo -e "${GREEN}✓ Full filtered logs saved to: $OUTPUT_FILE${NC}"
fi

echo ""
echo -e "${BLUE}=== Analysis Complete ===${NC}"
