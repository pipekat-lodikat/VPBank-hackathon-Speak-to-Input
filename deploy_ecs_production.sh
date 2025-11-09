#!/bin/bash
set -e

echo "🚀 Deploying to ECS Fargate + CloudFront (US-East-1)"

# Variables
AWS_REGION="us-east-1"
ECR_REPO_BROWSER="vpbank-browser-agent"
ECR_REPO_VOICE="vpbank-voice-bot"
ECR_REPO_FRONTEND="vpbank-frontend"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build and push Docker images
echo "📦 Building Docker images..."

# Browser Agent
docker build -t $ECR_REPO_BROWSER:latest -f Dockerfile.browser .
docker tag $ECR_REPO_BROWSER:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_BROWSER:latest
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_BROWSER:latest

# Voice Bot
docker build -t $ECR_REPO_VOICE:latest -f Dockerfile.voice .
docker tag $ECR_REPO_VOICE:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_VOICE:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_VOICE:latest

# Frontend
docker build -t $ECR_REPO_FRONTEND:latest -f Dockerfile.frontend .
docker tag $ECR_REPO_FRONTEND:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:latest

echo "✅ Images pushed to ECR"

# Deploy with Terraform
echo "🏗️ Deploying infrastructure..."
cd infrastructure/terraform
terraform init
terraform apply -auto-approve

echo "🎉 Deployment complete!"
terraform output
