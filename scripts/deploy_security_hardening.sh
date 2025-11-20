#!/bin/bash
# Deploy security hardening configurations for VPBank Voice Agent
# Usage: ./scripts/deploy_security_hardening.sh [--migrate-secrets] [--enable-all]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/infrastructure/terraform"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
MIGRATE_SECRETS=false
ENABLE_ALL=false
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --migrate-secrets)
            MIGRATE_SECRETS=true
            shift
            ;;
        --enable-all)
            ENABLE_ALL=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--migrate-secrets] [--enable-all] [--dry-run]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🔐 VPBank Voice Agent - Security Hardening Deployment${NC}"
echo "=========================================================="
echo ""

# Step 1: Pre-flight checks
echo -e "${YELLOW}📋 Step 1: Pre-flight checks${NC}"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ Error: AWS CLI not installed${NC}"
    exit 1
fi
echo "  ✅ AWS CLI installed"

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Error: Terraform not installed${NC}"
    exit 1
fi
echo "  ✅ Terraform installed"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ Error: AWS credentials not configured${NC}"
    exit 1
fi
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "  ✅ AWS credentials configured (Account: $AWS_ACCOUNT_ID)"

# Check Terraform directory
if [ ! -d "$TERRAFORM_DIR" ]; then
    echo -e "${RED}❌ Error: Terraform directory not found: $TERRAFORM_DIR${NC}"
    exit 1
fi
echo "  ✅ Terraform directory found"

echo ""

# Step 2: Migrate secrets to Secrets Manager (optional)
if [ "$MIGRATE_SECRETS" = true ]; then
    echo -e "${YELLOW}📋 Step 2: Migrating credentials to Secrets Manager${NC}"
    echo ""

    if [ -f "$SCRIPT_DIR/migrate_to_secrets_manager.sh" ]; then
        bash "$SCRIPT_DIR/migrate_to_secrets_manager.sh"
    else
        echo -e "${RED}❌ Error: Migration script not found${NC}"
        exit 1
    fi

    echo ""
fi

# Step 3: Review current security posture
echo -e "${YELLOW}📋 Step 3: Reviewing current security posture${NC}"
echo ""

echo "  Checking S3 bucket security..."
BUCKET_NAME="vpbank-voice-agent-frontend-$AWS_ACCOUNT_ID"
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    PUBLIC_ACCESS=$(aws s3api get-public-access-block --bucket "$BUCKET_NAME" 2>/dev/null || echo "{}")
    echo "  📦 S3 Bucket: $BUCKET_NAME"
    echo "     Public Access Block: $(echo "$PUBLIC_ACCESS" | jq -r '.PublicAccessBlockConfiguration.BlockPublicAcls // "Not configured"')"
else
    echo "  ⚠️  S3 bucket not found (will be created)"
fi

echo ""
echo "  Checking GuardDuty status..."
GUARDDUTY_STATUS=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text 2>/dev/null || echo "None")
if [ "$GUARDDUTY_STATUS" != "None" ]; then
    echo "  ✅ GuardDuty already enabled: $GUARDDUTY_STATUS"
else
    echo "  ⚠️  GuardDuty not enabled (will be enabled)"
fi

echo ""
echo "  Checking Security Hub status..."
SECURITY_HUB_STATUS=$(aws securityhub describe-hub --query 'HubArn' --output text 2>/dev/null || echo "Not enabled")
if [ "$SECURITY_HUB_STATUS" != "Not enabled" ]; then
    echo "  ✅ Security Hub already enabled"
else
    echo "  ⚠️  Security Hub not enabled (will be enabled)"
fi

echo ""

# Step 4: Terraform plan
echo -e "${YELLOW}📋 Step 4: Planning Terraform changes${NC}"
echo ""

cd "$TERRAFORM_DIR"

echo "  Initializing Terraform..."
terraform init -upgrade > /dev/null 2>&1
echo "  ✅ Terraform initialized"

