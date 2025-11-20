#!/bin/bash
# Multi-Region Deployment Script
# Deploy VPBank Voice Agent to multiple AWS regions

set -e

REGIONS=("us-east-1" "ap-southeast-1" "eu-west-1")
SERVICE_NAME="vpbank-voice-agent"

echo "🌍 Multi-Region Deployment for VPBank Voice Agent"
echo "=================================================="

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Function to deploy to a region
deploy_region() {
    local region=$1
    echo ""
    echo "📍 Deploying to region: $region"
    echo "--------------------------------"
    
    # Create ECR repositories if not exist
    echo "🐳 Setting up ECR in $region..."
    aws ecr describe-repositories --region $region --repository-names $SERVICE_NAME-voice-bot 2>/dev/null || \
        aws ecr create-repository --region $region --repository-name $SERVICE_NAME-voice-bot
    
    aws ecr describe-repositories --region $region --repository-names $SERVICE_NAME-browser-agent 2>/dev/null || \
        aws ecr create-repository --region $region --repository-name $SERVICE_NAME-browser-agent
    
    aws ecr describe-repositories --region $region --repository-names $SERVICE_NAME-frontend 2>/dev/null || \
        aws ecr create-repository --region $region --repository-name $SERVICE_NAME-frontend
    
    # Build and push images
    echo "🔨 Building and pushing images to $region..."
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_BASE="$ACCOUNT_ID.dkr.ecr.$region.amazonaws.com"
    
    # Login to ECR
    aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $ECR_BASE
    
    # Tag and push (assuming images already built)
    docker tag vpbank-voice-bot:latest $ECR_BASE/$SERVICE_NAME-voice-bot:latest
    docker tag vpbank-browser-agent:latest $ECR_BASE/$SERVICE_NAME-browser-agent:latest
    docker tag vpbank-frontend:latest $ECR_BASE/$SERVICE_NAME-frontend:latest
    
    docker push $ECR_BASE/$SERVICE_NAME-voice-bot:latest
    docker push $ECR_BASE/$SERVICE_NAME-browser-agent:latest
    docker push $ECR_BASE/$SERVICE_NAME-frontend:latest
    
    echo "✅ Deployment to $region completed"
}

# Deploy to all regions
for region in "${REGIONS[@]}"; do
    deploy_region $region
done

echo ""
echo "=================================================="
echo "✅ Multi-region deployment completed!"
echo ""
echo "📊 Deployed regions:"
for region in "${REGIONS[@]}"; do
    echo "   - $region"
done
echo ""
echo "🌐 Next steps:"
echo "   1. Configure Route53 for latency-based routing"
echo "   2. Setup CloudFront distribution with multiple origins"
echo "   3. Enable DynamoDB global tables"
echo "   4. Configure health checks and alarms"
