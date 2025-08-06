output "sns_topic_critical_arn" {
  description = "ARN of the critical alerts SNS topic"
  value       = aws_sns_topic.critical_alerts.arn
}

output "sns_topic_warning_arn" {
  description = "ARN of the warning alerts SNS topic"
  value       = aws_sns_topic.warning_alerts.arn
}

output "critical_alarms" {
  description = "List of critical alarm names (Auto Scaling triggers)"
  value = [
    aws_cloudwatch_metric_alarm.ec2_connection_pool_error.alarm_name,
    aws_cloudwatch_metric_alarm.ec2_connection_pool_ok.alarm_name
  ]
}

output "warning_alarms" {
  description = "List of warning alarm names (Monitoring only)"
  value = [
    aws_cloudwatch_metric_alarm.rds_connection_monitoring.alarm_name,
    [for alarm in aws_cloudwatch_metric_alarm.ec2_cpu_monitoring : alarm.alarm_name]
  ]
}

output "total_alarm_count" {
  description = "Total number of alarms created"
  value = (
    2 + # connection pool alarms (scale up/down)
    1 + # rds connection monitoring
    length(data.aws_instances.app_instances.ids) # ec2 cpu monitoring
  )
}
