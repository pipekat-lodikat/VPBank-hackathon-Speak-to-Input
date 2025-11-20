# Security Hardening Deployment Guide
**VPBank Voice Agent - AWS Security Implementation**

---

## Overview

This guide provides step-by-step instructions for deploying comprehensive security hardening for the VPBank Voice Agent infrastructure on AWS.

**Deployment Time:** ~2 hours
**Estimated Cost:** ~$70/month
**Risk Level:** Low (all changes are additive, non-breaking)

---

## Pre-Deployment Checklist

### ✅ Required Access
- [ ] AWS Console access with Administrator permissions
- [ ] AWS CLI configured with appropriate credentials
- [ ] Terraform installed (version ≥ 1.5.0)
- [ ] Bash shell access to deployment server

### ✅ Required Information
- [ ] Security alert email address
- [ ] Cognito User Pool ID (if restricting IAM policies)
- [ ] Current `.env` file with all credentials
- [ ] Backup of existing infrastructure state

### ✅ Pre-Deployment Tasks
- [ ] Review `AWS_SECURITY_ASSESSMENT.md`
- [ ] Backup current `.env` file
- [ ] Verify CloudTrail is enabled
- [ ] Notify team of deployment window

---

## Deployment Options

### Option 1: Automated Deployment (Recommended)

Use the automated script for complete security hardening:

```bash
# Full deployment with secrets migration
./scripts/deploy_security_hardening.sh --migrate-secrets

# Dry run to preview changes
./scripts/deploy_security_hardening.sh --dry-run
```

**What this does:**
1. Migrates credentials from `.env` to AWS Secrets Manager
2. Deploys all security hardening Terraform configurations
3. Enables GuardDuty, Security Hub, AWS Config
4. Configures KMS encryption for all services
5. Blocks S3 public access
6. Restricts IAM policies
7. Enables VPC Flow Logs

---

### Option 2: Manual Step-by-Step Deployment

For granular control, deploy each component separately:

---

## Step 1: Migrate Credentials to Secrets Manager

**Duration:** 15 minutes
**Risk:** Low (read-only, creates secrets)

```bash
# Review migration script
cat scripts/migrate_to_secrets_manager.sh

# Run migration
./scripts/migrate_to_secrets_manager.sh
```

**Expected Output:**
```
🔐 VPBank Voice Agent - Secrets Manager Migration
==================================================

📋 Step 1: Loading credentials from .env file...

📋 Step 2: Migrating credentials to Secrets Manager...

  📦 Processing: vpbank-voice-agent/openai-api-key
    + Creating new secret...
    ✅ Done

  📦 Processing: vpbank-voice-agent/elevenlabs-api-key
    + Creating new secret...
    ✅ Done

  ... (8 more secrets)

📋 Step 3: Verifying secrets...
  ✅ vpbank-voice-agent/openai-api-key
  ✅ vpbank-voice-agent/elevenlabs-api-key
  ... (8 more)

📊 Summary: 9/9 secrets migrated successfully
✅ All secrets migrated successfully!
```

**Verification:**
```bash
# List created secrets
aws secretsmanager list-secrets \
  --query 'SecretList[?starts_with(Name, `vpbank-voice-agent`)].Name' \
  --output table

# Test retrieving a secret (without exposing value)
aws secretsmanager describe-secret \
  --secret-id vpbank-voice-agent/openai-api-key
```

---

## Step 2: Review Terraform Changes

**Duration:** 10 minutes
**Risk:** None (review only)

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init -upgrade

# Review planned changes
terraform plan -out=security.tfplan

# Review specific resources
terraform plan | grep -A 5 "aws_guardduty_detector"
terraform plan | grep -A 5 "aws_securityhub_account"
terraform plan | grep -A 5 "aws_s3_bucket_public_access_block"
```

**Key Changes to Review:**
1. GuardDuty detector creation
2. Security Hub enablement
3. KMS key creation (4 keys: S3, Secrets, CloudWatch, ECS Exec)
4. S3 public access block
5. IAM policy restrictions
6. VPC Flow Logs enablement

---

## Step 3: Deploy Security Hardening

**Duration:** 30-45 minutes
**Risk:** Medium (changes IAM policies, may affect running services)

### 3a. Deploy Core Security Services

```bash
cd infrastructure/terraform

# Deploy GuardDuty
terraform apply -target=aws_guardduty_detector.main -auto-approve

