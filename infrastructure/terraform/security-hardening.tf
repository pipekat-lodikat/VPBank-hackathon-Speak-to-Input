# AWS Security Hardening Configuration
# This file implements comprehensive security best practices for VPBank Voice Agent

#--------------------------------------------------------------
# S3 Bucket Security Hardening
#--------------------------------------------------------------

# Enable versioning for frontend bucket
resource "aws_s3_bucket_versioning" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable public access block for frontend bucket
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable server-side encryption with KMS
resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 bucket encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "${var.project_name}-s3-kms-key"
  }
}

resource "aws_kms_alias" "s3" {
  name          = "alias/${var.project_name}-s3"
  target_key_id = aws_kms_key.s3.key_id
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true
  }
}

# Enable S3 bucket logging
resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_name}-access-logs-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_logging" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "frontend-access-logs/"
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "delete-old-logs"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

#--------------------------------------------------------------
# AWS Secrets Manager for Sensitive Credentials
#--------------------------------------------------------------

# Create secrets for API keys and credentials
resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "${var.project_name}/openai-api-key"
  description             = "OpenAI API Key for browser automation"
  recovery_window_in_days = 30

  tags = {
    Name        = "${var.project_name}-openai-api-key"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret" "elevenlabs_api_key" {
  name                    = "${var.project_name}/elevenlabs-api-key"
  description             = "ElevenLabs API Key for TTS"
  recovery_window_in_days = 30

  tags = {
    Name        = "${var.project_name}-elevenlabs-api-key"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret" "aws_credentials" {
  name                    = "${var.project_name}/aws-credentials"
  description             = "AWS credentials for Transcribe/Bedrock"
  recovery_window_in_days = 30

  tags = {
    Name        = "${var.project_name}-aws-credentials"
    Environment = var.environment
  }
}

# Grant ECS tasks permission to read secrets
resource "aws_iam_role_policy" "secrets_access" {
  name = "${var.project_name}-secrets-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.openai_api_key.arn,
          aws_secretsmanager_secret.elevenlabs_api_key.arn,
          aws_secretsmanager_secret.aws_credentials.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.secrets.arn
      }
    ]
  })
}

# KMS key for Secrets Manager encryption
resource "aws_kms_key" "secrets" {
  description             = "KMS key for Secrets Manager"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "${var.project_name}-secrets-kms-key"
  }
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.project_name}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

#--------------------------------------------------------------
# IAM Policy Hardening - Least Privilege Principle
#--------------------------------------------------------------

# Replace overly permissive IAM policies
resource "aws_iam_role_policy" "ecs_task_policy_restricted" {
  name = "${var.project_name}-ecs-task-policy-restricted"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockInvokeModel"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/us.anthropic.claude-sonnet-4-*"
        ]
      },
      {
        Sid    = "TranscribeStreamAccess"
        Effect = "Allow"
        Action = [
          "transcribe:StartStreamTranscription",
          "transcribe:StartStreamTranscriptionWebSocket"
        ]
        Resource = "*" # Transcribe doesn't support resource-level permissions
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = var.aws_region
          }
        }
      },
      {
        Sid    = "DynamoDBTableAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = [
          "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/vpbank-sessions",
          "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/vpbank-sessions/index/*"
        ]
      },
      {
        Sid    = "CognitoRestrictedAccess"
        Effect = "Allow"
        Action = [
          "cognito-idp:AdminInitiateAuth",
          "cognito-idp:AdminGetUser",
          "cognito-idp:AdminUpdateUserAttributes",
          "cognito-idp:ListUsers"
        ]
        Resource = [
          "arn:aws:cognito-idp:${var.aws_region}:${data.aws_caller_identity.current.account_id}:userpool/${var.cognito_user_pool_id}"
        ]
      }
    ]
  })
}

#--------------------------------------------------------------
# CloudWatch Logs Encryption
#--------------------------------------------------------------

resource "aws_kms_key" "cloudwatch" {
  description             = "KMS key for CloudWatch Logs encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${var.aws_region}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnLike = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.project_name}/*"
          }
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-cloudwatch-kms-key"
  }
}

resource "aws_kms_alias" "cloudwatch" {
  name          = "alias/${var.project_name}-cloudwatch"
  target_key_id = aws_kms_key.cloudwatch.key_id
}

# Update CloudWatch log groups with encryption
resource "aws_cloudwatch_log_group" "voice_bot_encrypted" {
  name              = "/ecs/${var.project_name}/voice-bot-encrypted"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cloudwatch.arn

  tags = {
    Name        = "${var.project_name}-voice-bot-logs"
    Environment = var.environment
    Encrypted   = "true"
  }
}

resource "aws_cloudwatch_log_group" "browser_agent_encrypted" {
  name              = "/ecs/${var.project_name}/browser-agent-encrypted"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cloudwatch.arn

  tags = {
    Name        = "${var.project_name}-browser-agent-logs"
    Environment = var.environment
    Encrypted   = "true"
  }
}

#--------------------------------------------------------------
# VPC Flow Logs for Network Monitoring
#--------------------------------------------------------------

resource "aws_flow_log" "vpc" {
  vpc_id          = data.aws_vpc.default.id
  traffic_type    = "ALL"
  iam_role_arn    = aws_iam_role.vpc_flow_logs.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_logs.arn

  tags = {
    Name = "${var.project_name}-vpc-flow-logs"
  }
}

resource "aws_cloudwatch_log_group" "vpc_flow_logs" {
  name              = "/aws/vpc/${var.project_name}"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.cloudwatch.arn
}

