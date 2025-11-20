#!/bin/bash
set -e

REGION="us-east-1"
BUCKET_NAME="vpbank-voice-agent-frontend-$(date +%s)"

echo "🚀 Deploying Frontend to S3 + CloudFront"
echo "========================================="

cd /home/ubuntu/speak-to-input/frontend

# Build frontend
echo "▶ Building frontend..."
npm run build

# Create S3 bucket
echo "▶ Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Configure bucket for static website
echo "▶ Configuring bucket..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

# Set bucket policy for public read
cat > /tmp/bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
  }]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file:///tmp/bucket-policy.json

# Upload files
echo "▶ Uploading files to S3..."
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete

# Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

echo ""
echo "✅ Frontend deployed!"
echo ""
echo "Access URL: $WEBSITE_URL"
echo ""
echo "Bucket: $BUCKET_NAME"
