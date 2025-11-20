# AWS WAF Configuration for VPBank Voice Agent
# Protects against common web attacks and malicious scanners

resource "aws_wafv2_web_acl" "vpbank_voice_agent" {
  name        = "vpbank-voice-agent-waf"
  description = "WAF for VPBank Voice Agent - blocks malicious requests"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Rule 1: Block known malicious paths (WebLogic, SendMail exploits)
  rule {
    name     = "BlockMaliciousPaths"
    priority = 1

    action {
      block {
        custom_response {
          response_code = 403
        }
      }
    }

    statement {
      or_statement {
        statement {
          byte_match_statement {
            search_string         = "/console/bea-helpsets"
            positional_constraint = "CONTAINS"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }

        statement {
          byte_match_statement {
            search_string         = "/bsguest.cgi"
            positional_constraint = "CONTAINS"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }

        statement {
          byte_match_statement {
            search_string         = "sendmail"
            positional_constraint = "CONTAINS"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }

        statement {
          byte_match_statement {
            search_string         = "ShellSession"
            positional_constraint = "CONTAINS"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "BlockMaliciousPaths"
      sampled_requests_enabled   = true
    }
  }

  # Rule 2: AWS Managed Rules - Core Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"

        # Exclude rule that might block legitimate WebRTC traffic
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "SizeRestrictions_BODY"
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Rule 3: AWS Managed Rules - Known Bad Inputs
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Rule 4: Rate limiting to prevent DDoS
  rule {
    name     = "RateLimitRule"
    priority = 4

    action {
      block {
        custom_response {
          response_code = 429
        }
      }
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  # Rule 5: Block invalid HTTP methods
  rule {
    name     = "BlockInvalidMethods"
    priority = 5

    action {
      block {
        custom_response {
          response_code = 405
        }
      }
    }

    statement {
      not_statement {
        statement {
          byte_match_statement {
            search_string         = "get"
            positional_constraint = "EXACTLY"
            field_to_match {
              method {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "BlockInvalidMethods"
      sampled_requests_enabled   = true
    }
  }

  # Rule 6: Geographic restriction (optional - restrict to Vietnam and common VPN countries)
  rule {
    name     = "GeoRestriction"
    priority = 6

    action {
      count {} # Start with count mode, change to block after testing
    }

    statement {
      not_statement {
        statement {
          geo_match_statement {
            country_codes = [
              "VN", # Vietnam
              "US", # United States
              "SG", # Singapore
              "JP", # Japan
              "KR", # South Korea
              "AU", # Australia
              "GB", # United Kingdom
              "DE", # Germany
              "FR", # France
              "CA", # Canada
            ]
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "GeoRestriction"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "vpbank-voice-agent-waf"
    sampled_requests_enabled   = true
  }

  tags = {
    Name        = "vpbank-voice-agent-waf"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Associate WAF with ALB
resource "aws_wafv2_web_acl_association" "alb" {
  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.vpbank_voice_agent.arn
}

# CloudWatch Log Group for WAF logs
resource "aws_cloudwatch_log_group" "waf_logs" {
  name              = "/aws/wafv2/vpbank-voice-agent"
  retention_in_days = 30

  tags = {
    Name        = "vpbank-voice-agent-waf-logs"
    Environment = "production"
  }
}

# WAF Logging Configuration
resource "aws_wafv2_web_acl_logging_configuration" "main" {
  resource_arn            = aws_wafv2_web_acl.vpbank_voice_agent.arn
  log_destination_configs = [aws_cloudwatch_log_group.waf_logs.arn]

  redacted_fields {
    single_header {
      name = "authorization"
    }
  }

  redacted_fields {
    single_header {
      name = "cookie"
    }
  }
}

# Output WAF Web ACL ARN
output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = aws_wafv2_web_acl.vpbank_voice_agent.arn
}

output "waf_web_acl_id" {
  description = "ID of the WAF Web ACL"
  value       = aws_wafv2_web_acl.vpbank_voice_agent.id
}
