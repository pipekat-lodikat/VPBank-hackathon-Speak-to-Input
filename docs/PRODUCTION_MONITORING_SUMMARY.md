# Production Logs & Debugging Summary
**Date:** November 9, 2025
**Status:** Complete - All 4 Tasks Delivered

---

## Executive Summary

Comprehensive production analysis completed with filtered logs, security investigation, WebRTC optimization recommendations, and CloudWatch monitoring setup. System is **operational** with identified improvements for connection reliability and security.

### Overall Production Health: ✅ OPERATIONAL

**Services Running:**
- Voice Bot: 2/2 tasks (HEALTHY)
- Browser Agent: 2/2 tasks (HEALTHY)
- Frontend: CloudFront deployed (d359aaha3l67dn.cloudfront.net)
- Load Balancer: Active and routing traffic

**Recent Activity (Last 2 hours):**
- 14 WebRTC sessions started
- 10 sessions completed successfully
- 81 WebSocket connections
- 303 DynamoDB saves

---

## Deliverable 1: Filtered Logs ✅

### Tool Created
**Location:** `/home/ubuntu/speak-to-input/scripts/filter_production_logs.sh`

**Usage:**
```bash
# Filter Voice Bot logs (last 2 hours)
./scripts/filter_production_logs.sh voice-bot 2

# Filter Browser Agent logs (last 1 hour)
./scripts/filter_production_logs.sh browser-agent 1

# Save to file
./scripts/filter_production_logs.sh voice-bot 1 /tmp/filtered_logs.txt
```

### Key Metrics (Last 2 Hours)
- **Sessions Created:** 14
- **Sessions Completed:** 10 (71% completion rate)
- **WebSocket Connections:** 81
- **Legitimate Errors:** 45 (excluding malicious requests)
- **Warnings:** 104 (mostly expected timeouts)
- **DynamoDB Operations:** 303 successful saves

### Legitimate Error Breakdown
1. **AWS Transcribe Timeouts:** 8 occurrences
   - Cause: 15-second silence timeout (expected behavior)
   - Action: None required

2. **ElevenLabs TTS Errors:** 6 occurrences
   - Cause: Voice settings policy violation
   - Action: Fix configuration in first message

3. **WebRTC Connection Timeouts:** ~10 occurrences
   - Cause: ICE gathering delays, UDP port restrictions
   - Action: Implement WebRTC optimizations (see Deliverable 3)

---

## Deliverable 2: Malicious Traffic Investigation ✅

### Investigation Results

**Source IP:** 172.31.78.80
**Identity:** Application Load Balancer internal interface
**Meaning:** Malicious requests originate from external internet sources, passing through ALB

### Attack Patterns Detected (Last 2 Hours)

1. **WebLogic Console RCE Attempts**
   - Pattern: `/console/bea-helpsets/...ShellSession...`
   - Frequency: Multiple per minute
   - Impact: None (rejected at protocol level)

2. **SendMail Injection**
   - Pattern: `/bsguest.cgi?...sendmail...`
   - Frequency: Intermittent
   - Impact: None (rejected at protocol level)

3. **Invalid HTTP Methods**
   - Pattern: `ABCD / HTTP/1.1`
   - Frequency: Constant background noise
   - Impact: None (rejected by aiohttp)

**Total Malicious Requests:** 141 in 2 hours (~1.2 per minute)

### Security Assessment
- ✅ **Backend is secure:** All malicious requests rejected at protocol level
- ⚠️ **Log noise:** Makes legitimate debugging harder
- ⚠️ **No WAF protection:** Requests reach backend before rejection
- ⚠️ **Public exposure:** ALB accepts all traffic from 0.0.0.0/0

### Mitigation Implemented

**1. WAF Configuration Created**
- **Location:** `/home/ubuntu/speak-to-input/infrastructure/terraform/waf.tf`
- **Features:**
  - Blocks known malicious paths (WebLogic, SendMail)
  - AWS Managed Rules (Core Rule Set, Known Bad Inputs)
  - Rate limiting (2000 req/5min per IP)
  - Geographic filtering (optional, currently in count mode)
  - CloudWatch logging for analysis

**2. Analysis Script**
- **Location:** `/home/ubuntu/speak-to-input/scripts/analyze_malicious_traffic.sh`
- **Usage:** `./scripts/analyze_malicious_traffic.sh`

### Deployment Recommendation
```bash
# Deploy WAF to protect ALB
cd infrastructure/terraform
terraform plan -target=aws_wafv2_web_acl.vpbank_voice_agent
terraform apply -target=aws_wafv2_web_acl.vpbank_voice_agent
```

