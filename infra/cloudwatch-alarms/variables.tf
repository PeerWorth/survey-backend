variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be either 'dev' or 'prod'."
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "olass"
}

# Alert settings
variable "alert_email" {
  description = "Email address for alert notifications"
  type        = string
}

variable "discord_webhook_url" {
  description = "Discord webhook URL for notifications (optional)"
  type        = string
  default     = ""
}

# Resource identifiers
variable "db_instance_identifier" {
  description = "RDS instance identifier"
  type        = string
}

variable "elasticache_cluster_id" {
  description = "ElastiCache cluster identifier"
  type        = string
  default     = ""
}

variable "alb_name" {
  description = "Application Load Balancer name"
  type        = string
  default     = ""
}

# Alarm thresholds - Critical
variable "rds_connection_threshold" {
  description = "RDS connection count threshold"
  type        = number
  default     = 40
}

variable "rds_storage_threshold_gb" {
  description = "RDS free storage space threshold in GB"
  type        = number
  default     = 1
}

# Alarm thresholds - Warning
variable "rds_cpu_threshold" {
  description = "RDS CPU utilization threshold (%)"
  type        = number
  default     = 75
}

variable "ec2_cpu_threshold" {
  description = "EC2 CPU utilization threshold (%)"
  type        = number
  default     = 80
}

variable "redis_memory_threshold" {
  description = "Redis memory usage threshold (%)"
  type        = number
  default     = 85
}

variable "alb_response_time_threshold" {
  description = "ALB target response time threshold (seconds)"
  type        = number
  default     = 1.0
}

variable "alb_5xx_error_threshold" {
  description = "ALB 5XX error count threshold per 5 minutes"
  type        = number
  default     = 10
}

variable "alb_4xx_error_threshold" {
  description = "ALB 4XX error count threshold per 5 minutes"
  type        = number
  default     = 100
}
