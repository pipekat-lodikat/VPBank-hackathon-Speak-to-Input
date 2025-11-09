#!/bin/bash
# Quick setup script for CloudWatch alarms (without Terraform)
# For manual deployment of critical monitoring

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ALARM_EMAIL="${1:-admin@vpbank.com}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo -e "${BLUE}=== CloudWatch Alarms Setup ===${NC}"
echo "Email: $ALARM_EMAIL"
echo "Region: $AWS_REGION"
echo ""

# Create SNS Topic
echo -e "${YELLOW}Creating SNS topic for alarms...${NC}"
SNS_TOPIC_ARN=$(aws sns create-topic \
    --name vpbank-voice-agent-alarms \
    --region "$AWS_REGION" \
    --query 'TopicArn' \
    --output text)

echo -e "${GREEN}✓ SNS Topic created: $SNS_TOPIC_ARN${NC}"

# Subscribe email to SNS topic
echo -e "${YELLOW}Subscribing $ALARM_EMAIL to SNS topic...${NC}"
aws sns subscribe \
    --topic-arn "$SNS_TOPIC_ARN" \
    --protocol email \
    --notification-endpoint "$ALARM_EMAIL" \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ Email subscription created (check your inbox to confirm)${NC}"
echo ""

# Create Metric Filters
echo -e "${YELLOW}Creating metric filters...${NC}"

# 1. WebRTC Connection Timeout
aws logs put-metric-filter \
    --log-group-name "/ecs/vpbank-voice-agent/voice-bot" \
    --filter-name "webrtc-connection-timeout" \
    --filter-pattern "[time, level, location, msg=\"Timeout establishing the connection*\"]" \
    --metric-transformations \
        metricName=WebRTCConnectionTimeout,metricNamespace=VPBankVoiceAgent,metricValue=1,unit=Count \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ WebRTC timeout metric filter created${NC}"

# 2. ElevenLabs TTS Errors
aws logs put-metric-filter \
    --log-group-name "/ecs/vpbank-voice-agent/voice-bot" \
    --filter-name "elevenlabs-tts-error" \
    --filter-pattern "[time, level=ERROR, location, msg=\"*ElevenLabsTTSService*\"]" \
    --metric-transformations \
        metricName=ElevenLabsTTSError,metricNamespace=VPBankVoiceAgent,metricValue=1,unit=Count \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ ElevenLabs error metric filter created${NC}"

# 3. AWS Transcribe Errors
aws logs put-metric-filter \
    --log-group-name "/ecs/vpbank-voice-agent/voice-bot" \
    --filter-name "transcribe-connection-error" \
    --filter-pattern "[time, level=ERROR, location, msg=\"*AWSTranscribeSTTService*\"]" \
    --metric-transformations \
        metricName=TranscribeConnectionError,metricNamespace=VPBankVoiceAgent,metricValue=1,unit=Count \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ Transcribe error metric filter created${NC}"

# 4. Session Created (Success metric)
aws logs put-metric-filter \
    --log-group-name "/ecs/vpbank-voice-agent/voice-bot" \
    --filter-name "session-created-success" \
    --filter-pattern "[time, level=INFO, location, msg=\"*Starting voice bot*\"]" \
    --metric-transformations \
        metricName=SessionCreated,metricNamespace=VPBankVoiceAgent,metricValue=1,unit=Count \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ Session created metric filter created${NC}"

# 5. Session Completed (Success metric)
aws logs put-metric-filter \
    --log-group-name "/ecs/vpbank-voice-agent/voice-bot" \
    --filter-name "session-completed-success" \
    --filter-pattern "[time, level=INFO, location, msg=\"*Session completed*\"]" \
    --metric-transformations \
        metricName=SessionCompleted,metricNamespace=VPBankVoiceAgent,metricValue=1,unit=Count \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ Session completed metric filter created${NC}"

# 6. Critical Errors
aws logs put-metric-filter \
    --log-group-name "/ecs/vpbank-voice-agent/voice-bot" \
    --filter-name "critical-application-error" \
    --filter-pattern "[time, level=ERROR|CRITICAL, ...]" \
    --metric-transformations \
        metricName=CriticalError,metricNamespace=VPBankVoiceAgent,metricValue=1,unit=Count \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ Critical error metric filter created${NC}"
