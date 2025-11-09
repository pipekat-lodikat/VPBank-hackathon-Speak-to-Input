#!/bin/bash

echo "🔍 FULL PRODUCTION DEBUG - VPBank Voice Agent"
echo "=============================================="
echo ""

# 1. LOCAL SERVICES
echo "1️⃣ LOCAL SERVICES (EC2)"
echo "------------------------"
ps aux | grep -E "main_browser_service|main_voice" | grep -v grep || echo "❌ No local services running"

echo ""
echo "Local Health Checks:"
echo -n "  Browser Agent (7863): "
curl -s http://localhost:7863/api/health > /dev/null 2>&1 && echo "✅ UP" || echo "❌ DOWN"
echo -n "  Voice Bot (7860): "
curl -s http://localhost:7860 > /dev/null 2>&1 && echo "✅ UP" || echo "❌ DOWN"

# 2. ECS SERVICES
echo ""
echo "2️⃣ ECS SERVICES (Fargate)"
echo "-------------------------"
aws ecs describe-services --cluster vpbank-voice-agent-cluster --services browser-agent voice-bot --region us-east-1 --query 'services[].{Service:serviceName,Status:status,Running:runningCount,Desired:desiredCount}' --output table 2>&1 | grep -v "^$"

# 3. ALB
echo ""
echo "3️⃣ APPLICATION LOAD BALANCER"
echo "-----------------------------"
ALB_DNS="vpbank-voice-agent-alb-1745174960.us-east-1.elb.amazonaws.com"
echo "DNS: $ALB_DNS"
echo -n "Health: "
curl -s http://$ALB_DNS/api/health > /dev/null 2>&1 && echo "✅ HEALTHY" || echo "❌ UNHEALTHY"

# 4. CLOUDFRONT
echo ""
echo "4️⃣ CLOUDFRONT CDN"
echo "-----------------"
CF_DOMAIN="d359aaha3l67dn.cloudfront.net"
echo "Domain: https://$CF_DOMAIN"
echo -n "Status: "
curl -s -o /dev/null -w "%{http_code}" https://$CF_DOMAIN 2>&1 | grep -q "200" && echo "✅ 200 OK" || echo "❌ ERROR"

# 5. RECENT ERRORS
echo ""
echo "5️⃣ RECENT ERRORS (Last 10 min)"
echo "-------------------------------"
echo "Local Browser Agent:"
tail -20 /home/ubuntu/speak-to-input/logs/browser_agent.log 2>/dev/null | grep -i "error\|exception\|failed" | tail -3 || echo "  No errors"

echo ""
echo "Local Voice Bot:"
tail -20 /home/ubuntu/speak-to-input/logs/voice_bot.log 2>/dev/null | grep -i "error\|exception\|failed" | tail -3 || echo "  No errors"

echo ""
echo "ECS Browser Agent:"
aws logs tail /ecs/vpbank-voice-agent/browser-agent --since 10m --region us-east-1 2>&1 | grep -i "error\|exception\|failed" | tail -3 || echo "  No errors"

echo ""
echo "ECS Voice Bot:"
aws logs tail /ecs/vpbank-voice-agent/voice-bot --since 10m --region us-east-1 2>&1 | grep -i "error\|exception\|failed\|traceback" | tail -5 || echo "  No errors"

# 6. NETWORK
echo ""
echo "6️⃣ NETWORK CONNECTIVITY"
echo "-----------------------"
echo -n "AWS API: "
aws sts get-caller-identity --region us-east-1 > /dev/null 2>&1 && echo "✅ Connected" || echo "❌ Failed"
echo -n "Internet: "
curl -s -o /dev/null -w "%{http_code}" https://www.google.com 2>&1 | grep -q "200" && echo "✅ Connected" || echo "❌ Failed"

# 7. RESOURCES
echo ""
echo "7️⃣ SYSTEM RESOURCES"
echo "-------------------"
echo "CPU & Memory:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "  CPU Usage: " 100 - $1"%"}'
free -h | awk 'NR==2{printf "  Memory: %s/%s (%.2f%%)\n", $3,$2,$3*100/$2 }'
df -h / | awk 'NR==2{printf "  Disk: %s/%s (%s)\n", $3,$2,$5}'

# 8. SUMMARY
echo ""
echo "8️⃣ SUMMARY"
echo "----------"
LOCAL_BROWSER=$(curl -s http://localhost:7863/api/health > /dev/null 2>&1 && echo "✅" || echo "❌")
LOCAL_VOICE=$(curl -s http://localhost:7860 > /dev/null 2>&1 && echo "✅" || echo "❌")
ECS_STATUS=$(aws ecs describe-services --cluster vpbank-voice-agent-cluster --services browser-agent --region us-east-1 --query 'services[0].runningCount' --output text 2>&1)
ALB_STATUS=$(curl -s http://$ALB_DNS/api/health > /dev/null 2>&1 && echo "✅" || echo "❌")
CF_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$CF_DOMAIN 2>&1 | grep -q "200" && echo "✅" || echo "❌")

echo "  Local Browser Agent:  $LOCAL_BROWSER"
echo "  Local Voice Bot:      $LOCAL_VOICE"
echo "  ECS Services:         $([ "$ECS_STATUS" = "2" ] && echo "✅ 2/2" || echo "❌ $ECS_STATUS")"
echo "  ALB:                  $ALB_STATUS"
echo "  CloudFront:           $CF_STATUS"

echo ""
echo "✅ Debug complete!"
