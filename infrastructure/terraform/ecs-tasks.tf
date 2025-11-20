# ALB Target Groups
resource "aws_lb_target_group" "voice_bot" {
  name        = "vpbank-va-voice-tg"
  port        = 7860
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = {
    Name = "${var.project_name}-voice-bot-tg"
  }
}

resource "aws_lb_target_group" "browser_agent" {
  name        = "vpbank-va-browser-tg"
  port        = 7863
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/api/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = {
    Name = "${var.project_name}-browser-agent-tg"
  }
}

# ALB Listener Rules
resource "aws_lb_listener_rule" "browser_agent" {
  listener_arn = aws_lb_listener.http.arn
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
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "voice_bot" {
  family                   = "${var.project_name}-voice-bot"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "voice-bot"
    image = "${aws_ecr_repository.voice_bot.repository_url}:latest"
    
    essential = true

    portMappings = [{
      containerPort = 7860
      protocol      = "tcp"
      name          = "voice-bot-7860-tcp"
    }]

    environment = [
      { name = "PORT", value = "7860" },
      { name = "AWS_REGION", value = var.aws_region },
      { name = "BROWSER_SERVICE_URL", value = "http://${aws_lb.main.dns_name}" }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.voice_bot.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:7860/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = {
    Name = "${var.project_name}-voice-bot-task"
  }
}

resource "aws_ecs_task_definition" "browser_agent" {
  family                   = "${var.project_name}-browser-agent"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "browser-agent"
    image = "${aws_ecr_repository.browser_agent.repository_url}:latest"
    
    essential = true
    
    command = ["python", "main_browser_service.py"]
    
    portMappings = [{
      containerPort = 7863
      protocol      = "tcp"
      name          = "browser-agent-7863-tcp"
    }]

    environment = [
      { name = "PORT", value = "7863" },
      { name = "AWS_REGION", value = var.aws_region }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.browser_agent.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:7863/api/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = {
    Name = "${var.project_name}-browser-agent-task"
  }
}

# ECS Services
resource "aws_ecs_service" "voice_bot" {
  name            = "voice-bot"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.voice_bot.arn
  desired_count   = var.voice_bot_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.voice_bot.arn
    container_name   = "voice-bot"
    container_port   = 7860
  }

  enable_execute_command = true

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  depends_on = [
    aws_lb_listener.http,
    aws_iam_role_policy.ecs_task_policy
  ]

  tags = {
    Name = "${var.project_name}-voice-bot-service"
  }
}

resource "aws_ecs_service" "browser_agent" {
  name            = "browser-agent"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.browser_agent.arn
  desired_count   = var.browser_agent_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.browser_agent.arn
    container_name   = "browser-agent"
    container_port   = 7863
  }

  enable_execute_command = true

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  depends_on = [
    aws_lb_listener.http,
    aws_iam_role_policy.ecs_task_policy
  ]

  tags = {
    Name = "${var.project_name}-browser-agent-service"
  }
}

# Auto Scaling
resource "aws_appautoscaling_target" "voice_bot" {
  max_capacity       = 5
  min_capacity       = var.voice_bot_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.voice_bot.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "voice_bot_cpu" {
  name               = "${var.project_name}-voice-bot-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.voice_bot.resource_id
  scalable_dimension = aws_appautoscaling_target.voice_bot.scalable_dimension
  service_namespace  = aws_appautoscaling_target.voice_bot.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