# Deploy Security Hub
terraform apply -target=aws_securityhub_account.main -auto-approve
terraform apply -target=aws_securityhub_standards_subscription.cis -auto-approve
terraform apply -target=aws_securityhub_standards_subscription.aws_foundational -auto-approve

# Deploy AWS Config
terraform apply -target=aws_config_configuration_recorder.main -auto-approve
terraform apply -target=aws_config_delivery_channel.main -auto-approve
```

### 3b. Deploy Encryption (KMS)

```bash
# Create KMS keys
terraform apply \
  -target=aws_kms_key.s3 \
  -target=aws_kms_key.secrets \
  -target=aws_kms_key.cloudwatch \
  -target=aws_kms_key.ecs_exec \
  -auto-approve

# Create KMS aliases
terraform apply \
  -target=aws_kms_alias.s3 \
  -target=aws_kms_alias.secrets \
  -target=aws_kms_alias.cloudwatch \
  -auto-approve
```

### 3c. Deploy S3 Security

```bash
# Block S3 public access
terraform apply -target=aws_s3_bucket_public_access_block.frontend -auto-approve

# Enable S3 versioning
terraform apply -target=aws_s3_bucket_versioning.frontend -auto-approve

# Enable S3 encryption with KMS
terraform apply -target=aws_s3_bucket_server_side_encryption_configuration.frontend -auto-approve

# Enable S3 logging
terraform apply -target=aws_s3_bucket_logging.frontend -auto-approve
```

### 3d. Deploy VPC Flow Logs

```bash
terraform apply \
  -target=aws_flow_log.vpc \
  -target=aws_cloudwatch_log_group.vpc_flow_logs \
  -target=aws_iam_role.vpc_flow_logs \
  -auto-approve
```

### 3e. Deploy WAF

```bash
# Review WAF configuration
terraform plan -target=aws_wafv2_web_acl.vpbank_voice_agent

# Deploy WAF
terraform apply -target=aws_wafv2_web_acl.vpbank_voice_agent -auto-approve

# Associate WAF with ALB
terraform apply -target=aws_wafv2_web_acl_association.alb -auto-approve
```

### 3f. Update IAM Policies (Careful!)

⚠️ **IMPORTANT:** This step updates IAM policies. Test in non-production first.

```bash
# Review IAM policy changes
terraform plan -target=aws_iam_role_policy.ecs_task_policy_restricted

# Apply IAM policy changes
terraform apply -target=aws_iam_role_policy.ecs_task_policy_restricted -auto-approve

# Verify services still work
aws ecs describe-services \
  --cluster vpbank-voice-agent-cluster \
  --services voice-bot browser-agent
```

---

## Step 4: Update ECS Task Definitions

**Duration:** 20 minutes
**Risk:** Medium (requires service restart)

Update task definitions to use Secrets Manager instead of environment variables.

```bash
# Backup current task definitions
aws ecs describe-task-definition \
  --task-definition vpbank-voice-agent-voice-bot \
  > backup-voice-bot-task-def.json

aws ecs describe-task-definition \
  --task-definition vpbank-voice-agent-browser-agent \
  > backup-browser-agent-task-def.json
```

### Update Voice Bot Task Definition

Edit `infrastructure/terraform/ecs-tasks.tf`:

```hcl
# Replace environment variables with secrets
container_definitions = jsonencode([{
  name  = "voice-bot"
  image = "${aws_ecr_repository.voice_bot.repository_url}:latest"

  # Remove hardcoded environment variables
  # environment = [...]

  # Add secrets from Secrets Manager
  secrets = [
    {
      name      = "AWS_ACCESS_KEY_ID"
      valueFrom = "${aws_secretsmanager_secret.aws_credentials.arn}:access_key_id::"
    },
    {
      name      = "AWS_SECRET_ACCESS_KEY"
      valueFrom = "${aws_secretsmanager_secret.aws_credentials.arn}:secret_access_key::"
    },
    {
      name      = "OPENAI_API_KEY"
      valueFrom = aws_secretsmanager_secret.openai_api_key.arn
    },
    {
      name      = "ELEVENLABS_API_KEY"
      valueFrom = aws_secretsmanager_secret.elevenlabs_api_key.arn
    },
    # ... add all secrets
  ]
}])
```

### Deploy Updated Task Definitions

```bash
cd infrastructure/terraform

# Apply changes
terraform apply -target=aws_ecs_task_definition.voice_bot -auto-approve
terraform apply -target=aws_ecs_task_definition.browser_agent -auto-approve

