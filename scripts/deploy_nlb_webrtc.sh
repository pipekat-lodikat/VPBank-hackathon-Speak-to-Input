#!/bin/bash
# Deploy Network Load Balancer for WebRTC Support
# NLB supports UDP traffic required for WebRTC media

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Deploying NLB for WebRTC Support ===${NC}"
echo ""

# Configuration
VPC_ID="vpc-0c4b057a76475d2d3"
SUBNETS="subnet-032b3bf427f76f3d4 subnet-033c0656eb5a0863c subnet-0b41a62d59b3ce52b subnet-0cafbb4db292f75c2 subnet-0f091e4379d5edb27 subnet-0f90d82ab535b9a3d"
CLUSTER_NAME="vpbank-voice-agent-cluster"
SERVICE_NAME="voice-bot"
AWS_REGION="us-east-1"

echo -e "${YELLOW}Step 1: Creating Network Load Balancer...${NC}"

# Create NLB
NLB_ARN=$(aws elbv2 create-load-balancer \
    --name vpbank-voice-agent-nlb \
    --type network \
    --scheme internet-facing \
    --subnets $SUBNETS \
    --tags Key=Name,Value=vpbank-voice-agent-nlb Key=Environment,Value=production \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text 2>&1)

if [[ "$NLB_ARN" == arn:aws:elasticloadbalancing:* ]]; then
    echo -e "${GREEN}✓ NLB Created: $NLB_ARN${NC}"

    # Get NLB DNS
    NLB_DNS=$(aws elbv2 describe-load-balancers \
        --load-balancer-arns "$NLB_ARN" \
        --query 'LoadBalancers[0].DNSName' \
        --output text)
    echo -e "${GREEN}✓ NLB DNS: $NLB_DNS${NC}"
else
    echo -e "${RED}Error creating NLB: $NLB_ARN${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Creating Target Groups...${NC}"

# Target Group 1: TCP 7860 (WebRTC Signaling + HTTP)
TG_TCP_ARN=$(aws elbv2 create-target-group \
    --name vpbank-va-nlb-tcp-7860 \
    --protocol TCP \
    --port 7860 \
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

echo -e "${GREEN}✓ TCP Target Group Created: $TG_TCP_ARN${NC}"

# Target Group 2: UDP 49152-65535 (WebRTC Media)
TG_UDP_ARN=$(aws elbv2 create-target-group \
    --name vpbank-va-nlb-udp-media \
    --protocol UDP \
    --port 49152 \
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

echo -e "${GREEN}✓ UDP Target Group Created: $TG_UDP_ARN${NC}"

echo ""
echo -e "${YELLOW}Step 3: Creating Listeners...${NC}"

# Listener 1: TCP 7860
aws elbv2 create-listener \
    --load-balancer-arn "$NLB_ARN" \
    --protocol TCP \
    --port 7860 \
    --default-actions Type=forward,TargetGroupArn="$TG_TCP_ARN" \
    --region $AWS_REGION > /dev/null

echo -e "${GREEN}✓ TCP Listener created on port 7860${NC}"

# Listener 2: UDP 49152-65535 (use port 50000 as representative)
aws elbv2 create-listener \
    --load-balancer-arn "$NLB_ARN" \
    --protocol UDP \
    --port 50000 \
    --default-actions Type=forward,TargetGroupArn="$TG_UDP_ARN" \
    --region $AWS_REGION > /dev/null

echo -e "${GREEN}✓ UDP Listener created on port 50000${NC}"

echo ""
echo -e "${YELLOW}Step 4: Waiting for NLB to become active...${NC}"
aws elbv2 wait load-balancer-available --load-balancer-arns "$NLB_ARN" --region $AWS_REGION
echo -e "${GREEN}✓ NLB is now active${NC}"

echo ""
echo -e "${BLUE}=== NLB Deployment Complete ===${NC}"
echo ""
echo -e "${GREEN}NLB Details:${NC}"
echo "  Name: vpbank-voice-agent-nlb"
echo "  ARN: $NLB_ARN"
echo "  DNS: $NLB_DNS"
echo "  TCP Target Group: $TG_TCP_ARN"
echo "  UDP Target Group: $TG_UDP_ARN"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update ECS service to use NLB target groups"
echo "2. Update frontend to use NLB DNS: $NLB_DNS"
echo "3. Test WebRTC connection"
echo ""

# Save configuration
cat > /tmp/nlb_config.json <<EOF
{
  "nlb_arn": "$NLB_ARN",
  "nlb_dns": "$NLB_DNS",
  "tcp_target_group": "$TG_TCP_ARN",
  "udp_target_group": "$TG_UDP_ARN"
}
EOF

echo -e "${GREEN}✓ Configuration saved to /tmp/nlb_config.json${NC}"
