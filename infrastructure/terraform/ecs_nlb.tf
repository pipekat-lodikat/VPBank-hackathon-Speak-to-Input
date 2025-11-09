# ECS Service with NLB for WebRTC Support

# Update Voice Bot service to use NLB
resource "aws_ecs_service" "voice_bot_nlb" {
  name            = "voice-bot-nlb"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.voice_bot.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
  
  # Register with NLB target groups
  load_balancer {
    target_group_arn = aws_lb_target_group.voice_tcp.arn
    container_name   = "voice-bot"
    container_port   = 7860
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.stun_udp.arn
    container_name   = "voice-bot"
    container_port   = 3478
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.media_udp.arn
    container_name   = "voice-bot"
    container_port   = 50000
  }
  
  depends_on = [
    aws_lb_listener.voice_tcp,
    aws_lb_listener.stun_udp,
    aws_lb_listener.media_udp
  ]
  
  tags = {
    Name = "voice-bot-nlb"
  }
}

# Update Browser Agent service
resource "aws_ecs_service" "browser_agent_nlb" {
  name            = "browser-agent-nlb"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.browser_agent.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.browser_tcp.arn
    container_name   = "browser-agent"
    container_port   = 7863
  }
  
  depends_on = [aws_lb_listener.browser_tcp]
  
  tags = {
    Name = "browser-agent-nlb"
  }
}

# Security Group for ECS Tasks (allow NLB traffic)
resource "aws_security_group_rule" "ecs_nlb_tcp" {
  type              = "ingress"
  from_port         = 7860
  to_port           = 7863
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ecs_tasks.id
  description       = "Allow TCP from NLB"
}

resource "aws_security_group_rule" "ecs_nlb_udp" {
  type              = "ingress"
  from_port         = 3478
  to_port           = 3478
  protocol          = "udp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ecs_tasks.id
  description       = "Allow STUN UDP from NLB"
}

resource "aws_security_group_rule" "ecs_nlb_media_udp" {
  type              = "ingress"
  from_port         = 50000
  to_port           = 50100
  protocol          = "udp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ecs_tasks.id
  description       = "Allow WebRTC media UDP from NLB"
}
