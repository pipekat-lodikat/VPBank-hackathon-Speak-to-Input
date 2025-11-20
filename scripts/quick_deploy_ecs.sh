#!/bin/bash
set -e

echo "⚡ Quick ECS Deploy (US-East-1)"

cd infrastructure/terraform

# Check if already deployed
if [ -f terraform.tfstate ]; then
    echo "📊 Updating existing deployment..."
    terraform apply -auto-approve
else
    echo "🆕 First-time deployment..."
    terraform init
    terraform apply -auto-approve
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Access URLs:"
terraform output -json | jq -r '
  "Frontend: https://" + .cloudfront_domain.value,
  "Voice Bot: http://" + .alb_dns_name.value,
  "Browser Agent: http://" + .alb_dns_name.value + ":7863"
'
