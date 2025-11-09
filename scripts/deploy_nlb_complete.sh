#!/bin/bash
# Deploy NLB for WebRTC with proper architecture
# Internet → NLB (TCP + UDP) → ECS Fargate Tasks

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Deploying NLB for WebRTC - Complete Architecture       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
VPC_ID="vpc-0c4b057a76475d2d3"
SUBNETS="subnet-032b3bf427f76f3d4 subnet-033c0656eb5a0863c subnet-0b41a62d59b3ce52b subnet-0cafbb4db292f75c2 subnet-0f091e4379d5edb27 subnet-0f90d82ab535b9a3d"
CLUSTER_NAME="vpbank-voice-agent-cluster"
AWS_REGION="us-east-1"

echo -e "${YELLOW}Configuration:${NC}"
echo "  VPC: $VPC_ID"
echo "  Region: $AWS_REGION"
echo "  Cluster: $CLUSTER_NAME"
echo ""

# Check if NLB already exists
EXISTING_NLB=$(aws elbv2 describe-load-balancers \
    --names vpbank-voice-agent-nlb \
    --region $AWS_REGION 2>&1 || echo "not found")

if [[ "$EXISTING_NLB" != "not found" ]] && [[ "$EXISTING_NLB" != *"LoadBalancerNotFound"* ]]; then
    echo -e "${YELLOW}NLB already exists. Deleting old NLB first...${NC}"
    NLB_ARN=$(echo "$EXISTING_NLB" | jq -r '.LoadBalancers[0].LoadBalancerArn')
    aws elbv2 delete-load-balancer --load-balancer-arn "$NLB_ARN" --region $AWS_REGION
    echo "Waiting for deletion..."
    sleep 30
fi

echo -e "${BLUE}═══ Step 1: Creating Network Load Balancer ═══${NC}"

NLB_ARN=$(aws elbv2 create-load-balancer \
    --name vpbank-voice-agent-nlb \
    --type network \
    --scheme internet-facing \
    --subnets $SUBNETS \
    --tags Key=Name,Value=vpbank-voice-agent-nlb Key=Environment,Value=production Key=Purpose,Value=WebRTC \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text)

echo -e "${GREEN}✓ NLB Created${NC}"
echo "  ARN: $NLB_ARN"

NLB_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns "$NLB_ARN" \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

echo -e "${GREEN}✓ NLB DNS: ${BLUE}$NLB_DNS${NC}"
echo ""

echo -e "${BLUE}═══ Step 2: Creating Target Groups ═══${NC}"

# Target Group 1: TCP 7860 (Voice Bot - HTTP/WebSocket/WebRTC Signaling)
echo -e "${YELLOW}Creating TCP 7860 target group (Voice Bot)...${NC}"
TG_VOICE_TCP=$(aws elbv2 create-target-group \
    --name vpbank-nlb-voice-tcp \
    --protocol TCP \
    --port 7860 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-enabled \
    --health-check-protocol HTTP \
    --health-check-path /health \
    --health-check-port 7860 \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 2 \
    --region $AWS_REGION \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)
echo -e "${GREEN}✓ Voice Bot TCP: $TG_VOICE_TCP${NC}"

# Target Group 2: TCP 7863 (Browser Agent)
echo -e "${YELLOW}Creating TCP 7863 target group (Browser Agent)...${NC}"
TG_BROWSER_TCP=$(aws elbv2 create-target-group \
    --name vpbank-nlb-browser-tcp \
    --protocol TCP \
    --port 7863 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-enabled \
    --health-check-protocol HTTP \
    --health-check-path /api/health \
    --health-check-port 7863 \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 2 \
    --region $AWS_REGION \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)
echo -e "${GREEN}✓ Browser Agent TCP: $TG_BROWSER_TCP${NC}"

# Target Group 3: UDP 3478 (STUN)
echo -e "${YELLOW}Creating UDP 3478 target group (STUN)...${NC}"
TG_STUN_UDP=$(aws elbv2 create-target-group \
    --name vpbank-nlb-stun-udp \
    --protocol UDP \
    --port 3478 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-enabled \
    --health-check-protocol TCP \
    --health-check-port 7860 \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 2 \
    --region $AWS_REGION \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)
echo -e "${GREEN}✓ STUN UDP: $TG_STUN_UDP${NC}"

# Target Group 4: UDP 50000 (WebRTC Media - representative port)
echo -e "${YELLOW}Creating UDP 50000 target group (WebRTC Media)...${NC}"
TG_MEDIA_UDP=$(aws elbv2 create-target-group \
    --name vpbank-nlb-media-udp \
    --protocol UDP \
    --port 50000 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-enabled \
    --health-check-protocol TCP \
    --health-check-port 7860 \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 2 \
    --region $AWS_REGION \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)
