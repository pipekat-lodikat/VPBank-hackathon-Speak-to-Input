#!/bin/bash
set -e

REGION="us-east-1"
ACCOUNT_ID="590183822512"
CLUSTER="vpbank-voice-agent-cluster"
REPO="vpbank-voice-agent-frontend"

echo "🚀 Deploying Frontend to AWS ECS"
echo "================================="

cd /home/ubuntu/speak-to-input

# Build frontend
echo "▶ Building frontend..."
cd frontend
npm run build
cd ..

# Login to ECR
echo "▶ Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build Docker image
echo "▶ Building Docker image..."
cat > Dockerfile.frontend << 'EOF'
FROM nginx:alpine
COPY frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

# Create nginx config
cat > frontend/nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Enable CORS
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
}
EOF

docker build -t $REPO:latest -f Dockerfile.frontend .

# Tag and push
echo "▶ Pushing to ECR..."
docker tag $REPO:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:latest

# Check if service exists
SERVICE_EXISTS=$(aws ecs describe-services --cluster $CLUSTER --services frontend --region $REGION 2>&1 | grep -c "ACTIVE" || echo "0")

if [ "$SERVICE_EXISTS" -eq "0" ]; then
    echo "▶ Creating new ECS service..."
    # Service doesn't exist, need to create it via Terraform or manually
    echo "⚠️  Frontend service not found. Create it first with Terraform."
    exit 1
else
    echo "▶ Updating existing service..."
    aws ecs update-service \
        --cluster $CLUSTER \
        --service frontend \
        --force-new-deployment \
        --region $REGION
fi

echo ""
echo "✅ Frontend deployment initiated!"
echo ""
echo "Monitor: aws ecs describe-services --cluster $CLUSTER --services frontend --region $REGION"
