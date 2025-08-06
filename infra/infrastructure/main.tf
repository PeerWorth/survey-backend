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

# EB Environment에서 사용할 서브넷 (public 서브넷만)
data "aws_subnets" "olass" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.olass.id]
  }
  filter {
    name   = "tag:Name"
    values = ["ollass-public-subnet-*"]
  }
}

# 모든 서브넷 (일시적으로 사용)
data "aws_subnets" "all" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.olass.id]
  }
}

# Public 서브넷 (ALB, NAT Gateway용) - 서로 다른 AZ만
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.olass.id]
  }
  filter {
    name   = "tag:Name"
    values = ["*public*"]
  }
}

# 서로 다른 AZ의 서브넷만 선택
locals {
  # 첫 번째와 두 번째 AZ의 서브넷만 사용 (ALB 요구사항)
  public_subnet_ids = slice(data.aws_subnets.public.ids, 0, min(2, length(data.aws_subnets.public.ids)))
}

# Private 서브넷 (RDS, ElastiCache, EC2 인스턴스용)
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.olass.id]
  }
  filter {
    name   = "tag:Name"
    values = ["*private*"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# 최신 Docker 플랫폼 자동 탐지
data "aws_elastic_beanstalk_solution_stack" "docker" {
  most_recent = true
  name_regex  = "^64bit Amazon Linux 2 .* running Docker$"
}