# Force new deployment
aws ecs update-service \
  --cluster vpbank-voice-agent-cluster \
  --service voice-bot \
  --force-new-deployment

aws ecs update-service \
  --cluster vpbank-voice-agent-cluster \
  --service browser-agent \
  --force-new-deployment

# Monitor deployment
watch -n 5 "aws ecs describe-services \
  --cluster vpbank-voice-agent-cluster \
  --services voice-bot browser-agent \
  --query 'services[*].{Name:serviceName,Running:runningCount,Desired:desiredCount,Status:deployments[0].rolloutState}'"
```

---

## Step 5: Configure Notifications

**Duration:** 10 minutes
**Risk:** None

### Subscribe to SNS Topics

```bash
# Get SNS topic ARN
TOPIC_ARN=$(terraform output -raw guardduty_alerts_topic_arn 2>/dev/null || \
  aws sns list-topics --query "Topics[?contains(TopicArn, 'guardduty-alerts')].TopicArn" --output text)

# Subscribe email
aws sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol email \
  --notification-endpoint admin@vpbank.com

# Check email and confirm subscription
```

### Test Notifications

```bash
# Trigger test alarm
aws cloudwatch set-alarm-state \
  --alarm-name "vpbank-voice-agent-critical-error-high" \
  --state-value ALARM \
  --state-reason "Security deployment test"

# Check email for notification
```

---

## Step 6: Verification

**Duration:** 15 minutes

### 6a. Verify Security Services

```bash
# Check GuardDuty
aws guardduty list-detectors
aws guardduty get-detector --detector-id <detector-id>

# Check Security Hub
aws securityhub describe-hub
aws securityhub get-findings --max-results 10

# Check AWS Config
aws configservice describe-configuration-recorders
aws configservice describe-delivery-channels

# Check VPC Flow Logs
aws ec2 describe-flow-logs
```

### 6b. Verify S3 Security

```bash
BUCKET_NAME="vpbank-voice-agent-frontend-590183822512"

# Check public access block
aws s3api get-public-access-block --bucket "$BUCKET_NAME"

# Check versioning
aws s3api get-bucket-versioning --bucket "$BUCKET_NAME"

# Check encryption
aws s3api get-bucket-encryption --bucket "$BUCKET_NAME"

# Check logging
aws s3api get-bucket-logging --bucket "$BUCKET_NAME"
```

Expected output:
```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }
}
```

### 6c. Verify Secrets Manager

```bash
# List secrets
aws secretsmanager list-secrets \
  --query 'SecretList[?starts_with(Name, `vpbank-voice-agent`)].{Name:Name,LastChanged:LastChangedDate}' \
  --output table

# Test secret retrieval (without showing value)
aws secretsmanager describe-secret \
  --secret-id vpbank-voice-agent/openai-api-key
```

### 6d. Verify Services Still Running

```bash
# Check ECS services
aws ecs describe-services \
  --cluster vpbank-voice-agent-cluster \
  --services voice-bot browser-agent \
  --query 'services[*].{Name:serviceName,Status:status,Running:runningCount,Desired:desiredCount}'

# Check ALB targets
aws elbv2 describe-target-health \
  --target-group-arn <voice-bot-tg-arn> \
  --query 'TargetHealthDescriptions[*].{Target:Target.Id,Health:TargetHealth.State}'

# Test frontend
curl -I https://d359aaha3l67dn.cloudfront.net/

# Test backend API
curl http://<alb-dns>/health
```

### 6e. Verify WAF

```bash
# Check WAF association
aws wafv2 list-web-acls --scope REGIONAL --region us-east-1

# View WAF metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/WAFV2 \
  --metric-name BlockedRequests \
  --dimensions Name=Rule,Value=ALL \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

---

## Step 7: Post-Deployment Tasks

### 7a. Update Documentation

- [ ] Update `.env.example` to reference Secrets Manager
- [ ] Document secret rotation schedule
- [ ] Update runbooks with new procedures

### 7b. Cleanup

```bash
# Backup .env file
cp .env .env.backup.$(date +%Y%m%d)

# Encrypt backup
gpg -c .env.backup.$(date +%Y%m%d)

# Optional: Remove plaintext .env (after verifying everything works)
# rm .env
```

### 7c. Schedule Reviews

- [ ] Schedule weekly Security Hub review
- [ ] Schedule monthly GuardDuty findings review
- [ ] Schedule quarterly access review

