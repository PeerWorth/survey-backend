resource "aws_cloudwatch_metric_alarm" "alb_high_5xx_errors" {
  count               = var.alb_name != "" ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-ALB-High5xxErrors-Warning"
  alarm_description   = "5XX 에러가 증가하고 있습니다"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.alb_5xx_error_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = try(data.aws_lb.app_alb[0].arn_suffix, "")
  }

  alarm_actions = [aws_sns_topic.warning_alerts.arn]
  ok_actions    = [aws_sns_topic.warning_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Warning"
    Service     = "ALB"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_high_cpu" {
  alarm_name          = "${var.project_name}-${var.environment}-RDS-HighCPU-Warning"
  alarm_description   = "RDS CPU 사용률이 높습니다"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.rds_cpu_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = var.db_instance_identifier
  }

  alarm_actions = [aws_sns_topic.warning_alerts.arn]
  ok_actions    = [aws_sns_topic.warning_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Warning"
    Service     = "RDS"
  }
}

resource "aws_cloudwatch_metric_alarm" "redis_high_memory" {
  count               = var.elasticache_cluster_id != "" ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-Redis-HighMemory-Warning"
  alarm_description   = "Redis 메모리 사용률이 높습니다"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = var.redis_memory_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    CacheClusterId = var.elasticache_cluster_id
  }

  alarm_actions = [aws_sns_topic.warning_alerts.arn]
  ok_actions    = [aws_sns_topic.warning_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Warning"
    Service     = "ElastiCache"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_slow_response" {
  count               = var.alb_name != "" ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-ALB-SlowResponse-Warning"
  alarm_description   = "응답 시간이 지연되고 있습니다"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = var.alb_response_time_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = try(data.aws_lb.app_alb[0].arn_suffix, "")
  }

  alarm_actions = [aws_sns_topic.warning_alerts.arn]
  ok_actions    = [aws_sns_topic.warning_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Warning"
    Service     = "ALB"
  }
}

resource "aws_cloudwatch_metric_alarm" "ec2_high_cpu" {
  for_each            = toset(data.aws_instances.app_instances.ids)
  alarm_name          = "${var.project_name}-${var.environment}-EC2-HighCPU-Warning-${each.key}"
  alarm_description   = "EC2 CPU 사용률이 높습니다"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = var.ec2_cpu_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    InstanceId = each.key
  }

  alarm_actions = [aws_sns_topic.warning_alerts.arn]
  ok_actions    = [aws_sns_topic.warning_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Warning"
    Service     = "EC2"
    InstanceId  = each.key
  }
}
