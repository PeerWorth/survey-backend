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
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

data "aws_vpc" "olass" {
  id = var.vpc_id
}

# Public 서브넷 (ALB, NAT Gateway용)
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.olass.id]
  }
  filter {
    name   = "tag:Name"
    values = ["olass-public-subnet-*"]
  }
}

# Private 서브넷 (RDS, ElastiCache, EC2 인스턴스용)
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.olass.id]
  }
  filter {
    name   = "tag:Name"
    values = ["olass-private-subnet-*"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}