**Expected Impact:**
- 95%+ reduction in malicious request log noise
- Block attacks at edge (before reaching backend)
- Detailed attack analytics via CloudWatch
- Protection against DDoS with rate limiting

---

## Deliverable 3: WebRTC Optimization ✅

### Documentation Created
**Location:** `/home/ubuntu/speak-to-input/docs/WEBRTC_OPTIMIZATION_GUIDE.md`

### Issues Identified

1. **Connection Timeouts** ⚠️
   - Symptom: `Timeout establishing the connection to the remote peer`
   - Frequency: ~30% of connection attempts
   - Cause: Single STUN server, UDP port restrictions, 60s timeout

2. **ICE Gathering Delays** ⚠️
   - Duration: 5-7 seconds (should be 2-3 seconds)
   - Impact: Poor user experience
   - Cause: Limited ICE candidate pool, single STUN server

3. **Audio Frame Timeouts** ⚠️
   - Frequency: During user silence
   - Impact: Session disconnections
   - Cause: Expected AWS Transcribe behavior (15s timeout)

### Optimization Recommendations

#### High Priority (Immediate)
1. **Multiple STUN Servers**
   ```python
   ice_servers = [
       IceServer(urls="stun:stun.l.google.com:19302"),
       IceServer(urls="stun:stun1.l.google.com:19302"),
       IceServer(urls="stun:stun2.l.google.com:19302"),
       # Existing TURN servers...
   ]
   ```

2. **UDP Port Configuration**
   ```bash
   # Open WebRTC media ports in Security Group
   aws ec2 authorize-security-group-ingress \
     --group-id sg-02c87c9c66309b96d \
     --protocol udp \
     --port 49152-65535 \
     --cidr 0.0.0.0/0
   ```

3. **Connection State Monitoring**
   - Add timeout configuration
   - Implement automatic reconnection
   - Monitor connection states

#### Medium Priority
4. Configure ICE gathering timeout (10 seconds)
5. Add connection keepalive
6. Implement CloudWatch metrics for WebRTC

#### Low Priority (Future)
7. Deploy dedicated TURN server
8. Implement adaptive bitrate
9. Add network quality indicators

### Expected Improvements
- **Connection Success Rate:** 95%+ (currently ~70%)
- **ICE Gathering Time:** 2-3 seconds (currently 5-7 seconds)
- **Connection Timeouts:** < 5% (currently ~30%)

---

## Deliverable 4: CloudWatch Alarms ✅

### Monitoring Infrastructure Created

**1. Terraform Configuration**
- **Location:** `/home/ubuntu/speak-to-input/infrastructure/terraform/cloudwatch_alarms.tf`
- **Components:** 15 alarms + 6 metric filters + CloudWatch dashboard + SNS topic

**2. Quick Setup Script**
- **Location:** `/home/ubuntu/speak-to-input/scripts/setup_cloudwatch_alarms.sh`
- **Usage:** `./scripts/setup_cloudwatch_alarms.sh admin@vpbank.com`

### Alarms Configured

#### Application Errors (Log-Based)
1. **WebRTC Connection Timeout** - Threshold: >5 in 5 min
2. **ElevenLabs TTS Errors** - Threshold: >10 in 5 min
3. **AWS Transcribe Errors** - Threshold: >10 in 5 min
4. **Critical Application Errors** - Threshold: >20 in 1 min
5. **Browser Service Failures** - Threshold: >5 in 5 min

#### Infrastructure Health
6. **Voice Bot Task Count Low** - Threshold: <1 task
7. **Browser Agent Task Count Low** - Threshold: <1 task
8. **Voice Bot Unhealthy Targets** - Threshold: >0 unhealthy
9. **Browser Agent Unhealthy Targets** - Threshold: >0 unhealthy
10. **ALB 5XX Errors** - Threshold: >10 in 5 min

#### Frontend & Distribution
11. **CloudFront 5XX Error Rate** - Threshold: >5%
12. **CloudFront 4XX Error Rate** - Threshold: >10% (attacks)

#### Database Performance
13. **DynamoDB Read Throttles** - Threshold: >5 in 1 min
14. **DynamoDB Write Throttles** - Threshold: >5 in 1 min

### Success Metrics (Tracked)
- Sessions Created (per 5 min)
- Sessions Completed (per 5 min)
- ECS Running Task Count
- ALB Response Time
- Request Count

