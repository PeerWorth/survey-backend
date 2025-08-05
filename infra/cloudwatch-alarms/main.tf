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
}

data "aws_instances" "app_instances" {
  filter {
    name   = "tag:Environment"
    values = [var.environment]
  }

  filter {
    name   = "instance-state-name"
    values = ["running"]
  }
}

data "aws_db_instances" "rds_instances" {
  filter {
    name   = "engine"
    values = ["mysql"]
  }
}

data "aws_elasticache_replication_group" "redis_cluster" {
  replication_group_id = "${var.project_name}-${var.environment}-valkey"
}

# ALB 데이터 소스 - 조건부 (ALB가 없을 수 있음)
data "aws_lb" "app_alb" {
  count = var.alb_name != "" && length(var.alb_name) <= 32 ? 1 : 0
  name  = var.alb_name
}

# 대안: ALB ARN으로 직접 찾기 (권장)
data "aws_lbs" "all_albs" {
  tags = {
    "elasticbeanstalk:environment-name" = "${var.project_name}-${var.environment}-env"
  }
}

locals {
  # ALB가 존재하면 첫 번째 ALB 사용, 없으면 null
  alb_arn_suffix = length(data.aws_lbs.all_albs.arns) > 0 ? split("/", tolist(data.aws_lbs.all_albs.arns)[0])[1] : ""
}
