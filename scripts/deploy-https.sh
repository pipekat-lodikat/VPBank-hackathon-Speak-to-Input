#!/bin/bash
#
# Quick HTTPS Deployment Script for VPBank Voice Agent
# For BTC Demo with Self-Signed Certificate
#

set -e

echo "=========================================="
echo "VPBank Voice Agent - HTTPS Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "main.tf" ]; then
    echo -e "${RED}Error: main.tf not found. Please run this script from terraform-ecs/ directory${NC}"
    exit 1
fi

# Prompt for deployment mode
echo -e "${BLUE}Select deployment mode:${NC}"
echo "1. Self-signed certificate (Quick - for BTC demo)"
echo "2. Custom domain with ACM (Production)"
echo "3. Disable HTTPS (Rollback)"
echo ""
read -p "Enter choice [1-3]: " mode

case $mode in
    1)
        echo ""
        echo -e "${GREEN}Deploying with self-signed certificate...${NC}"
        echo ""

        # Ask about HTTP redirect
        read -p "Redirect HTTP to HTTPS? [y/N]: " redirect
        if [[ $redirect =~ ^[Yy]$ ]]; then
            terraform apply \
                -var="enable_https=true" \
                -var="domain_name=" \
                -var="redirect_http_to_https=true"
        else
            terraform apply \
                -var="enable_https=true" \
                -var="domain_name=" \
                -var="redirect_http_to_https=false"
        fi

        # Get ALB URL
        echo ""
        echo -e "${GREEN}Deployment complete!${NC}"
        echo ""
        ALB_URL=$(terraform output -raw alb_https_url 2>/dev/null || echo "Not available")
        echo -e "${YELLOW}HTTPS ALB URL:${NC} $ALB_URL"
        echo ""
        echo -e "${YELLOW}⚠️  Important for BTC Demo:${NC}"
        echo "1. Update frontend/src/config.ts to use: $ALB_URL"
        echo "2. Rebuild frontend: cd ../frontend && npm run build"
        echo "3. Deploy frontend to S3"
        echo "4. Invalidate CloudFront cache"
        echo "5. Open ALB URL in browser and accept self-signed certificate"
        echo ""
        echo -e "${BLUE}See HTTPS_DEPLOYMENT_GUIDE.md for detailed instructions${NC}"
        ;;

    2)
        echo ""
        read -p "Enter domain name (e.g., vpbank-agent.example.com): " domain

        if [ -z "$domain" ]; then
            echo -e "${RED}Error: Domain name is required${NC}"
            exit 1
        fi

        echo ""
        echo -e "${GREEN}Deploying with custom domain: $domain${NC}"
        echo ""

        terraform apply \
            -var="enable_https=true" \
            -var="domain_name=$domain" \
            -var="redirect_http_to_https=true"

        echo ""
        echo -e "${GREEN}Deployment complete!${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  DNS Configuration Required:${NC}"
        echo ""
        echo "Create the following DNS records:"
        echo ""
        terraform output acm_validation_records
        echo ""
        ALB_URL=$(terraform output -raw alb_https_url 2>/dev/null || echo "Not available")
        echo "HTTPS URL: $ALB_URL"
        echo ""
        echo -e "${BLUE}See HTTPS_DEPLOYMENT_GUIDE.md for detailed instructions${NC}"
        ;;

    3)
        echo ""
        echo -e "${YELLOW}Disabling HTTPS...${NC}"
        echo ""

        terraform apply -var="enable_https=false"

        echo ""
        echo -e "${GREEN}HTTPS disabled${NC}"
        echo ""
        echo "ALB will use HTTP only (port 80)"
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Done!${NC}"
