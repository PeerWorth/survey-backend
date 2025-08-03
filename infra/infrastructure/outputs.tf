# Elastic Beanstalk 출력
output "eb_application_name" {
  description = "Elastic Beanstalk 애플리케이션 이름"
  value       = aws_elastic_beanstalk_application.app.name
}

output "eb_environment_name" {
  description = "Elastic Beanstalk 환경 이름 (GitHub Actions에서 사용)"
  value       = var.eb_environment_name
}

# 환경이 GitHub Actions에서 생성되므로 URL과 CNAME은 출력하지 않음
# output "eb_environment_url" {
#   description = "Elastic Beanstalk 환경 URL"
#   value       = aws_elastic_beanstalk_environment.env.endpoint_url
# }

# output "eb_cname" {
#   description = "Elastic Beanstalk CNAME"
#   value       = aws_elastic_beanstalk_environment.env.cname
# }

# RDS 출력
output "rds_endpoint" {
  description = "RDS 엔드포인트"
  value       = aws_db_instance.mysql.endpoint
}

output "rds_port" {
  description = "RDS 포트"
  value       = aws_db_instance.mysql.port
}

output "rds_identifier" {
  description = "RDS 인스턴스 식별자"
  value       = aws_db_instance.mysql.identifier
}

# ElastiCache (Valkey) 출력
output "redis_endpoint" {
  description = "Valkey 엔드포인트"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "redis_port" {
  description = "Valkey 포트"
  value       = aws_elasticache_replication_group.redis.port
}

output "redis_cluster_id" {
  description = "Valkey 클러스터 ID"
  value       = aws_elasticache_replication_group.redis.replication_group_id
}

# 보안 그룹 출력
output "eb_security_group_id" {
  description = "Elastic Beanstalk 보안 그룹 ID"
  value       = aws_security_group.eb_sg.id
}

output "rds_security_group_id" {
  description = "RDS 보안 그룹 ID"
  value       = aws_security_group.rds_sg.id
}

output "redis_security_group_id" {
  description = "Redis 보안 그룹 ID"
  value       = aws_security_group.redis_sg.id
}

# 환경 정보
output "environment" {
  description = "배포된 환경"
  value       = var.environment
}

output "project_name" {
  description = "프로젝트 이름"
  value       = var.project_name
}

# S3 배포 버킷 정보
output "eb_deployment_bucket" {
  description = "Elastic Beanstalk 배포용 S3 버킷"
  value       = aws_s3_bucket.eb_deployments.bucket
}

output "eb_deployment_bucket_arn" {
  description = "Elastic Beanstalk 배포용 S3 버킷 ARN"
  value       = aws_s3_bucket.eb_deployments.arn
}

# CloudWatch 로그 그룹
output "eb_log_group" {
  description = "Elastic Beanstalk CloudWatch 로그 그룹"
  value       = aws_cloudwatch_log_group.eb_logs.name
}

# 네트워크 정보
output "vpc_id" {
  description = "사용 중인 VPC ID"
  value       = data.aws_vpc.olass.id
}

output "public_subnet_ids" {
  description = "Public 서브넷 ID 목록 (ALB용)"
  value       = local.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private 서브넷 ID 목록"
  value       = data.aws_subnets.private.ids
}

output "all_subnet_ids" {
  description = "모든 서브넷 ID 목록 (쉼표로 구분)"
  value       = join(",", data.aws_subnets.all.ids)
}

# IAM 역할 정보
output "eb_service_role_arn" {
  description = "Elastic Beanstalk 서비스 역할 ARN"
  value       = aws_iam_role.eb_service_role.arn
}

output "eb_instance_profile_name" {
  description = "Elastic Beanstalk EC2 인스턴스 프로파일 이름"
  value       = aws_iam_instance_profile.eb_ec2_profile.name
}
