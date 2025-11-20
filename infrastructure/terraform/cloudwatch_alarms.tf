# CloudWatch Alarms for VPBank Voice Agent Production Monitoring

# SNS Topic for Alarm Notifications
resource "aws_sns_topic" "vpbank_voice_agent_alarms" {
  name = "vpbank-voice-agent-alarms"

  tags = {
    Name        = "vpbank-voice-agent-alarms"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# SNS Topic Subscription (Email)
resource "aws_sns_topic_subscription" "alarm_email" {
  topic_arn = aws_sns_topic.vpbank_voice_agent_alarms.arn
  protocol  = "email"
  endpoint  = var.alarm_email # Set this in terraform.tfvars
}

# ========== ECS Service Alarms ==========

# Alarm: Voice Bot Service - Running Task Count Low
resource "aws_cloudwatch_metric_alarm" "voice_bot_task_count_low" {
  alarm_name          = "vpbank-voice-agent-voice-bot-task-count-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "RunningTaskCount"
  namespace           = "ECS/ContainerInsights"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Voice Bot service has less than expected running tasks"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "breaching"

  dimensions = {
    ServiceName = "voice-bot"
    ClusterName = "vpbank-voice-agent-cluster"
  }

  tags = {
    Name        = "voice-bot-task-count-alarm"
    Environment = "production"
  }
}

# Alarm: Browser Agent Service - Running Task Count Low
resource "aws_cloudwatch_metric_alarm" "browser_agent_task_count_low" {
  alarm_name          = "vpbank-voice-agent-browser-agent-task-count-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "RunningTaskCount"
  namespace           = "ECS/ContainerInsights"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Browser Agent service has less than expected running tasks"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "breaching"

  dimensions = {
    ServiceName = "browser-agent"
    ClusterName = "vpbank-voice-agent-cluster"
  }

  tags = {
    Name        = "browser-agent-task-count-alarm"
    Environment = "production"
  }
}

# ========== Application Log-Based Alarms ==========

# Metric Filter: WebRTC Connection Timeouts
resource "aws_cloudwatch_log_metric_filter" "webrtc_timeout" {
  name           = "webrtc-connection-timeout"
  log_group_name = "/ecs/vpbank-voice-agent/voice-bot"
  pattern        = "[time, level, location, msg=\"Timeout establishing the connection*\"]"

  metric_transformation {
    name      = "WebRTCConnectionTimeout"
    namespace = "VPBankVoiceAgent"
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_metric_alarm" "webrtc_timeout_high" {
  alarm_name          = "vpbank-voice-agent-webrtc-timeout-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "WebRTCConnectionTimeout"
  namespace           = "VPBankVoiceAgent"
  period              = 300 # 5 minutes
  statistic           = "Sum"
  threshold           = 5 # More than 5 timeouts in 5 minutes
  alarm_description   = "High rate of WebRTC connection timeouts detected"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Name        = "webrtc-timeout-alarm"
    Environment = "production"
  }
}

# Metric Filter: ElevenLabs TTS Errors
resource "aws_cloudwatch_log_metric_filter" "elevenlabs_error" {
  name           = "elevenlabs-tts-error"
  log_group_name = "/ecs/vpbank-voice-agent/voice-bot"
  pattern        = "[time, level=ERROR, location, msg=\"*ElevenLabsTTSService*\"]"

  metric_transformation {
    name      = "ElevenLabsTTSError"
    namespace = "VPBankVoiceAgent"
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_metric_alarm" "elevenlabs_error_high" {
  alarm_name          = "vpbank-voice-agent-elevenlabs-error-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ElevenLabsTTSError"
  namespace           = "VPBankVoiceAgent"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "High rate of ElevenLabs TTS errors"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Name        = "elevenlabs-error-alarm"
    Environment = "production"
  }
}

# Metric Filter: AWS Transcribe Errors
resource "aws_cloudwatch_log_metric_filter" "transcribe_error" {
  name           = "transcribe-connection-error"
  log_group_name = "/ecs/vpbank-voice-agent/voice-bot"
  pattern        = "[time, level=ERROR, location, msg=\"*AWSTranscribeSTTService*\"]"

  metric_transformation {
    name      = "TranscribeConnectionError"
    namespace = "VPBankVoiceAgent"
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_metric_alarm" "transcribe_error_high" {
  alarm_name          = "vpbank-voice-agent-transcribe-error-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "TranscribeConnectionError"
  namespace           = "VPBankVoiceAgent"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "High rate of AWS Transcribe connection errors"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Name        = "transcribe-error-alarm"
    Environment = "production"
  }
}

# Metric Filter: Browser Service Connection Failures
resource "aws_cloudwatch_log_metric_filter" "browser_service_failure" {
  name           = "browser-service-connection-failure"
  log_group_name = "/ecs/vpbank-voice-agent/voice-bot"
  pattern        = "[time, level=ERROR, location, msg=\"*Browser Service*connection*\"]"

  metric_transformation {
    name      = "BrowserServiceConnectionFailure"
    namespace = "VPBankVoiceAgent"
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_metric_alarm" "browser_service_failure_high" {
  alarm_name          = "vpbank-voice-agent-browser-service-failure-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "BrowserServiceConnectionFailure"
  namespace           = "VPBankVoiceAgent"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "High rate of Browser Service connection failures"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Name        = "browser-service-failure-alarm"
    Environment = "production"
  }
}

# Metric Filter: Session Creation Success
resource "aws_cloudwatch_log_metric_filter" "session_created" {
  name           = "session-created-success"
  log_group_name = "/ecs/vpbank-voice-agent/voice-bot"
  pattern        = "[time, level=INFO, location, msg=\"*Starting voice bot*\"]"

  metric_transformation {
    name      = "SessionCreated"
    namespace = "VPBankVoiceAgent"
    value     = "1"
    unit      = "Count"
  }
}

# Metric Filter: Session Completion Success
resource "aws_cloudwatch_log_metric_filter" "session_completed" {
  name           = "session-completed-success"
  log_group_name = "/ecs/vpbank-voice-agent/voice-bot"
  pattern        = "[time, level=INFO, location, msg=\"*Session completed*\"]"

  metric_transformation {
    name      = "SessionCompleted"
    namespace = "VPBankVoiceAgent"
    value     = "1"
    unit      = "Count"
  }
}

# Metric Filter: Critical Application Errors
resource "aws_cloudwatch_log_metric_filter" "critical_error" {
  name           = "critical-application-error"
  log_group_name = "/ecs/vpbank-voice-agent/voice-bot"
  pattern        = "[time, level=ERROR|CRITICAL, ...]"

  metric_transformation {
    name      = "CriticalError"
    namespace = "VPBankVoiceAgent"
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_metric_alarm" "critical_error_high" {
  alarm_name          = "vpbank-voice-agent-critical-error-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CriticalError"
  namespace           = "VPBankVoiceAgent"
  period              = 60
  statistic           = "Sum"
  threshold           = 20 # More than 20 errors per minute
  alarm_description   = "High rate of critical application errors"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Name        = "critical-error-alarm"
    Environment = "production"
  }
}

# ========== ALB Health Check Alarms ==========

# Alarm: Voice Bot Target Group Unhealthy
resource "aws_cloudwatch_metric_alarm" "voice_bot_unhealthy_hosts" {
  alarm_name          = "vpbank-voice-agent-voice-bot-unhealthy-hosts"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 0
  alarm_description   = "Voice Bot targets are unhealthy"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    TargetGroup  = "targetgroup/vpbank-va-voice-tg/ae94fb33d60195af"
    LoadBalancer = "app/vpbank-voice-agent-alb/21a2eda047609e0d"
  }

  tags = {
    Name        = "voice-bot-unhealthy-alarm"
    Environment = "production"
  }
}

# Alarm: Browser Agent Target Group Unhealthy
resource "aws_cloudwatch_metric_alarm" "browser_agent_unhealthy_hosts" {
  alarm_name          = "vpbank-voice-agent-browser-agent-unhealthy-hosts"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 0
  alarm_description   = "Browser Agent targets are unhealthy"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    TargetGroup  = aws_lb_target_group.browser_agent.arn_suffix
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name        = "browser-agent-unhealthy-alarm"
    Environment = "production"
  }
}

