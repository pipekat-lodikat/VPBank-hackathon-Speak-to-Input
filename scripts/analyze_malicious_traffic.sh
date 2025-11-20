#!/bin/bash
# Analyze malicious traffic patterns in production logs

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}=== Malicious Traffic Analysis ===${NC}"
echo ""

LOG_GROUP="/ecs/vpbank-voice-agent/voice-bot"

echo -e "${YELLOW}Analyzing malicious request patterns from last 2 hours...${NC}"

# Get malicious requests
aws logs tail "$LOG_GROUP" --since 2h --format short 2>&1 | \
    grep "Error handling request from 172.31.78.80" -A 5 > /tmp/malicious_requests.txt || true

TOTAL_MALICIOUS=$(grep -c "Error handling request" /tmp/malicious_requests.txt || echo "0")

echo -e "${RED}Total malicious requests: $TOTAL_MALICIOUS${NC}"
echo ""

echo -e "${BLUE}=== Attack Patterns Detected ===${NC}"

# Analyze attack types
echo -e "${YELLOW}1. WebLogic Console RCE attempts:${NC}"
WEBLOGIC=$(grep -c "console/bea-helpsets" /tmp/malicious_requests.txt || echo "0")
echo "   Count: $WEBLOGIC"
grep "console/bea-helpsets" /tmp/malicious_requests.txt | head -2 | sed 's/^/   /'

echo ""
echo -e "${YELLOW}2. SendMail injection attempts:${NC}"
SENDMAIL=$(grep -c "sendmail" /tmp/malicious_requests.txt || echo "0")
echo "   Count: $SENDMAIL"
grep "sendmail" /tmp/malicious_requests.txt | head -2 | sed 's/^/   /'

echo ""
echo -e "${YELLOW}3. Invalid HTTP methods:${NC}"
INVALID_METHOD=$(grep -c "BadHttpMethod" /tmp/malicious_requests.txt || echo "0")
echo "   Count: $INVALID_METHOD"
grep "BadHttpMethod" /tmp/malicious_requests.txt | head -2 | sed 's/^/   /'

echo ""
echo -e "${YELLOW}4. Protocol violations:${NC}"
PROTOCOL=$(grep -c "Expected HTTP/, RTSP/ or ICE/" /tmp/malicious_requests.txt || echo "0")
echo "   Count: $PROTOCOL"

echo ""
echo -e "${BLUE}=== Source Analysis ===${NC}"
echo -e "${YELLOW}The IP 172.31.78.80 is the Application Load Balancer's internal interface.${NC}"
echo "This means malicious requests are coming from the internet through the ALB."
echo ""
echo "The actual source IPs are external attackers/scanners."
echo "Recommendation: Implement AWS WAF to block these requests at the edge."

echo ""
echo -e "${BLUE}=== Attack Timeline ===${NC}"
echo "Showing request frequency over time:"
grep "Error handling request" /tmp/malicious_requests.txt | \
    awk '{print $1}' | \
    uniq -c | \
    tail -20

echo ""
echo -e "${GREEN}=== Recommendations ===${NC}"
echo "1. ✓ Backend is rejecting these requests (no security impact)"
echo "2. ⚠️  Deploy AWS WAF to block malicious patterns at ALB level"
echo "3. ⚠️  Enable ALB access logs to capture original source IPs"
echo "4. ⚠️  Implement rate limiting to prevent DDoS attempts"
echo "5. ⚠️  Add CloudFront custom error pages to hide backend errors"

echo ""
echo -e "${BLUE}=== Analysis Complete ===${NC}"
