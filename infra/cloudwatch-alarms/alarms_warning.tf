# Connection Pool 모니터링을 위한 기본 메트릭 알람들
# 이들은 auto scaling과 직접 연결되지 않고 모니터링 용도

resource "aws_cloudwatch_metric_alarm" "rds_connection_monitoring" {
  alarm_name          = "${var.project_name}-${var.environment}-RDS-ConnectionMonitoring"
  alarm_description   = "RDS 연결 수 모니터링 (참고용)"
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

  alarm_actions = [aws_sns_topic.warning_alerts.arn]
  ok_actions    = [aws_sns_topic.warning_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Warning"
    Service     = "RDS"
    Purpose     = "Monitoring"
  }
}

resource "aws_cloudwatch_metric_alarm" "ec2_cpu_monitoring" {
  for_each            = toset(data.aws_instances.app_instances.ids)
  alarm_name          = "${var.project_name}-${var.environment}-EC2-CPUMonitoring-${each.key}"
  alarm_description   = "EC2 CPU 사용률 모니터링 (참고용)"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
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
    Purpose     = "Monitoring"
  }
}