# Alarm: ALB 5XX Errors
resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
  alarm_name          = "vpbank-voice-agent-alb-5xx-errors-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "High rate of 5XX errors from ALB targets"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name        = "alb-5xx-errors-alarm"
    Environment = "production"
  }
}

# ========== CloudFront Alarms ==========

# Alarm: CloudFront 5XX Error Rate
resource "aws_cloudwatch_metric_alarm" "cloudfront_5xx_errors" {
  alarm_name          = "vpbank-voice-agent-cloudfront-5xx-errors-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = 300
  statistic           = "Average"
  threshold           = 5 # 5% error rate
  alarm_description   = "High rate of 5XX errors from CloudFront"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    DistributionId = "E157XTMGCFVXEO"
  }

  tags = {
    Name        = "cloudfront-5xx-errors-alarm"
    Environment = "production"
  }
}

# Alarm: CloudFront 4XX Error Rate (potential attacks)
resource "aws_cloudwatch_metric_alarm" "cloudfront_4xx_errors" {
  alarm_name          = "vpbank-voice-agent-cloudfront-4xx-errors-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "4xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = 300
  statistic           = "Average"
  threshold           = 10 # 10% error rate
  alarm_description   = "High rate of 4XX errors from CloudFront (potential attacks or bad requests)"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    DistributionId = "E157XTMGCFVXEO"
  }

  tags = {
    Name        = "cloudfront-4xx-errors-alarm"
    Environment = "production"
  }
}

