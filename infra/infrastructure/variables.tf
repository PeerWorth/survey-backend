# 기본 설정
variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "environment" {
  description = "환경 (dev/prod)"
  type        = string
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be either 'dev' or 'prod'."
  }
}

variable "project_name" {
  description = "프로젝트 이름"
  type        = string
  default     = "olass"
}

# Elastic Beanstalk 설정
variable "eb_application_name" {
  description = "Elastic Beanstalk 애플리케이션 이름"
  type        = string
}

variable "eb_environment_name" {
  description = "Elastic Beanstalk 환경 이름"
  type        = string
}

variable "eb_instance_type" {
  description = "EC2 인스턴스 타입"
  type        = string
  default     = "t3.small"
}

variable "eb_min_size" {
  description = "최소 인스턴스 수"
  type        = number
  default     = 1
}

variable "eb_max_size" {
  description = "최대 인스턴스 수"
  type        = number
  default     = 5
}

# RDS 설정
variable "db_instance_identifier" {
  description = "RDS 인스턴스 식별자"
  type        = string
}

variable "db_instance_class" {
  description = "RDS 인스턴스 클래스"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "RDS 스토리지 크기 (GB)"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "데이터베이스 이름"
  type        = string
  default     = "olass"
}

variable "db_username" {
  description = "데이터베이스 마스터 사용자명"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "데이터베이스 비밀번호"
  type        = string
  sensitive   = true
}

# ElastiCache 설정 (Valkey)
variable "redis_cluster_id" {
  description = "Valkey 클러스터 ID"
  type        = string
}

variable "redis_node_type" {
  description = "Valkey 노드 타입"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_port" {
  description = "Valkey 포트"
  type        = number
  default     = 6379
}

# Email
variable "personal_email" {
  description = "알림 이메일 주소"
  type        = string
}

# 네트워킹
variable "vpc_id" {
  description = "사용할 VPC ID"
  type        = string
  default     = ""
}

variable "allowed_cidr_blocks" {
  description = "접근 허용할 CIDR 블록"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# SSL 인증서
variable "ssl_certificate_arn" {
  description = "HTTPS 리스너에 사용할 SSL 인증서 ARN"
  type        = string
  default     = ""
}

# 커스텀 도메인
variable "custom_domain" {
  description = "커스텀 도메인 (예: api.olass.co.kr)"
  type        = string
  default     = ""
}
