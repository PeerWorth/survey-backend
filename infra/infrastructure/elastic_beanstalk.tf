# IAM Role for Elastic Beanstalk EC2 instances
resource "aws_iam_role" "eb_ec2_role" {
  name = "${var.project_name}-${var.environment}-eb-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policies for EB EC2 instances
resource "aws_iam_role_policy_attachment" "eb_web_tier" {
  role       = aws_iam_role.eb_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

resource "aws_iam_role_policy_attachment" "eb_worker_tier" {
  role       = aws_iam_role.eb_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"
}

resource "aws_iam_role_policy_attachment" "eb_multicontainer_docker" {
  role       = aws_iam_role.eb_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker"
}

# S3 접근 권한 (배포 아티팩트용)
resource "aws_iam_role_policy" "eb_s3_access" {
  name = "${var.project_name}-${var.environment}-eb-s3-access"
  role = aws_iam_role.eb_ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${aws_s3_bucket.eb_deployments.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.eb_deployments.arn
      }
    ]
  })
}


# IAM Instance Profile
resource "aws_iam_instance_profile" "eb_ec2_profile" {
  name = "${var.project_name}-${var.environment}-eb-ec2-profile"
  role = aws_iam_role.eb_ec2_role.name
}

# IAM Role for Elastic Beanstalk Service
resource "aws_iam_role" "eb_service_role" {
  name = "${var.project_name}-${var.environment}-eb-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "elasticbeanstalk.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eb_service" {
  role       = aws_iam_role.eb_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkService"
}

resource "aws_iam_role_policy_attachment" "eb_health" {
  role       = aws_iam_role.eb_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth"
}

# Security Group for EB Environment
resource "aws_security_group" "eb_sg" {
  name_prefix = "${var.project_name}-${var.environment}-eb-"
  vpc_id      = data.aws_vpc.olass.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # Docker 컨테이너 포트 (내부 통신용)
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    self        = true
    description = "Allow internal traffic on container port"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-eb-sg"
  }
}

# Elastic Beanstalk Application
resource "aws_elastic_beanstalk_application" "app" {
  name        = var.eb_application_name
  description = "${var.project_name} ${var.environment} application"

  appversion_lifecycle {
    service_role          = aws_iam_role.eb_service_role.arn
    max_count             = 5
    delete_source_from_s3 = true
  }
}

# Elastic Beanstalk Environment
resource "aws_elastic_beanstalk_environment" "environment" {
  name                = var.eb_environment_name
  application         = aws_elastic_beanstalk_application.app.name
  solution_stack_name = "64bit Amazon Linux 2023 v4.6.2 running Docker"
  tier                = "WebServer"

  # EC2 인스턴스 설정
  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "InstanceType"
    value     = var.eb_instance_type
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = aws_iam_instance_profile.eb_ec2_profile.name
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "SecurityGroups"
    value     = aws_security_group.eb_sg.id
  }

  # Auto Scaling 설정
  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MinSize"
    value     = var.eb_min_size
  }

  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MaxSize"
    value     = var.eb_max_size
  }

  # 기본 Auto Scaling 정책 사용
  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "MeasureName"
    value     = "CPUUtilization"
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "Unit"
    value     = "Percent"
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "UpperThreshold"
    value     = "80"
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "LowerThreshold"
    value     = "20"
  }

  # Load Balancer 설정
  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "LoadBalancerType"
    value     = "application"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "ServiceRole"
    value     = aws_iam_role.eb_service_role.arn
  }

  # Health Check 설정
  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "Port"
    value     = "8000"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "Protocol"
    value     = "HTTP"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "HealthCheckPath"
    value     = "/health"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "HealthCheckInterval"
    value     = "15"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "HealthCheckTimeout"
    value     = "10"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "HealthyThresholdCount"
    value     = "2"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "UnhealthyThresholdCount"
    value     = "10"
  }

  # Application Load Balancer 리스너 설정 (HTTP)
  setting {
    namespace = "aws:elbv2:listener:default"
    name      = "Protocol"
    value     = "HTTP"
  }

  # HTTPS 리스너 설정 (SSL 인증서가 있을 때만)
  dynamic "setting" {
    for_each = var.ssl_certificate_arn != "" ? [1] : []
    content {
      namespace = "aws:elbv2:listener:443"
      name      = "Protocol"
      value     = "HTTPS"
    }
  }

  dynamic "setting" {
    for_each = var.ssl_certificate_arn != "" ? [1] : []
    content {
      namespace = "aws:elbv2:listener:443"
      name      = "DefaultProcess"
      value     = "default"
    }
  }

  dynamic "setting" {
    for_each = var.ssl_certificate_arn != "" ? [1] : []
    content {
      namespace = "aws:elbv2:listener:443"
      name      = "SSLCertificateArns"
      value     = var.ssl_certificate_arn
    }
  }

  # 모니터링 설정 (Enhanced)
  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "SystemType"
    value     = "enhanced"
  }

  # 알림 이메일 설정
  setting {
    namespace = "aws:elasticbeanstalk:sns:topics"
    name      = "Notification Endpoint"
    value     = var.personal_email
  }

  setting {
    namespace = "aws:elasticbeanstalk:sns:topics"
    name      = "Notification Protocol"
    value     = "email"
  }


  # 환경 변수 설정
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ENVIRONMENT"
    value     = var.environment
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AWS_REGION"
    value     = var.aws_region
  }

  # 데이터베이스 설정
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DEV_MYSQL_URL"
    value     = "mysql+aiomysql://${var.db_username}:${var.db_password}@${aws_db_instance.mysql.endpoint}/${var.db_name}"
  }

  # Redis 설정
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DEV_REDIS_HOST"
    value     = aws_elasticache_replication_group.redis.primary_endpoint_address
  }

  # Rolling deployments 설정
  setting {
    namespace = "aws:elasticbeanstalk:command"
    name      = "DeploymentPolicy"
    value     = "Rolling"
  }

  setting {
    namespace = "aws:elasticbeanstalk:command"
    name      = "BatchSizeType"
    value     = "Percentage"
  }

  setting {
    namespace = "aws:elasticbeanstalk:command"
    name      = "BatchSize"
    value     = "50"
  }

  # Network 설정 (기본 VPC 사용)
  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = data.aws_vpc.olass.id
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = join(",", data.aws_subnets.olass.ids)
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "ELBSubnets"
    value     = join(",", data.aws_subnets.olass.ids)
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-eb-env"
    Environment = var.environment
  }
}
