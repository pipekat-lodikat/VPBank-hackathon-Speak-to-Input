# AWS Production Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Route 53 (DNS)                            │
│              vpbank-voice.yourdomain.com                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Network Load Balancer (NLB)                         │
│              TCP/UDP Support for WebRTC                      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Port 443   │  │   Port 7860  │  │   Port 7863  │      │
│  │  (Frontend)  │  │  (Voice Bot) │  │(Browser Agent)│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    ECS Fargate Cluster                       │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Frontend Service (Auto-scaling 1-3 tasks)           │   │
│  │  - React + Vite production build                     │   │
│  │  - Port 5173                                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Voice Bot Service (Auto-scaling 2-5 tasks)          │   │
│  │  - WebRTC + AWS Transcribe + Bedrock + ElevenLabs   │   │
│  │  - Port 7860                                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Browser Agent Service (Auto-scaling 1-3 tasks)      │   │
│  │  - Playwright + GPT-4 + browser-use                  │   │
│  │  - Port 7863                                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS Services                              │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  DynamoDB    │  │   Cognito    │  │  Transcribe  │      │
│  │  (Sessions)  │  │    (Auth)    │  │    (STT)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Bedrock    │  │  CloudWatch  │  │     WAF      │      │
│  │  (Claude)    │  │   (Logs)     │  │  (Security)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### 1. AWS Account Setup
- AWS Account with admin access
- AWS CLI installed and configured
- Region: `us-east-1` (for Bedrock Claude Sonnet 4)

### 2. Required Tools
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 3. AWS Services Configuration

#### Enable Bedrock Model Access
```bash
# Navigate to AWS Bedrock Console
# Region: us-east-1
# Enable: Anthropic Claude Sonnet 4
```

#### Create DynamoDB Table
```bash
aws dynamodb create-table \
    --table-name vpbank-sessions \
    --attribute-definitions AttributeName=session_id,AttributeType=S \
    --key-schema AttributeName=session_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

#### Create Cognito User Pool
```bash
# Via AWS Console or CLI
aws cognito-idp create-user-pool \
    --pool-name vpbank-voice-users \
    --auto-verified-attributes email \
    --region us-east-1
```

---

## Deployment Steps

### Step 1: Configure Environment Variables

Create `.env.production` in project root:

```bash
# AWS Credentials (Main - for Transcribe/Bedrock)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# AWS Bedrock
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# OpenAI (for Browser Agent)
OPENAI_API_KEY=sk-...

# ElevenLabs (Vietnamese TTS)
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...

# AWS Cognito
COGNITO_USER_POOL_ID=us-east-1_...
COGNITO_CLIENT_ID=...

# DynamoDB
DYNAMODB_TABLE_NAME=vpbank-sessions
DYNAMODB_ACCESS_KEY_ID=AKIA...
DYNAMODB_SECRET_ACCESS_KEY=...
DYNAMODB_REGION=us-east-1

# Browser Service URL (internal)
BROWSER_SERVICE_URL=http://browser-agent:7863
```

### Step 2: Deploy Infrastructure with Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review deployment plan
terraform plan -out=tfplan

# Deploy infrastructure
terraform apply tfplan
```

**What gets created:**
- VPC with public/private subnets
- Network Load Balancer (NLB)
- ECS Fargate Cluster
- ECR Repositories (3)
- Security Groups
- IAM Roles
- CloudWatch Log Groups
- Auto-scaling policies
- WAF rules

### Step 3: Build and Push Docker Images

```bash
# Run deployment script
./scripts/deploy-ecs-fargate.sh
```

**Script does:**
1. Builds 3 Docker images (Frontend, Voice Bot, Browser Agent)
2. Tags images with version
3. Pushes to AWS ECR
4. Updates ECS task definitions
5. Deploys to ECS cluster
6. Waits for services to stabilize

### Step 4: Configure DNS

```bash
# Get NLB DNS name
terraform output nlb_dns_name

# Create Route 53 record
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
      "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "vpbank-voice.yourdomain.com",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "Z215JYRZR1TBD5",
            "DNSName": "vpbank-nlb-xxx.elb.us-east-1.amazonaws.com",
            "EvaluateTargetHealth": false
          }
        }
      }]
    }'
```

### Step 5: Configure SSL/TLS

```bash
# Request ACM certificate
aws acm request-certificate \
    --domain-name vpbank-voice.yourdomain.com \
    --validation-method DNS \
    --region us-east-1

# Add NLB TLS listener
terraform apply -var="enable_https=true"
```

### Step 6: Verify Deployment

