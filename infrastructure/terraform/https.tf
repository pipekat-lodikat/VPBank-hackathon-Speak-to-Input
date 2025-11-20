#--------------------------------------------------------------
# HTTPS Configuration for ALB
# Fixes mixed content security issue (HTTPS frontend → HTTP backend)
#--------------------------------------------------------------

# Variables for HTTPS configuration
variable "enable_https" {
  description = "Enable HTTPS listener on ALB"
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "Domain name for SSL certificate (optional, uses ALB DNS if not provided)"
  type        = string
  default     = ""
}

variable "redirect_http_to_https" {
  description = "Redirect HTTP traffic to HTTPS"
  type        = bool
  default     = false
}

#--------------------------------------------------------------
# Self-Signed Certificate (For Development/Testing)
#--------------------------------------------------------------

# Generate private key
resource "tls_private_key" "alb" {
  count     = var.enable_https && var.domain_name == "" ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Generate self-signed certificate
resource "tls_self_signed_cert" "alb" {
  count           = var.enable_https && var.domain_name == "" ? 1 : 0
  private_key_pem = tls_private_key.alb[0].private_key_pem

  subject {
    common_name  = aws_lb.main.dns_name
    organization = "VPBank Voice Agent"
  }

  validity_period_hours = 8760 # 1 year

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

# Import self-signed certificate to ACM
resource "aws_acm_certificate" "self_signed" {
  count             = var.enable_https && var.domain_name == "" ? 1 : 0
  private_key       = tls_private_key.alb[0].private_key_pem
  certificate_body  = tls_self_signed_cert.alb[0].cert_pem

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "${var.project_name}-self-signed-cert"
    Description = "Self-signed certificate for ALB HTTPS (development only)"
  }
}

#--------------------------------------------------------------
# ACM Certificate (For Production with Custom Domain)
#--------------------------------------------------------------

# Request ACM certificate for custom domain
resource "aws_acm_certificate" "main" {
  count             = var.enable_https && var.domain_name != "" ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.project_name}-acm-cert"
  }
}

# Output for DNS validation (user must manually create DNS records)
output "acm_validation_records" {
  description = "DNS records needed for ACM certificate validation"
  value = var.enable_https && var.domain_name != "" ? {
    for dvo in aws_acm_certificate.main[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      value  = dvo.resource_record_value
    }
  } : {}
}

#--------------------------------------------------------------
# HTTPS Listener (Port 443)
#--------------------------------------------------------------

resource "aws_lb_listener" "https" {
  count             = var.enable_https ? 1 : 0
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  # Use self-signed cert if no domain provided, otherwise use ACM cert
  certificate_arn = var.domain_name == "" ? aws_acm_certificate.self_signed[0].arn : aws_acm_certificate.main[0].arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.voice_bot.arn
  }

  tags = {
    Name = "${var.project_name}-https-listener"
  }

  depends_on = [
    aws_lb.main,
    aws_lb_target_group.voice_bot
  ]
}

# HTTPS Listener Rule for Browser Agent
resource "aws_lb_listener_rule" "browser_agent_https" {
  count        = var.enable_https ? 1 : 0
  listener_arn = aws_lb_listener.https[0].arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.browser_agent.arn
  }

  condition {
    path_pattern {
      values = ["/api/browser/*", "/api/execute", "/api/health", "/api/live"]
    }
  }

  tags = {
    Name = "${var.project_name}-browser-agent-https-rule"
  }
}

#--------------------------------------------------------------
# HTTP to HTTPS Redirect (Optional)
#--------------------------------------------------------------

# Modify existing HTTP listener to redirect to HTTPS
resource "aws_lb_listener" "http_redirect" {
  count             = var.enable_https && var.redirect_http_to_https ? 1 : 0
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = {
    Name = "${var.project_name}-http-redirect-listener"
  }
}

#--------------------------------------------------------------
# Outputs
#--------------------------------------------------------------

output "alb_https_url" {
  description = "HTTPS URL for Application Load Balancer"
  value       = var.enable_https ? "https://${aws_lb.main.dns_name}" : "Not enabled"
}

output "https_enabled" {
  description = "Whether HTTPS is enabled"
  value       = var.enable_https
}

output "certificate_type" {
  description = "Type of certificate being used"
  value       = var.enable_https ? (var.domain_name == "" ? "self-signed (development)" : "ACM (production)") : "none"
}
