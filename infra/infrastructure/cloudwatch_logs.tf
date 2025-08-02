# CloudWatch Log Group for Elastic Beanstalk
resource "aws_cloudwatch_log_group" "eb_logs" {
  name              = "/aws/elasticbeanstalk/${var.eb_environment_name}"
  retention_in_days = var.environment == "prod" ? 30 : 7

  tags = {
    Name = "${var.project_name}-${var.environment}-eb-logs"
  }
}

# CloudWatch Log Group for Docker containers
resource "aws_cloudwatch_log_group" "eb_docker_logs" {
  name              = "/aws/elasticbeanstalk/${var.eb_environment_name}/var/log/docker"
  retention_in_days = var.environment == "prod" ? 30 : 7

  tags = {
    Name = "${var.project_name}-${var.environment}-eb-docker-logs"
  }
}
