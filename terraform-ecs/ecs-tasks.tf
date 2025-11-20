# Target Groups for ALB
resource "aws_lb_target_group" "voice_bot" {
  name        = "${var.project_name}-voice-bot-tg"
  port        = 7860
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
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
}

resource "aws_lb_target_group" "browser_agent" {
  name        = "${var.project_name}-browser-agent-tg"
  port        = 7863
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
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
}

# ALB Listeners
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.voice_bot.arn
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
    
    portMappings = [{
      containerPort = 7860
      protocol      = "tcp"
    }]

    environment = [
      { name = "PORT", value = "7860" },
      { name = "AWS_REGION", value = var.aws_region }
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
    
    command = ["python", "main_browser_service.py"]
    
    portMappings = [{
      containerPort = 7863
      protocol      = "tcp"
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
  }])
}

# ECS Services
resource "aws_ecs_service" "voice_bot" {
  name            = "voice-bot"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.voice_bot.arn
  desired_count   = var.voice_bot_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.voice_bot.arn
    container_name   = "voice-bot"
    container_port   = 7860
  }

  depends_on = [aws_lb_listener.http]
}

resource "aws_ecs_service" "browser_agent" {
  name            = "browser-agent"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.browser_agent.arn
  desired_count   = var.browser_agent_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.browser_agent.arn
    container_name   = "browser-agent"
    container_port   = 7863
  }

  depends_on = [aws_lb_listener.http]
}
