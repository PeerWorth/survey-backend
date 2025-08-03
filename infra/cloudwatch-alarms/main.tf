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

data "aws_elasticache_clusters" "redis_clusters" {

}

data "aws_lb" "app_alb" {
  count = var.alb_name != "" ? 1 : 0
  name  = var.alb_name
}
