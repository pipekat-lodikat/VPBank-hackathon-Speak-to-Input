#!/bin/bash
set -e

REGION="us-east-1"
ACCOUNT_ID="590183822512"
CLUSTER="vpbank-voice-agent-cluster"

echo "🔄 Updating VPBank Voice Agent on ECS"
echo "======================================"

# Login to ECR
echo "▶ Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build Voice Bot
echo "▶ Building Voice Bot image..."
docker build -t vpbank-voice-bot:latest -f Dockerfile .

# Tag and push Voice Bot
echo "▶ Pushing Voice Bot to ECR..."
docker tag vpbank-voice-bot:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/vpbank-voice-agent-voice-bot:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/vpbank-voice-agent-voice-bot:latest

# Force new deployment
echo "▶ Forcing new deployment of voice-bot service..."
aws ecs update-service \
    --cluster $CLUSTER \
    --service voice-bot \
    --force-new-deployment \
    --region $REGION

echo ""
echo "✅ Update initiated!"
echo ""
echo "Monitor deployment:"
echo "  aws ecs describe-services --cluster $CLUSTER --services voice-bot --region $REGION"
echo ""
echo "View logs:"
echo "  aws logs tail /ecs/vpbank-voice-bot --follow --region $REGION"
