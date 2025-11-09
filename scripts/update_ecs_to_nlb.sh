#!/bin/bash
# Update ECS services to use NLB instead of ALB

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Updating ECS Services to Use NLB                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
CLUSTER="vpbank-voice-agent-cluster"
REGION="us-east-1"

# Read NLB config
NLB_CONFIG=$(cat /tmp/nlb_config.json)
TG_VOICE=$(echo "$NLB_CONFIG" | jq -r '.target_groups.voice_tcp_7860')
TG_BROWSER=$(echo "$NLB_CONFIG" | jq -r '.target_groups.browser_tcp_7863')

echo -e "${YELLOW}Target Groups:${NC}"
echo "  Voice Bot:    $TG_VOICE"
echo "  Browser Agent: $TG_BROWSER"
echo ""

# Network configuration (same for both services)
SUBNETS="subnet-032b3bf427f76f3d4,subnet-033c0656eb5a0863c,subnet-0cafbb4db292f75c2,subnet-0f90d82ab535b9a3d,subnet-0b41a62d59b3ce52b,subnet-0f091e4379d5edb27"
SECURITY_GROUP="sg-02c87c9c66309b96d"

# Get current task definitions
VOICE_TASK_DEF=$(aws ecs describe-services --cluster $CLUSTER --services voice-bot --region $REGION --query 'services[0].taskDefinition' --output text)
BROWSER_TASK_DEF=$(aws ecs describe-services --cluster $CLUSTER --services browser-agent --region $REGION --query 'services[0].taskDefinition' --output text)

echo -e "${BLUE}═══ Step 1: Scaling down existing services ═══${NC}"
echo -e "${YELLOW}Scaling Voice Bot to 0...${NC}"
aws ecs update-service --cluster $CLUSTER --service voice-bot --desired-count 0 --region $REGION > /dev/null
echo -e "${GREEN}✓ Voice Bot scaled to 0${NC}"

echo -e "${YELLOW}Scaling Browser Agent to 0...${NC}"
aws ecs update-service --cluster $CLUSTER --service browser-agent --desired-count 0 --region $REGION > /dev/null
echo -e "${GREEN}✓ Browser Agent scaled to 0${NC}"

echo ""
echo -e "${YELLOW}Waiting for tasks to drain (30 seconds)...${NC}"
sleep 30

echo ""
echo -e "${BLUE}═══ Step 2: Deleting old services ═══${NC}"
echo -e "${YELLOW}Deleting Voice Bot service...${NC}"
aws ecs delete-service --cluster $CLUSTER --service voice-bot --region $REGION > /dev/null
echo -e "${GREEN}✓ Voice Bot service deleted${NC}"

echo -e "${YELLOW}Deleting Browser Agent service...${NC}"
aws ecs delete-service --cluster $CLUSTER --service browser-agent --region $REGION > /dev/null
echo -e "${GREEN}✓ Browser Agent service deleted${NC}"

echo ""
echo -e "${YELLOW}Waiting for service deletion to complete (60 seconds)...${NC}"
sleep 60

echo ""
echo -e "${BLUE}═══ Step 3: Creating Voice Bot service with NLB ═══${NC}"
aws ecs create-service \
    --cluster $CLUSTER \
    --service-name voice-bot \
    --task-definition "$VOICE_TASK_DEF" \
    --desired-count 2 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$TG_VOICE,containerName=voice-bot,containerPort=7860" \
    --health-check-grace-period-seconds 60 \
    --region $REGION > /dev/null

echo -e "${GREEN}✓ Voice Bot service created with NLB${NC}"

echo ""
echo -e "${BLUE}═══ Step 4: Creating Browser Agent service with NLB ═══${NC}"
aws ecs create-service \
    --cluster $CLUSTER \
    --service-name browser-agent \
    --task-definition "$BROWSER_TASK_DEF" \
    --desired-count 2 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$TG_BROWSER,containerName=browser-agent,containerPort=7863" \
    --health-check-grace-period-seconds 60 \
    --region $REGION > /dev/null

echo -e "${GREEN}✓ Browser Agent service created with NLB${NC}"

echo ""
echo -e "${BLUE}═══ Step 5: Waiting for services to stabilize ═══${NC}"
echo -e "${YELLOW}Waiting for Voice Bot...${NC}"
aws ecs wait services-stable --cluster $CLUSTER --services voice-bot --region $REGION
echo -e "${GREEN}✓ Voice Bot is stable${NC}"

echo -e "${YELLOW}Waiting for Browser Agent...${NC}"
aws ecs wait services-stable --cluster $CLUSTER --services browser-agent --region $REGION
echo -e "${GREEN}✓ Browser Agent is stable${NC}"

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         ECS Services Updated Successfully!                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check service status
echo -e "${GREEN}Service Status:${NC}"
aws ecs describe-services --cluster $CLUSTER --services voice-bot browser-agent --region $REGION \
    --query 'services[].{Name:serviceName,Running:runningCount,Desired:desiredCount,Status:status}' \
    --output table

echo ""
echo -e "${GREEN}Target Health:${NC}"
echo -e "${YELLOW}Voice Bot (TCP 7860):${NC}"
aws elbv2 describe-target-health --target-group-arn "$TG_VOICE" --region $REGION \
    --query 'TargetHealthDescriptions[].{Target:Target.Id,Health:TargetHealth.State}' \
    --output table

echo ""
echo -e "${YELLOW}Browser Agent (TCP 7863):${NC}"
aws elbv2 describe-target-health --target-group-arn "$TG_BROWSER" --region $REGION \
    --query 'TargetHealthDescriptions[].{Target:Target.Id,Health:TargetHealth.State}' \
    --output table

echo ""
echo -e "${BLUE}Next Step:${NC}"
echo "  Update frontend to use NLB endpoint"
