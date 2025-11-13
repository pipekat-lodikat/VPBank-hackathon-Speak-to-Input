# DynamoDB Global Secondary Indexes for Optimized Queries
# Improves query performance for common access patterns

resource "aws_dynamodb_table" "vpbank_sessions_optimized" {
  name           = "vpbank-sessions"
  billing_mode   = "PAY_PER_REQUEST"  # Auto-scaling
  hash_key       = "session_id"
  
  # Primary key
  attribute {
    name = "session_id"
    type = "S"
  }
  
  # GSI 1: Query sessions by user
  attribute {
    name = "user_id"
    type = "S"
  }
  
  # GSI 2: Query sessions by timestamp
  attribute {
    name = "created_at"
    type = "N"
  }
  
  # GSI 3: Query sessions by status
  attribute {
    name = "status"
    type = "S"
  }
  
  # Global Secondary Index 1: user_id-created_at-index
  # Use case: Get all sessions for a specific user, sorted by time
  global_secondary_index {
    name               = "user_id-created_at-index"
    hash_key           = "user_id"
    range_key          = "created_at"
    projection_type    = "ALL"
    read_capacity      = 0  # Pay per request
    write_capacity     = 0  # Pay per request
  }
  
  # Global Secondary Index 2: status-created_at-index
  # Use case: Get all sessions by status (active/completed/failed), sorted by time
  global_secondary_index {
    name               = "status-created_at-index"
    hash_key           = "status"
    range_key          = "created_at"
    projection_type    = "ALL"
    read_capacity      = 0
    write_capacity     = 0
  }
  
  # TTL configuration
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }
  
  # Server-side encryption
  server_side_encryption {
    enabled = true
  }
  
  tags = {
    Name        = "vpbank-sessions"
    Environment = var.environment
    Service     = "voice-agent"
    ManagedBy   = "terraform"
  }
}

# Variables
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}

# Outputs
output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.vpbank_sessions_optimized.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.vpbank_sessions_optimized.arn
}

