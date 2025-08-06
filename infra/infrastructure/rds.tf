resource "aws_security_group" "rds_sg" {
  name_prefix = "${var.project_name}-${var.environment}-rds-"
  vpc_id      = data.aws_vpc.olass.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = var.environment == "dev" ? [] : [aws_security_group.eb_sg.id]
    cidr_blocks     = var.environment == "dev" ? ["0.0.0.0/0"] : []
    description     = var.environment == "dev" ? "MySQL access from anywhere (dev only)" : "MySQL access from Elastic Beanstalk"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  }
}

# DB Subnet Group
# RDS는 Private 서브넷에만 배치 (보안)
resource "aws_db_subnet_group" "mysql" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = data.aws_subnets.all.ids

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

# RDS Parameter Group
resource "aws_db_parameter_group" "mysql" {
  family = "mysql8.0"
  name   = "${var.project_name}-${var.environment}-mysql-params"

  parameter {
    name  = "slow_query_log"
    value = "1"
  }

  parameter {
    name  = "long_query_time"
    value = "0.2"
  }

  parameter {
    name  = "log_queries_not_using_indexes"
    value = "1"
  }

  parameter {
    name  = "innodb_buffer_pool_size"
    value = "{DBInstanceClassMemory*3/4}"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-mysql-params"
  }
}

# RDS MySQL Instance
resource "aws_db_instance" "mysql" {
  identifier = var.db_instance_identifier

  # Engine settings
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = var.db_instance_class
  allocated_storage    = var.db_allocated_storage
  storage_type         = "gp2"
  storage_encrypted    = var.environment == "prod" ? true : false

  # Database settings
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 3306

  # Network settings
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.mysql.name
  publicly_accessible    = var.environment == "dev" ? true : false

  # Parameter and option groups
  parameter_group_name = aws_db_parameter_group.mysql.name

  # Backup settings
  backup_retention_period = var.environment == "prod" ? 7 : 0
  backup_window          = var.environment == "prod" ? "03:00-04:00" : null
  maintenance_window     = "sun:04:00-sun:05:00"

  # Monitoring and logging (Enhanced Monitoring 비활성화)
  monitoring_interval = 0
  monitoring_role_arn = null
  enabled_cloudwatch_logs_exports      = []
  performance_insights_enabled         = var.environment == "prod" ? true : false
  performance_insights_retention_period = var.environment == "prod" ? 7 : null

  # Deletion protection
  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment == "dev" ? true : false
  final_snapshot_identifier = var.environment == "prod" ? "${var.db_instance_identifier}-final-snapshot" : null

  # Auto minor version upgrade
  auto_minor_version_upgrade = true

  tags = {
    Name = "${var.project_name}-${var.environment}-mysql"
  }
}