# ========== DynamoDB Alarms ==========

# Alarm: DynamoDB Read Throttles
resource "aws_cloudwatch_metric_alarm" "dynamodb_read_throttle" {
  alarm_name          = "vpbank-voice-agent-dynamodb-read-throttle"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ReadThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "DynamoDB read throttling detected"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    TableName = "vpbank-voice-agent-sessions"
  }

  tags = {
    Name        = "dynamodb-read-throttle-alarm"
    Environment = "production"
  }
}

# Alarm: DynamoDB Write Throttles
resource "aws_cloudwatch_metric_alarm" "dynamodb_write_throttle" {
  alarm_name          = "vpbank-voice-agent-dynamodb-write-throttle"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "WriteThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "DynamoDB write throttling detected"
  alarm_actions       = [aws_sns_topic.vpbank_voice_agent_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    TableName = "vpbank-voice-agent-sessions"
  }

  tags = {
    Name        = "dynamodb-write-throttle-alarm"
    Environment = "production"
  }
}

# ========== Custom Dashboard ==========

resource "aws_cloudwatch_dashboard" "vpbank_voice_agent" {
  dashboard_name = "VPBank-Voice-Agent-Production"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["VPBankVoiceAgent", "SessionCreated", { stat = "Sum", label = "Sessions Created" }],
            [".", "SessionCompleted", { stat = "Sum", label = "Sessions Completed" }],
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Session Metrics"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["VPBankVoiceAgent", "WebRTCConnectionTimeout", { stat = "Sum" }],
            [".", "ElevenLabsTTSError", { stat = "Sum" }],
            [".", "TranscribeConnectionError", { stat = "Sum" }],
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Error Metrics"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["ECS/ContainerInsights", "RunningTaskCount", { stat = "Average", dimensions = { ServiceName = "voice-bot", ClusterName = "vpbank-voice-agent-cluster" } }],
            ["...", { dimensions = { ServiceName = "browser-agent", ClusterName = "vpbank-voice-agent-cluster" } }],
          ]
          period = 60
          stat   = "Average"
          region = var.aws_region
          title  = "ECS Running Tasks"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", { stat = "Average", dimensions = { LoadBalancer = "app/vpbank-voice-agent-alb/21a2eda047609e0d" } }],
            [".", "RequestCount", { stat = "Sum" }],
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "ALB Performance"
        }
      },
    ]
  })
}

# Variables
variable "alarm_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
  default     = "admin@vpbank.com"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# Outputs
output "sns_topic_arn" {
  description = "ARN of the SNS topic for alarms"
  value       = aws_sns_topic.vpbank_voice_agent_alarms.arn
}

output "dashboard_url" {
  description = "URL to the CloudWatch Dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=VPBank-Voice-Agent-Production"
}