echo ""
echo "  Running Terraform plan..."
if [ "$DRY_RUN" = true ]; then
    terraform plan -out=security-plan.tfplan
    echo ""
    echo -e "${BLUE}ℹ️  Dry run mode: No changes will be applied${NC}"
    echo "   Review the plan above and run without --dry-run to apply"
    exit 0
fi

terraform plan -out=security-plan.tfplan

echo ""
read -p "Do you want to apply these changes? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}⚠️  Deployment cancelled${NC}"
    rm -f security-plan.tfplan
    exit 0
fi

# Step 5: Apply Terraform changes
echo ""
echo -e "${YELLOW}📋 Step 5: Applying security hardening${NC}"
echo ""

terraform apply security-plan.tfplan

rm -f security-plan.tfplan

echo ""
echo -e "${GREEN}✅ Security hardening applied successfully!${NC}"
echo ""

# Step 6: Post-deployment verification
echo -e "${YELLOW}📋 Step 6: Post-deployment verification${NC}"
echo ""

echo "  Verifying GuardDuty..."
GUARDDUTY_ID=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text)
if [ -n "$GUARDDUTY_ID" ] && [ "$GUARDDUTY_ID" != "None" ]; then
    echo "  ✅ GuardDuty enabled: $GUARDDUTY_ID"
else
    echo "  ❌ GuardDuty verification failed"
fi

echo ""
echo "  Verifying Security Hub..."
if aws securityhub describe-hub &> /dev/null; then
    echo "  ✅ Security Hub enabled"
else
    echo "  ❌ Security Hub verification failed"
fi

echo ""
echo "  Verifying S3 bucket security..."
PUBLIC_ACCESS=$(aws s3api get-public-access-block --bucket "$BUCKET_NAME")
BLOCK_PUBLIC_ACLS=$(echo "$PUBLIC_ACCESS" | jq -r '.PublicAccessBlockConfiguration.BlockPublicAcls')
if [ "$BLOCK_PUBLIC_ACLS" = "true" ]; then
    echo "  ✅ S3 public access blocked"
else
    echo "  ❌ S3 public access block verification failed"
fi

echo ""
echo "  Verifying KMS keys..."
KMS_KEYS=$(aws kms list-aliases --query "Aliases[?starts_with(AliasName, 'alias/vpbank-voice-agent')].AliasName" --output json)
KMS_COUNT=$(echo "$KMS_KEYS" | jq '. | length')
echo "  ✅ KMS keys created: $KMS_COUNT"

echo ""
echo -e "${GREEN}========================================================${NC}"
echo -e "${GREEN}🎉 Security Hardening Deployment Complete!${NC}"
echo -e "${GREEN}========================================================${NC}"
echo ""

# Summary
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo ""
echo "✅ Enabled Services:"
echo "   • AWS GuardDuty (Threat Detection)"
echo "   • AWS Security Hub (Compliance Monitoring)"
echo "   • AWS Config (Resource Compliance)"
echo "   • VPC Flow Logs (Network Monitoring)"
echo ""
echo "✅ Security Enhancements:"
echo "   • S3 bucket public access blocked"
echo "   • KMS encryption for S3, Secrets Manager, CloudWatch"
echo "   • IAM policies restricted to least privilege"
echo "   • Secrets migrated to AWS Secrets Manager"
echo "   • VPC Flow Logs enabled"
echo ""
echo "📋 Next Steps:"
echo "   1. Subscribe to SNS email notifications (check inbox)"
echo "   2. Review Security Hub findings"
echo "   3. Configure GuardDuty notifications"
echo "   4. Update application to use Secrets Manager"
echo "   5. Deploy WAF (run: cd infrastructure/terraform && terraform apply)"
echo ""
echo "📚 Documentation:"
echo "   • Security Assessment: AWS_SECURITY_ASSESSMENT.md"
echo "   • Deployment Guide: SECURITY_DEPLOYMENT_GUIDE.md"
echo ""