---

## Rollback Procedures

If deployment causes issues:

### Rollback Secrets Manager Migration

```bash
# Services will fall back to .env file if it still exists
# Ensure .env file is present

# Remove Secrets Manager secrets
aws secretsmanager delete-secret \
  --secret-id vpbank-voice-agent/openai-api-key \
  --force-delete-without-recovery
```

### Rollback IAM Policies

```bash
# Revert to previous task definition
aws ecs update-service \
  --cluster vpbank-voice-agent-cluster \
  --service voice-bot \
  --task-definition vpbank-voice-agent-voice-bot:<previous-revision>
```

### Rollback Terraform Changes

```bash
cd infrastructure/terraform

# Destroy specific resources
terraform destroy -target=aws_guardduty_detector.main
terraform destroy -target=aws_securityhub_account.main

# Or restore from backup state
terraform state pull > current-state.json
# Restore from backup
terraform state push backup-state.json
```

---

## Troubleshooting

### Issue: Services fail to start after Secrets Manager migration

**Symptoms:**
- ECS tasks fail health checks
- Logs show "Unable to retrieve secret"

**Solution:**
```bash
# Check IAM role has Secrets Manager permissions
aws iam get-role-policy \
  --role-name vpbank-voice-agent-ecs-task-role \
  --policy-name vpbank-voice-agent-secrets-access

# Check secret exists
aws secretsmanager describe-secret \
  --secret-id vpbank-voice-agent/openai-api-key

# Check KMS key permissions
aws kms describe-key --key-id <kms-key-id>
```

### Issue: GuardDuty not sending alerts

**Solution:**
```bash
# Verify SNS subscription
aws sns list-subscriptions-by-topic \
  --topic-arn <topic-arn>

# Check subscription is confirmed
# If PendingConfirmation, check email and confirm

# Test notification
aws sns publish \
  --topic-arn <topic-arn> \
  --message "Test notification"
```

### Issue: WAF blocking legitimate traffic

**Solution:**
```bash
# Check WAF logs
aws wafv2 list-logging-configurations \
  --scope REGIONAL --region us-east-1

# Temporarily switch to COUNT mode
aws wafv2 update-web-acl \
  --id <web-acl-id> \
  --scope REGIONAL \
  --default-action Count={}
```

---

## Success Criteria

Deployment is successful when:

- [x] All Terraform resources created without errors
- [x] GuardDuty detector active
- [x] Security Hub showing findings
- [x] S3 public access blocked (verified)
- [x] Secrets in Secrets Manager (9 total)
- [x] ECS services running with 2/2 tasks
- [x] Frontend accessible via CloudFront
- [x] Backend API responding to health checks
- [x] WAF blocking malicious requests
- [x] VPC Flow Logs capturing traffic
- [x] SNS notifications received

---

## Monitoring Post-Deployment

### Daily (First Week)
- Check Security Hub for new findings
- Review GuardDuty alerts
- Monitor CloudWatch alarms
- Verify service health

### Weekly
- Review Security Hub compliance score
- Analyze VPC Flow Logs for anomalies
- Check WAF blocked request metrics
- Review cost impact

### Monthly
- Conduct access review
- Rotate secrets (if not automated)
- Review and update security policies
- Update security documentation

---

## Cost Monitoring

Track actual costs vs. estimates:

```bash
# Get cost for last 30 days
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://cost-filter.json

# cost-filter.json:
# {
#   "Tags": {
#     "Key": "Project",
#     "Values": ["vpbank-voice-agent"]
#   }
# }
```

---

## Next Steps

After successful deployment:

1. **Compliance Certification**
   - Work towards SOC2 Type II
   - Achieve ISO 27001 certification

2. **Advanced Security**
   - Implement AWS Detective
   - Deploy AWS Network Firewall
   - Enable AWS Shield Advanced

3. **Automation**
   - Automated incident response
   - Self-healing infrastructure
   - Continuous compliance monitoring

4. **Penetration Testing**
   - Hire third-party security firm
   - Conduct annual pen tests
   - Implement bug bounty program

---

## Support

For issues during deployment:

1. Check logs: `aws logs tail /ecs/vpbank-voice-agent/<service> --follow`
2. Review Terraform output for errors
3. Consult AWS documentation
4. Contact AWS Support

---

**Document Version:** 1.0
**Last Updated:** November 9, 2025
**Maintained By:** DevOps/Security Team
