# Production Deployment Guide - AWS US-East-1

## Architecture
```
CloudFront (CDN) → ALB → ECS Fargate
                         ├── Browser Agent (7863)
                         ├── Voice Bot (7860)
                         └── Frontend (80)
```

## Quick Deploy

### Option 1: Full Deploy (with Docker build)
```bash
./deploy_ecs_production.sh
```

### Option 2: Infrastructure Only
```bash
./quick_deploy_ecs.sh
```

## Manual Steps

### 1. Create ECR Repositories
```bash
aws ecr create-repository --repository-name vpbank-browser-agent --region us-east-1
aws ecr create-repository --repository-name vpbank-voice-bot --region us-east-1
aws ecr create-repository --repository-name vpbank-frontend --region us-east-1
```

### 2. Build & Push Images
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t vpbank-browser-agent:latest -f Dockerfile.browser .
docker tag vpbank-browser-agent:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/vpbank-browser-agent:latest
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/vpbank-browser-agent:latest
```

### 3. Deploy Infrastructure
```bash
cd infrastructure/terraform
terraform init
terraform apply
```

## Access URLs

After deployment:
- **Frontend**: `https://<cloudfront-domain>`
- **Voice Bot**: `http://<alb-dns>:7860`
- **Browser Agent**: `http://<alb-dns>:7863`

Get URLs:
```bash
cd infrastructure/terraform
terraform output
```

## Monitoring

```bash
# Check ECS tasks
aws ecs list-tasks --cluster vpbank-cluster --region us-east-1

# View logs
aws logs tail /ecs/vpbank-browser-agent --follow
aws logs tail /ecs/vpbank-voice-bot --follow
```

## Update Deployment

```bash
# Rebuild and push new images
./deploy_ecs_production.sh

# Force new deployment
aws ecs update-service --cluster vpbank-cluster --service browser-agent --force-new-deployment --region us-east-1
aws ecs update-service --cluster vpbank-cluster --service voice-bot --force-new-deployment --region us-east-1
```

## Cost Estimate

- **ECS Fargate**: ~$50-100/month (2 tasks, 0.5 vCPU, 1GB RAM each)
- **ALB**: ~$20/month
- **CloudFront**: ~$10-50/month (depends on traffic)
- **Total**: ~$80-170/month

## Cleanup

```bash
cd infrastructure/terraform
terraform destroy -auto-approve
```