```bash
# Check ECS services
aws ecs list-services --cluster vpbank-voice-cluster

# Check task health
aws ecs describe-services \
    --cluster vpbank-voice-cluster \
    --services voice-bot-service

# Test endpoints
curl https://vpbank-voice.yourdomain.com/api/health
```

---

## Monitoring & Operations

### CloudWatch Dashboards

```bash
# View logs
aws logs tail /ecs/voice-bot --follow
aws logs tail /ecs/browser-agent --follow
aws logs tail /ecs/frontend --follow
```

### Auto-Scaling Configuration

**Voice Bot Service:**
- Min: 2 tasks
- Max: 5 tasks
- Scale up: CPU > 70% or Memory > 80%
- Scale down: CPU < 30% for 5 minutes

**Browser Agent Service:**
- Min: 1 task
- Max: 3 tasks
- Scale up: CPU > 60%

**Frontend Service:**
- Min: 1 task
- Max: 3 tasks
- Scale up: Request count > 1000/min

### Cost Monitoring

```bash
# Setup billing alerts
./scripts/setup_cloudwatch_alarms.sh
```

**Estimated Monthly Costs:**
- ECS Fargate: $150-300 (depends on usage)
- NLB: $20-30
- DynamoDB: $5-20
- CloudWatch: $10-20
- Data Transfer: $20-50
- **Total: $205-420/month**

---

## Security Hardening

### Apply Security Best Practices

```bash
# Deploy security hardening
./scripts/deploy_security_hardening.sh
```

**Includes:**
- WAF rules (rate limiting, SQL injection protection)
- Secrets Manager for credentials
- VPC security groups
- IAM least privilege policies
- Encryption at rest and in transit

### Migrate to Secrets Manager

```bash
# Move credentials from .env to Secrets Manager
./scripts/migrate_to_secrets_manager.sh
```

---

## Scaling & Performance

### Horizontal Scaling

ECS auto-scales based on:
- CPU utilization
- Memory utilization
- Request count
- Custom CloudWatch metrics

### Vertical Scaling

Update task definitions:
```bash
# Edit infrastructure/terraform/ecs-tasks.tf
# Increase CPU/Memory:
cpu    = "2048"  # 2 vCPU
memory = "4096"  # 4 GB

terraform apply
```

---

## Troubleshooting

### Common Issues

**1. WebRTC Connection Fails**
```bash
# Check NLB security group allows UDP
aws ec2 describe-security-groups --group-ids sg-xxx

# Verify STUN/TURN servers configured
aws ecs describe-task-definition --task-definition voice-bot
```

**2. Tasks Keep Restarting**
```bash
# Check logs
aws logs tail /ecs/voice-bot --follow

# Check task health
aws ecs describe-tasks --cluster vpbank-voice-cluster --tasks <task-id>
```

**3. High Costs**
```bash
# Review CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name CPUUtilization \
    --dimensions Name=ServiceName,Value=voice-bot-service

# Reduce task count if underutilized
```

---

## Rollback Procedure

```bash
# Rollback to previous version
aws ecs update-service \
    --cluster vpbank-voice-cluster \
    --service voice-bot-service \
    --task-definition voice-bot:PREVIOUS_VERSION \
    --force-new-deployment
```

---

## Cleanup

```bash
# Destroy all infrastructure
cd infrastructure/terraform
terraform destroy

# Delete ECR images
aws ecr batch-delete-image \
    --repository-name vpbank-voice-bot \
    --image-ids imageTag=latest
```

---

## Support & Maintenance

### Health Checks
- NLB health checks every 30 seconds
- Unhealthy threshold: 2 consecutive failures
- Healthy threshold: 2 consecutive successes

### Backup Strategy
- DynamoDB: Point-in-time recovery enabled
- ECS task definitions: Versioned automatically
- Infrastructure: Terraform state in S3

### Update Strategy
1. Build new Docker images
2. Push to ECR with new tag
3. Update task definition
4. Deploy with rolling update (zero downtime)

---

## Production Checklist

- [ ] AWS account configured
- [ ] All environment variables set
- [ ] Bedrock model access enabled
- [ ] DynamoDB table created
- [ ] Cognito user pool configured
- [ ] Domain name registered
- [ ] SSL certificate issued
- [ ] Terraform infrastructure deployed
- [ ] Docker images built and pushed
- [ ] ECS services running
- [ ] DNS configured
- [ ] Health checks passing
- [ ] Monitoring dashboards created
- [ ] Billing alerts configured
- [ ] Security hardening applied
- [ ] Load testing completed
- [ ] Backup strategy verified

---

**For questions or issues, refer to:**
- Main README: `/README.md`
- Terraform docs: `/infrastructure/terraform/`
- Scripts: `/scripts/`
