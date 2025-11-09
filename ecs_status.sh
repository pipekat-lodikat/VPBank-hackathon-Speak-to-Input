#!/bin/bash

echo "🔍 ECS + CloudFront Production Status"
echo "======================================"
echo ""

# ECS Cluster
echo "📦 ECS Cluster: vpbank-voice-agent-cluster"
aws ecs describe-services --cluster vpbank-voice-agent-cluster --services browser-agent voice-bot --region us-east-1 --query 'services[].{Service:serviceName,Status:status,Running:runningCount,Desired:desiredCount}' --output table

echo ""
echo "🌐 CloudFront Distribution"
echo "Domain: d359aaha3l67dn.cloudfront.net"
echo "Status: Deployed ✅"
echo "Origin: vpbank-voice-agent-alb-1745174960.us-east-1.elb.amazonaws.com"

echo ""
echo "🔗 Access URLs:"
echo "  CloudFront: https://d359aaha3l67dn.cloudfront.net"
echo "  ALB Direct: http://vpbank-voice-agent-alb-1745174960.us-east-1.elb.amazonaws.com"

echo ""
echo "🏥 Health Check:"
curl -s http://vpbank-voice-agent-alb-1745174960.us-east-1.elb.amazonaws.com/api/health | jq .

echo ""
echo "📊 Recent Logs (last 5 lines):"
echo "--- Browser Agent ---"
aws logs tail /ecs/vpbank-voice-agent/browser-agent --since 5m --region us-east-1 2>&1 | tail -5

echo ""
echo "--- Voice Bot ---"
aws logs tail /ecs/vpbank-voice-agent/voice-bot --since 5m --region us-east-1 2>&1 | tail -5
