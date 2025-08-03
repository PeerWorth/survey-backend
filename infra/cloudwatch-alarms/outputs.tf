output "sns_topic_critical_arn" {
  description = "ARN of the critical alerts SNS topic"
  value       = aws_sns_topic.critical_alerts.arn
}

output "sns_topic_warning_arn" {
  description = "ARN of the warning alerts SNS topic"
  value       = aws_sns_topic.warning_alerts.arn
}

output "critical_alarms" {
  description = "List of critical alarm names"
  value = [
    aws_cloudwatch_metric_alarm.rds_connection_saturation.alarm_name,
    aws_cloudwatch_metric_alarm.rds_low_storage.alarm_name,
    try(aws_cloudwatch_metric_alarm.alb_no_healthy_targets[0].alarm_name, ""),
    try(aws_cloudwatch_metric_alarm.redis_evictions[0].alarm_name, ""),
    [for alarm in aws_cloudwatch_metric_alarm.ec2_status_check_failed : alarm.alarm_name]
  ]
}

output "warning_alarms" {
  description = "List of warning alarm names"
  value = [
    try(aws_cloudwatch_metric_alarm.alb_high_5xx_errors[0].alarm_name, ""),
    aws_cloudwatch_metric_alarm.rds_high_cpu.alarm_name,
    try(aws_cloudwatch_metric_alarm.redis_high_memory[0].alarm_name, ""),
    try(aws_cloudwatch_metric_alarm.alb_slow_response[0].alarm_name, ""),
    [for alarm in aws_cloudwatch_metric_alarm.ec2_high_cpu : alarm.alarm_name]
  ]
}

output "total_alarm_count" {
  description = "Total number of alarms created"
  value = (
    1 + # rds_connection_saturation
    1 + # rds_low_storage
    (var.alb_name != "" ? 1 : 0) + # alb_no_healthy_targets
    (var.elasticache_cluster_id != "" ? 1 : 0) + # redis_evictions
    length(data.aws_instances.app_instances.ids) + # ec2_status_check_failed

    (var.alb_name != "" ? 1 : 0) + # alb_high_5xx_errors
    1 + # rds_high_cpu
    (var.elasticache_cluster_id != "" ? 1 : 0) + # redis_high_memory
    (var.alb_name != "" ? 1 : 0) + # alb_slow_response
    length(data.aws_instances.app_instances.ids) # ec2_high_cpu
  )
}
