# Infrastructure

Infrastructure as Code (IaC) configurations for VPBank Voice Agent.

## Directory Structure

```
infrastructure/
└── terraform/          # Terraform configurations for AWS deployment
    ├── .terraform/     # Terraform plugins and modules (auto-generated)
    └── .terraform.lock.hcl  # Terraform dependency lock file
```

## Terraform

The Terraform configuration deploys the application to AWS ECS Fargate with:

- **VPC**: Virtual Private Cloud with public/private subnets
- **ECS Cluster**: Container orchestration
- **ALB**: Application Load Balancer for traffic routing
- **Security Groups**: Network access control
- **Auto-scaling**: Automatic resource scaling

### Usage

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan infrastructure changes
terraform plan

# Apply infrastructure changes
terraform apply

# Destroy infrastructure
terraform destroy
```

### Required AWS Credentials

Ensure AWS credentials are configured:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

## Notes

- Terraform state files (`.tfstate`) are git-ignored for security
- `.terraform/` directory contains provider plugins (auto-downloaded)
- Always review `terraform plan` output before applying changes