echo ""

# Create Alarms
echo -e "${YELLOW}Creating CloudWatch alarms...${NC}"

# Alarm 1: High WebRTC Timeout Rate
aws cloudwatch put-metric-alarm \
    --alarm-name "vpbank-voice-agent-webrtc-timeout-high" \
    --alarm-description "High rate of WebRTC connection timeouts detected" \
    --metric-name WebRTCConnectionTimeout \
    --namespace VPBankVoiceAgent \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions "$SNS_TOPIC_ARN" \
    --treat-missing-data notBreaching \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ WebRTC timeout alarm created${NC}"

# Alarm 2: High ElevenLabs Error Rate
aws cloudwatch put-metric-alarm \
    --alarm-name "vpbank-voice-agent-elevenlabs-error-high" \
    --alarm-description "High rate of ElevenLabs TTS errors" \
    --metric-name ElevenLabsTTSError \
    --namespace VPBankVoiceAgent \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions "$SNS_TOPIC_ARN" \
    --treat-missing-data notBreaching \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ ElevenLabs error alarm created${NC}"

# Alarm 3: High Transcribe Error Rate
aws cloudwatch put-metric-alarm \
    --alarm-name "vpbank-voice-agent-transcribe-error-high" \
    --alarm-description "High rate of AWS Transcribe connection errors" \
    --metric-name TranscribeConnectionError \
    --namespace VPBankVoiceAgent \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions "$SNS_TOPIC_ARN" \
    --treat-missing-data notBreaching \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ Transcribe error alarm created${NC}"

# Alarm 4: Critical Error Rate
aws cloudwatch put-metric-alarm \
    --alarm-name "vpbank-voice-agent-critical-error-high" \
    --alarm-description "High rate of critical application errors" \
    --metric-name CriticalError \
    --namespace VPBankVoiceAgent \
    --statistic Sum \
    --period 60 \
    --evaluation-periods 1 \
    --threshold 20 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions "$SNS_TOPIC_ARN" \
    --treat-missing-data notBreaching \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ Critical error alarm created${NC}"

# Alarm 5: Voice Bot Unhealthy Targets
aws cloudwatch put-metric-alarm \
    --alarm-name "vpbank-voice-agent-voice-bot-unhealthy-hosts" \
    --alarm-description "Voice Bot targets are unhealthy" \
    --metric-name UnHealthyHostCount \
    --namespace AWS/ApplicationELB \
    --statistic Average \
    --period 60 \
    --evaluation-periods 2 \
    --threshold 0 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=TargetGroup,Value=targetgroup/vpbank-va-voice-tg/ae94fb33d60195af Name=LoadBalancer,Value=app/vpbank-voice-agent-alb/21a2eda047609e0d \
    --alarm-actions "$SNS_TOPIC_ARN" \
    --treat-missing-data notBreaching \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ Voice Bot unhealthy hosts alarm created${NC}"

# Alarm 6: CloudFront 5XX Errors
aws cloudwatch put-metric-alarm \
    --alarm-name "vpbank-voice-agent-cloudfront-5xx-errors-high" \
    --alarm-description "High rate of 5XX errors from CloudFront" \
    --metric-name 5xxErrorRate \
    --namespace AWS/CloudFront \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=DistributionId,Value=E157XTMGCFVXEO \
    --alarm-actions "$SNS_TOPIC_ARN" \
    --treat-missing-data notBreaching \
    --region us-east-1

echo -e "${GREEN}✓ CloudFront 5XX error alarm created${NC}"

echo ""
echo -e "${BLUE}=== Setup Complete ===${NC}"
echo -e "${GREEN}✓ SNS Topic: $SNS_TOPIC_ARN${NC}"
echo -e "${GREEN}✓ 6 Metric Filters created${NC}"
echo -e "${GREEN}✓ 6 CloudWatch Alarms created${NC}"
echo ""
echo -e "${YELLOW}⚠️  Important: Check your email ($ALARM_EMAIL) and confirm the SNS subscription!${NC}"
echo ""
echo -e "${BLUE}View alarms at:${NC}"
echo "https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#alarmsV2:"
echo ""
echo -e "${BLUE}View metrics at:${NC}"
echo "https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#metricsV2:graph=~();namespace=VPBankVoiceAgent"
