#!/bin/bash
set -e

echo "🚀 VPBank Voice Agent - AWS Production Deployment"
echo "=================================================="
echo ""

# Check prerequisites
echo "▶ Checking prerequisites..."
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI required"; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }

# Check AWS credentials
aws sts get-caller-identity > /dev/null 2>&1 || { echo "❌ AWS credentials not configured"; exit 1; }

echo "✅ Prerequisites OK"
echo ""

# Step 1: Deploy infrastructure
echo "▶ Step 1/3: Deploying AWS infrastructure..."
cd infrastructure/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
cd ../..
echo "✅ Infrastructure deployed"
echo ""

# Step 2: Build and push Docker images
echo "▶ Step 2/3: Building and pushing Docker images..."
./scripts/deploy-ecs-fargate.sh
echo "✅ Docker images deployed"
echo ""

# Step 3: Verify deployment
echo "▶ Step 3/3: Verifying deployment..."
sleep 10

# Get NLB DNS
NLB_DNS=$(terraform -chdir=infrastructure/terraform output -raw nlb_dns_name 2>/dev/null || echo "")

if [ -n "$NLB_DNS" ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "Access your application at:"
    echo "  http://$NLB_DNS"
    echo ""
    echo "Next steps:"
    echo "  1. Configure DNS: Point your domain to $NLB_DNS"
    echo "  2. Setup SSL: Run ./scripts/deploy-https.sh"
    echo "  3. Monitor: Check CloudWatch logs"
else
    echo "⚠️  Could not retrieve NLB DNS. Check Terraform outputs."
fi

echo ""
echo "📊 View logs:"
echo "  aws logs tail /ecs/voice-bot --follow"
echo "  aws logs tail /ecs/browser-agent --follow"
echo ""
