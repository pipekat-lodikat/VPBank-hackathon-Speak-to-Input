# Network Load Balancer for WebRTC Support
# NLB supports UDP traffic required for WebRTC

resource "aws_lb" "nlb" {
  name               = "vpbank-voice-nlb"
  load_balancer_type = "network"
  subnets            = aws_subnet.public[*].id
  
  enable_cross_zone_load_balancing = true
  
  tags = {
    Name        = "vpbank-voice-nlb"
    Project     = "vpbank-voice-agent"
    Environment = "production"
  }
}

# Target Group for Voice Bot (TCP)
resource "aws_lb_target_group" "voice_tcp" {
  name        = "vpbank-voice-tcp"
  port        = 7860
  protocol    = "TCP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  
  health_check {
    enabled             = true
    protocol            = "TCP"
    port                = 7860
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
  }
  
  tags = {
    Name = "vpbank-voice-tcp"
  }
}

# Target Group for Browser Agent (TCP)
resource "aws_lb_target_group" "browser_tcp" {
  name        = "vpbank-browser-tcp"
  port        = 7863
  protocol    = "TCP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  
  health_check {
    enabled             = true
    protocol            = "TCP"
    port                = 7863
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
  }
  
  tags = {
    Name = "vpbank-browser-tcp"
  }
}

# Target Group for WebRTC STUN (UDP)
resource "aws_lb_target_group" "stun_udp" {
  name        = "vpbank-stun-udp"
  port        = 3478
  protocol    = "UDP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  
  health_check {
    enabled             = true
    protocol            = "TCP"
    port                = 7860  # Health check on TCP port
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
  }
  
  tags = {
    Name = "vpbank-stun-udp"
  }
}

# Target Group for WebRTC Media (UDP)
resource "aws_lb_target_group" "media_udp" {
  name        = "vpbank-media-udp"
  port        = 50000
  protocol    = "UDP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  
  health_check {
    enabled             = true
    protocol            = "TCP"
    port                = 7860  # Health check on TCP port
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
  }
  
  tags = {
    Name = "vpbank-media-udp"
  }
}

# Listener: Voice Bot TCP
resource "aws_lb_listener" "voice_tcp" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = 7860
  protocol          = "TCP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.voice_tcp.arn
  }
}

# Listener: Browser Agent TCP
resource "aws_lb_listener" "browser_tcp" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = 7863
  protocol          = "TCP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.browser_tcp.arn
  }
}

# Listener: STUN UDP
resource "aws_lb_listener" "stun_udp" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = 3478
  protocol          = "UDP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.stun_udp.arn
  }
}

# Listener: WebRTC Media UDP (single port for demo)
resource "aws_lb_listener" "media_udp" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = 50000
  protocol          = "UDP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.media_udp.arn
  }
}

# Output NLB DNS
output "nlb_dns_name" {
  value       = aws_lb.nlb.dns_name
  description = "NLB DNS name for WebRTC access"
}