echo -e "${GREEN}✓ WebRTC Media UDP: $TG_MEDIA_UDP${NC}"
echo ""

echo -e "${BLUE}═══ Step 3: Creating Listeners ═══${NC}"

# Listener 1: TCP 7860
echo -e "${YELLOW}Creating TCP 7860 listener...${NC}"
aws elbv2 create-listener \
    --load-balancer-arn "$NLB_ARN" \
    --protocol TCP \
    --port 7860 \
    --default-actions Type=forward,TargetGroupArn="$TG_VOICE_TCP" \
    --region $AWS_REGION > /dev/null
echo -e "${GREEN}✓ TCP 7860 Listener (Voice Bot)${NC}"

# Listener 2: TCP 7863
echo -e "${YELLOW}Creating TCP 7863 listener...${NC}"
aws elbv2 create-listener \
    --load-balancer-arn "$NLB_ARN" \
    --protocol TCP \
    --port 7863 \
    --default-actions Type=forward,TargetGroupArn="$TG_BROWSER_TCP" \
    --region $AWS_REGION > /dev/null
echo -e "${GREEN}✓ TCP 7863 Listener (Browser Agent)${NC}"

# Listener 3: UDP 3478
echo -e "${YELLOW}Creating UDP 3478 listener...${NC}"
aws elbv2 create-listener \
    --load-balancer-arn "$NLB_ARN" \
    --protocol UDP \
    --port 3478 \
    --default-actions Type=forward,TargetGroupArn="$TG_STUN_UDP" \
    --region $AWS_REGION > /dev/null
echo -e "${GREEN}✓ UDP 3478 Listener (STUN)${NC}"

# Listener 4: UDP 50000
echo -e "${YELLOW}Creating UDP 50000 listener...${NC}"
aws elbv2 create-listener \
    --load-balancer-arn "$NLB_ARN" \
    --protocol UDP \
    --port 50000 \
    --default-actions Type=forward,TargetGroupArn="$TG_MEDIA_UDP" \
    --region $AWS_REGION > /dev/null
echo -e "${GREEN}✓ UDP 50000 Listener (WebRTC Media)${NC}"
echo ""

echo -e "${YELLOW}Waiting for NLB to become active...${NC}"
aws elbv2 wait load-balancer-available --load-balancer-arns "$NLB_ARN" --region $AWS_REGION
echo -e "${GREEN}✓ NLB is ACTIVE${NC}"
echo ""

# Save configuration
cat > /tmp/nlb_config.json <<EOF
{
  "nlb_arn": "$NLB_ARN",
  "nlb_dns": "$NLB_DNS",
  "target_groups": {
    "voice_tcp_7860": "$TG_VOICE_TCP",
    "browser_tcp_7863": "$TG_BROWSER_TCP",
    "stun_udp_3478": "$TG_STUN_UDP",
    "media_udp_50000": "$TG_MEDIA_UDP"
  }
}
EOF

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              NLB Deployment Complete!                     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}NLB Details:${NC}"
echo "  Name:   vpbank-voice-agent-nlb"
echo "  DNS:    ${BLUE}$NLB_DNS${NC}"
echo "  ARN:    $NLB_ARN"
echo ""
echo -e "${GREEN}Architecture:${NC}"
echo "  Internet"
echo "     ↓"
echo "  NLB (Network Load Balancer)"
echo "     ├─ TCP 7860  → Voice Bot (HTTP/WebSocket/Signaling)"
echo "     ├─ TCP 7863  → Browser Agent (HTTP API)"
echo "     ├─ UDP 3478  → STUN Server"
echo "     └─ UDP 50000 → WebRTC Media (50000-50100 range)"
echo "     ↓"
echo "  ECS Fargate Tasks (awsvpc mode)"
echo ""
echo -e "${GREEN}Target Groups:${NC}"
echo "  Voice TCP:   $TG_VOICE_TCP"
echo "  Browser TCP: $TG_BROWSER_TCP"
echo "  STUN UDP:    $TG_STUN_UDP"
echo "  Media UDP:   $TG_MEDIA_UDP"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Update ECS Voice Bot service with NLB target group"
echo "  2. Update ECS Browser Agent service with NLB target group"
echo "  3. Update frontend to use: http://$NLB_DNS:7860"
echo "  4. Test WebRTC connection"
echo ""
echo -e "${GREEN}Config saved to: /tmp/nlb_config.json${NC}"