### CloudWatch Dashboard
**Name:** VPBank-Voice-Agent-Production
**Widgets:**
1. Session Metrics (Created vs Completed)
2. Error Metrics (Timeouts, TTS, Transcribe)
3. ECS Running Tasks
4. ALB Performance

### Deployment

**Option 1: Terraform (Recommended)**
```bash
cd infrastructure/terraform
terraform plan
terraform apply
```

**Option 2: Quick Script**
```bash
./scripts/setup_cloudwatch_alarms.sh your-email@vpbank.com
```

**Post-Deployment:**
1. Confirm SNS email subscription (check inbox)
2. View dashboard: [CloudWatch Console](https://console.aws.amazon.com/cloudwatch)
3. Test alarms with sample errors

### Notification Setup
- **SNS Topic:** vpbank-voice-agent-alarms
- **Email:** Configurable via script parameter
- **Protocol:** Email (can add SMS, Slack, PagerDuty)

---

## Recommended Action Plan

### Immediate (Today)
1. ✅ **Deploy CloudWatch Alarms**
   ```bash
   ./scripts/setup_cloudwatch_alarms.sh admin@vpbank.com
   ```

2. ⏳ **Configure UDP Ports for WebRTC**
   ```bash
   aws ec2 authorize-security-group-ingress \
     --group-id sg-02c87c9c66309b96d \
     --protocol udp --port 49152-65535 \
     --cidr 0.0.0.0/0
   ```

3. ⏳ **Update STUN Server Configuration**
   - Add multiple STUN servers to `voice_bot.py`
   - Redeploy Voice Bot service

### Short-Term (This Week)
4. ⏳ **Deploy AWS WAF**
   ```bash
   cd infrastructure/terraform
   terraform apply -target=aws_wafv2_web_acl.vpbank_voice_agent
   ```

5. ⏳ **Implement WebRTC Auto-Reconnection**
   - Frontend: Add reconnection logic
   - Backend: Add connection monitoring

6. ⏳ **Fix ElevenLabs TTS Configuration**
   - Ensure voice_settings in first message only
   - Test with new sessions

### Medium-Term (Next 2 Weeks)
7. ⏳ **Add Custom CloudWatch Metrics**
   - WebRTC connection success rate
   - Session duration
   - Form completion rate

8. ⏳ **Enable ALB Access Logs**
   - Capture original source IPs
   - Analyze traffic patterns

9. ⏳ **Create Runbook for Common Issues**
   - Connection timeout troubleshooting
   - Service restart procedures
   - Escalation paths

---

## Monitoring URLs

**CloudWatch Dashboard:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=VPBank-Voice-Agent-Production
```

**CloudWatch Alarms:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:
```

**Custom Metrics:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#metricsV2:graph=~();namespace=VPBankVoiceAgent
```

**Log Insights:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:logs-insights
```

---

## Files Delivered

### Scripts
1. `scripts/filter_production_logs.sh` - Filter legitimate traffic
2. `scripts/analyze_malicious_traffic.sh` - Analyze attack patterns
3. `scripts/setup_cloudwatch_alarms.sh` - Deploy monitoring

### Infrastructure
4. `infrastructure/terraform/waf.tf` - WAF configuration
5. `infrastructure/terraform/cloudwatch_alarms.tf` - Monitoring setup

### Documentation
6. `docs/WEBRTC_OPTIMIZATION_GUIDE.md` - WebRTC improvements
7. `PRODUCTION_MONITORING_SUMMARY.md` - This document

---

## Success Metrics Baseline

**Current Performance (Pre-Optimization):**
- WebRTC Connection Success: ~70%
- ICE Gathering Time: 5-7 seconds
- Session Completion Rate: 71%
- Malicious Request Volume: 141 per 2 hours

**Target Performance (Post-Optimization):**
- WebRTC Connection Success: >95%
- ICE Gathering Time: 2-3 seconds
- Session Completion Rate: >90%
- Malicious Request Volume: <10 per 2 hours (with WAF)

---

## Support & Troubleshooting

**Check Service Health:**
```bash
./scripts/filter_production_logs.sh voice-bot 1
```

**View Alarms:**
```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix "vpbank-voice-agent" \
  --region us-east-1
```

**Test Alarm:**
```bash
aws cloudwatch set-alarm-state \
  --alarm-name "vpbank-voice-agent-critical-error-high" \
  --state-value ALARM \
  --state-reason "Testing alarm notification"
```

---

**Status:** Ready for production deployment
**Last Updated:** 2025-11-09 17:06 UTC
**Next Review:** After 1 week of monitoring with new alarms
