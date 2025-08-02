resource "aws_cloudwatch_metric_alarm" "rds_connection_saturation" {
  alarm_name          = "${var.project_name}-${var.environment}-RDS-ConnectionSaturation-Critical"
  alarm_description   = "RDS 연결 수가 임계점에 도달했습니다"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.rds_connection_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = var.db_instance_identifier
  }

  alarm_actions = [aws_sns_topic.critical_alerts.arn]
  ok_actions    = [aws_sns_topic.critical_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Critical"
    Service     = "RDS"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_low_storage" {
  alarm_name          = "${var.project_name}-${var.environment}-RDS-LowStorage-Critical"
  alarm_description   = "RDS 저장 공간이 부족합니다"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.rds_storage_threshold_gb * 1073741824  # GB to bytes
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = var.db_instance_identifier
  }

  alarm_actions = [aws_sns_topic.critical_alerts.arn]
  ok_actions    = [aws_sns_topic.critical_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Critical"
    Service     = "RDS"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_no_healthy_targets" {
  count               = var.alb_name != "" ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-ALB-NoHealthyTargets-Critical"
  alarm_description   = "정상 타겟이 없어 서비스가 중단되었습니다"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  treat_missing_data  = "breaching"

  dimensions = {
    LoadBalancer = try(data.aws_lb.app_alb[0].arn_suffix, "")
  }

  alarm_actions = [aws_sns_topic.critical_alerts.arn]
  ok_actions    = [aws_sns_topic.critical_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Critical"
    Service     = "ALB"
  }
}

resource "aws_cloudwatch_metric_alarm" "ec2_status_check_failed" {
  for_each            = toset(data.aws_instances.app_instances.ids)
  alarm_name          = "${var.project_name}-${var.environment}-EC2-StatusCheckFailed-Critical-${each.key}"
  alarm_description   = "EC2 인스턴스 상태 체크가 실패했습니다"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Maximum"
  threshold           = "0"
  treat_missing_data  = "breaching"

  dimensions = {
    InstanceId = each.key
  }

  alarm_actions = [aws_sns_topic.critical_alerts.arn]
  ok_actions    = [aws_sns_topic.critical_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Critical"
    Service     = "EC2"
    InstanceId  = each.key
  }
}

resource "aws_cloudwatch_metric_alarm" "redis_evictions" {
  count               = var.elasticache_cluster_id != "" ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-Redis-Evictions-Critical"
  alarm_description   = "Redis에서 메모리 부족으로 키가 제거되고 있습니다"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Evictions"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  treat_missing_data  = "notBreaching"

  dimensions = {
    CacheClusterId = var.elasticache_cluster_id
  }

  alarm_actions = [aws_sns_topic.critical_alerts.arn]
  ok_actions    = [aws_sns_topic.critical_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Critical"
    Service     = "ElastiCache"
  }
}
