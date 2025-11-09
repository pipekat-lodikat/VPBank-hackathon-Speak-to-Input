#!/bin/bash
set -e

PROJECT_NAME="vpbank-voice-agent"
AWS_REGION="us-east-1"

echo "🚀 VPBank Voice Agent - ECS Fargate Deployment"
echo "==============================================="
echo ""

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo ""

# Check prerequisites
echo "▶ Checking prerequisites..."
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm required"; exit 1; }

echo "✅ Prerequisites OK"
echo ""

cd /home/ubuntu/speak-to-input

# Step 1: Build Docker images
echo "▶ Step 1/5: Building Docker images..."
docker build -t $PROJECT_NAME/voice-bot:latest -f Dockerfile .
docker build -t $PROJECT_NAME/browser-agent:latest -f Dockerfile .
echo "✅ Docker images built"
echo ""

# Step 2: Create Terraform files
echo "▶ Step 2/5: Creating Terraform configuration..."
mkdir -p terraform-ecs
cd terraform-ecs

# Note: main.tf already created, now create remaining files

# Create ECS tasks configuration
cat > ecs-tasks.tf << 'EOFTF'
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
EOFTF

echo "✅ Terraform configuration created"
echo ""

# Step 3: Initialize Terraform
echo "▶ Step 3/5: Initializing Terraform..."
terraform init
terraform plan -out=tfplan

echo ""
echo "⚠️  COST WARNING: ~\$213/month"
echo ""
read -p "Continue with deployment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Step 4: Deploy infrastructure
echo ""
echo "▶ Step 4/5: Deploying infrastructure (this may take 10-15 minutes)..."
terraform apply tfplan

ECR_VOICE_BOT=$(terraform output -raw ecr_voice_bot_url)
ECR_BROWSER_AGENT=$(terraform output -raw ecr_browser_agent_url)
ALB_DNS=$(terraform output -raw alb_dns_name)

echo "✅ Infrastructure deployed"
echo ""

# Step 5: Push Docker images
echo "▶ Step 5/5: Pushing Docker images to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

docker tag $PROJECT_NAME/voice-bot:latest $ECR_VOICE_BOT:latest
docker push $ECR_VOICE_BOT:latest

docker tag $PROJECT_NAME/browser-agent:latest $ECR_BROWSER_AGENT:latest
docker push $ECR_BROWSER_AGENT:latest

echo "✅ Docker images pushed"
echo ""

# Summary
echo "========================================"
echo "🎉 Deployment Complete!"
echo "========================================"
echo ""
echo "📍 Application URL: http://$ALB_DNS"
echo ""
echo "🔧 Useful commands:"
echo "   aws logs tail /ecs/$PROJECT_NAME/voice-bot --follow"
echo "   aws ecs list-services --cluster $PROJECT_NAME-cluster"
echo ""
echo "💰 Monthly cost: ~\$213"
echo ""
