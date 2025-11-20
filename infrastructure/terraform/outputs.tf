output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}

output "ecr_voice_bot_url" {
  description = "ECR repository URL for Voice Bot"
  value       = aws_ecr_repository.voice_bot.repository_url
}

output "ecr_browser_agent_url" {
  description = "ECR repository URL for Browser Agent"
  value       = aws_ecr_repository.browser_agent.repository_url
}

output "ecs_cluster_name" {
  description = "ECS Cluster name"
  value       = aws_ecs_cluster.main.name
}

output "vpc_id" {
  description = "VPC ID"
  value       = data.aws_vpc.default.id
}

output "subnets" {
  description = "Subnet IDs"
  value       = data.aws_subnets.default.ids
}

output "frontend_s3_bucket" {
  description = "Frontend S3 bucket name"
  value       = aws_s3_bucket.frontend.id
}

output "frontend_s3_website_endpoint" {
  description = "Frontend S3 website endpoint"
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.frontend.id
}
