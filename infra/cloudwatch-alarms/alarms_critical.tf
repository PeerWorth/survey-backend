# EC2 Connection Pool Error 알람 - Auto Scaling 트리거용
resource "aws_cloudwatch_metric_alarm" "ec2_connection_pool_error" {
  alarm_name          = "${var.project_name}-${var.environment}-EC2-ConnectionPoolError-ScaleUp"
  alarm_description   = "EC2 connection pool 에러로 인한 auto scaling 트리거"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"  # 2번 연속 임계값 초과시
  metric_name         = "HTTPCode_Target_5XX_Count"  # 5XX 에러를 connection pool 에러 지표로 사용
  namespace           = "AWS/ApplicationELB"
  period              = "300"  # 5분
  statistic           = "Sum"
  threshold           = "10"   # 5분간 5XX 에러 10개 초과시 scale up
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = local.alb_arn_suffix
  }

  # Auto Scaling을 위한 알람이므로 SNS는 선택사항
  alarm_actions = [aws_sns_topic.critical_alerts.arn]
  ok_actions    = [aws_sns_topic.critical_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Critical"
    Service     = "AutoScaling"
    Purpose     = "ScaleUp"
  }
}

# Scale Down을 위한 알람 (5XX 에러가 낮을 때)
resource "aws_cloudwatch_metric_alarm" "ec2_connection_pool_ok" {
  alarm_name          = "${var.project_name}-${var.environment}-EC2-ConnectionPoolOK-ScaleDown"
  alarm_description   = "Connection pool 안정화로 인한 scale down 트리거"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "5"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "2"   # 5분간 5XX 에러 2개 미만시 scale down 고려
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = local.alb_arn_suffix
  }

  alarm_actions = [aws_sns_topic.critical_alerts.arn]
  ok_actions    = [aws_sns_topic.critical_alerts.arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Priority    = "Info"
    Service     = "AutoScaling"
    Purpose     = "ScaleDown"
  }
}
