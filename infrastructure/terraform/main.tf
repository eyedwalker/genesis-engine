# Hive BizOS Factory - AWS Free Tier Infrastructure
# Optimized for minimal cost using Free Tier services

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "hive-bizos-factory"
      Environment = var.environment
      ManagedBy   = "terraform"
      FreeTier    = "true"
    }
  }
}

# ============================================================================
# Variables
# ============================================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "free-tier"
}

variable "tenant_id" {
  description = "Tenant identifier for multi-tenancy"
  type        = string
  default     = "default"
}

variable "db_password" {
  description = "PostgreSQL database password"
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key for Claude"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key for GPT-4"
  type        = string
  sensitive   = true
}

# ============================================================================
# VPC & Networking (Free Tier)
# ============================================================================

resource "aws_vpc" "factory" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "hive-factory-vpc"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.factory.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "hive-factory-public-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.factory.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "hive-factory-public-b"
  }
}

resource "aws_internet_gateway" "factory" {
  vpc_id = aws_vpc.factory.id
  
  tags = {
    Name = "hive-factory-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.factory.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.factory.id
  }
  
  tags = {
    Name = "hive-factory-public-rt"
  }
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

# ============================================================================
# Security Groups
# ============================================================================

resource "aws_security_group" "rds" {
  name        = "hive-factory-rds"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.factory.id
  
  ingress {
    description = "PostgreSQL from Lambda"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.factory.cidr_block]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "hive-factory-rds-sg"
  }
}

# ============================================================================
# RDS PostgreSQL (FREE TIER - db.t3.micro, Single-AZ)
# ============================================================================

resource "aws_db_subnet_group" "factory" {
  name       = "hive-factory-db-subnet"
  subnet_ids = [aws_subnet.public_a.id, aws_subnet.public_b.id]
  
  tags = {
    Name = "hive-factory-db-subnet-group"
  }
}

resource "aws_db_instance" "factory" {
  identifier     = "hive-factory-${var.environment}"
  engine         = "postgres"
  engine_version = "15.4"
  
  # FREE TIER: db.t3.micro
  instance_class = "db.t3.micro"
  
  # FREE TIER: 20GB storage
  allocated_storage     = 20
  max_allocated_storage = 20  # Prevent auto-scaling beyond free tier
  storage_type          = "gp2"  # Required for free tier
  storage_encrypted     = true
  
  # Database configuration
  db_name  = "hive_bizos"
  username = "hive_admin"
  password = var.db_password
  port     = 5432
  
  # FREE TIER: Single-AZ (Multi-AZ costs extra)
  multi_az               = false
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.factory.name
  
  # Backups (free within limits)
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  
  # Performance insights (not free, disabled)
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  # Deletion protection (disable for testing)
  deletion_protection = false
  skip_final_snapshot = true
  
  tags = {
    Name = "hive-factory-db"
  }
}

# ============================================================================
# DynamoDB for Caching (FREE TIER - 25GB forever!)
# ============================================================================

resource "aws_dynamodb_table" "factory_cache" {
  name         = "factory-cache-${var.tenant_id}"
  billing_mode = "PAY_PER_REQUEST"  # Free tier friendly
  hash_key     = "key"
  
  attribute {
    name = "key"
    type = "S"
  }
  
  # TTL for automatic expiration
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  tags = {
    Name = "hive-factory-cache"
  }
}

# ============================================================================
# S3 Bucket for Storage (FREE TIER - 5GB)
# ============================================================================

resource "aws_s3_bucket" "factory" {
  bucket = "hive-factory-${var.tenant_id}-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name = "hive-factory-storage"
  }
}

resource "aws_s3_bucket_versioning" "factory" {
  bucket = aws_s3_bucket.factory.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "factory" {
  bucket = aws_s3_bucket.factory.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ============================================================================
# Lambda Execution Role
# ============================================================================

resource "aws_iam_role" "lambda_execution" {
  name = "hive-factory-lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_access" {
  name = "lambda-factory-access"
  role = aws_iam_role.lambda_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.factory_cache.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.factory.arn,
          "${aws_s3_bucket.factory.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.api_keys.arn
      }
    ]
  })
}

# ============================================================================
# Secrets Manager for API Keys
# ============================================================================

resource "aws_secretsmanager_secret" "api_keys" {
  name = "hive-factory-api-keys-${var.environment}"
  
  recovery_window_in_days = 0  # Immediate deletion for testing
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  
  secret_string = jsonencode({
    ANTHROPIC_API_KEY = var.anthropic_api_key
    OPENAI_API_KEY    = var.openai_api_key
    DB_PASSWORD       = var.db_password
  })
}

# ============================================================================
# Lambda Function Placeholder
# (Actual deployment happens via Serverless Framework)
# ============================================================================

# Lambda functions will be deployed separately using Serverless Framework
# This Terraform creates the infrastructure they'll use

# ============================================================================
# Outputs
# ============================================================================

data "aws_caller_identity" "current" {}

output "database_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.factory.endpoint
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.factory.db_name
}

output "dynamodb_table" {
  description = "DynamoDB cache table name"
  value       = aws_dynamodb_table.factory_cache.name
}

output "s3_bucket" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.factory.bucket
}

output "lambda_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_execution.arn
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.factory.id
}

output "subnet_ids" {
  description = "Subnet IDs for Lambda"
  value       = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}

output "secrets_arn" {
  description = "Secrets Manager ARN"
  value       = aws_secretsmanager_secret.api_keys.arn
}

# ============================================================================
# Cost Estimate
# ============================================================================

# RDS db.t3.micro (Single-AZ):  750 hours/month FREE (12 months)
# RDS Storage 20GB:              20GB FREE (12 months)
# DynamoDB:                      25GB + 200M requests FREE (forever)
# S3:                            5GB FREE (12 months)
# Lambda:                        1M requests + 400K GB-sec FREE (forever)
# Secrets Manager:               $0.40/secret/month ($0.40)
#
# Total first 12 months: ~$0.40/month (infrastructure only)
# After 12 months: ~$14/month (RDS db.t3.micro ~$13 + Secrets $0.40)
# Plus AI API costs: ~$0.22 per feature generated
