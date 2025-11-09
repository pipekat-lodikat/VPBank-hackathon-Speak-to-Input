variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "vpbank-voice-agent"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

variable "voice_bot_count" {
  description = "Number of Voice Bot tasks"
  type        = number
  default     = 2
}

variable "browser_agent_count" {
  description = "Number of Browser Agent tasks"
  type        = number
  default     = 2
}

#--------------------------------------------------------------
# Security-related Variables
#--------------------------------------------------------------

variable "security_alert_email" {
  description = "Email address for security alerts (GuardDuty, Security Hub)"
  type        = string
  default     = "admin@vpbank.com"
}

variable "enable_guardduty" {
  description = "Enable AWS GuardDuty for threat detection"
  type        = bool
  default     = true
}

variable "enable_security_hub" {
  description = "Enable AWS Security Hub for compliance monitoring"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config for resource compliance"
  type        = bool
  default     = true
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs for network monitoring"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 30
}

variable "cognito_user_pool_id" {
  description = "Cognito User Pool ID (for IAM policy restriction)"
  type        = string
  default     = ""
}

variable "bedrock_model_id" {
  description = "AWS Bedrock model ID"
  type        = string
  default     = "us.anthropic.claude-sonnet-4-20250514-v1:0"
}
