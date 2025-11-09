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