resource "aws_iam_role" "vpc_flow_logs" {
  name = "${var.project_name}-vpc-flow-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "vpc-flow-logs.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "vpc_flow_logs" {
  name = "${var.project_name}-vpc-flow-logs-policy"
  role = aws_iam_role.vpc_flow_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "${aws_cloudwatch_log_group.vpc_flow_logs.arn}:*"
      }
    ]
  })
}

#--------------------------------------------------------------
# GuardDuty for Threat Detection
#--------------------------------------------------------------

resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = false # Not using EKS
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  finding_publishing_frequency = "FIFTEEN_MINUTES"

  tags = {
    Name        = "${var.project_name}-guardduty"
    Environment = var.environment
  }
}

# SNS topic for GuardDuty alerts
resource "aws_sns_topic" "guardduty_alerts" {
  name              = "${var.project_name}-guardduty-alerts"
  kms_master_key_id = aws_kms_key.secrets.id

  tags = {
    Name = "${var.project_name}-guardduty-alerts"
  }
}

resource "aws_sns_topic_subscription" "guardduty_email" {
  topic_arn = aws_sns_topic.guardduty_alerts.arn
  protocol  = "email"
  endpoint  = var.security_alert_email
}

# EventBridge rule for high-severity GuardDuty findings
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "${var.project_name}-guardduty-high-severity"
  description = "Capture high severity GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      severity = [
        { numeric = [">=", 7] } # High and Critical findings
      ]
    }
  })
}

resource "aws_cloudwatch_event_target" "guardduty_sns" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.guardduty_alerts.arn
}

#--------------------------------------------------------------
# AWS Config for Compliance Monitoring
#--------------------------------------------------------------

resource "aws_config_configuration_recorder" "main" {
  name     = "${var.project_name}-config-recorder"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

resource "aws_config_delivery_channel" "main" {
  name           = "${var.project_name}-config-delivery"
  s3_bucket_name = aws_s3_bucket.config.bucket

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  is_enabled = true

  depends_on = [aws_config_delivery_channel.main]
}

resource "aws_s3_bucket" "config" {
  bucket = "${var.project_name}-config-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "config" {
  bucket = aws_s3_bucket.config.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_role" "config" {
  name = "${var.project_name}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "config.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "config" {
  role       = aws_iam_role.config.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/ConfigRole"
}

# AWS Config Rules for Security Compliance
resource "aws_config_config_rule" "encrypted_volumes" {
  name = "${var.project_name}-encrypted-volumes"

  source {
    owner             = "AWS"
    source_identifier = "ENCRYPTED_VOLUMES"
  }

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_config_rule" "s3_bucket_public_read_prohibited" {
  name = "${var.project_name}-s3-public-read-prohibited"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_PUBLIC_READ_PROHIBITED"
  }

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_config_rule" "s3_bucket_public_write_prohibited" {
  name = "${var.project_name}-s3-public-write-prohibited"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_PUBLIC_WRITE_PROHIBITED"
  }

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_config_rule" "iam_password_policy" {
  name = "${var.project_name}-iam-password-policy"

  source {
    owner             = "AWS"
    source_identifier = "IAM_PASSWORD_POLICY"
  }

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_config_rule" "cloudtrail_enabled" {
  name = "${var.project_name}-cloudtrail-enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUD_TRAIL_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.main]
}

#--------------------------------------------------------------
# Security Hub for Centralized Security Findings
#--------------------------------------------------------------

resource "aws_securityhub_account" "main" {
  enable_default_standards = true
  control_finding_generator = "SECURITY_CONTROL"
}

resource "aws_securityhub_standards_subscription" "cis" {
  standards_arn = "arn:aws:securityhub:${var.aws_region}::standards/cis-aws-foundations-benchmark/v/1.4.0"
  depends_on    = [aws_securityhub_account.main]
}

resource "aws_securityhub_standards_subscription" "aws_foundational" {
  standards_arn = "arn:aws:securityhub:${var.aws_region}::standards/aws-foundational-security-best-practices/v/1.0.0"
  depends_on    = [aws_securityhub_account.main]
}

#--------------------------------------------------------------
# ECS Task Definition Security Enhancements
#--------------------------------------------------------------

# Enable ECS Exec encryption
resource "aws_kms_key" "ecs_exec" {
  description             = "KMS key for ECS Exec encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "${var.project_name}-ecs-exec-kms-key"
  }
}

#--------------------------------------------------------------
# Outputs
#--------------------------------------------------------------

output "kms_keys" {
  description = "KMS key ARNs for encryption"
  value = {
    s3         = aws_kms_key.s3.arn
    secrets    = aws_kms_key.secrets.arn
    cloudwatch = aws_kms_key.cloudwatch.arn
    ecs_exec   = aws_kms_key.ecs_exec.arn
  }
}

output "secrets_manager_arns" {
  description = "Secrets Manager secret ARNs"
  value = {
    openai_api_key     = aws_secretsmanager_secret.openai_api_key.arn
    elevenlabs_api_key = aws_secretsmanager_secret.elevenlabs_api_key.arn
    aws_credentials    = aws_secretsmanager_secret.aws_credentials.arn
  }
}

output "guardduty_detector_id" {
  description = "GuardDuty detector ID"
  value       = aws_guardduty_detector.main.id
}

output "security_hub_arn" {
  description = "Security Hub ARN"
  value       = aws_securityhub_account.main.arn
}
