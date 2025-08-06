resource "aws_security_group" "redis_sg" {
  name_prefix = "${var.project_name}-${var.environment}-redis-"
  vpc_id      = data.aws_vpc.olass.id

  ingress {
    from_port       = var.redis_port
    to_port         = var.redis_port
    protocol        = "tcp"
    security_groups = [aws_security_group.eb_sg.id]
    description     = "Redis access from Elastic Beanstalk"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  }
}

# ElastiCache Subnet Group
# ElastiCache는 Private 서브넷에만 배치 (보안)
resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = data.aws_subnets.all.ids

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-subnet-group"
  }
}

# ElastiCache Parameter Group
resource "aws_elasticache_parameter_group" "redis" {
  family = "valkey7"
  name   = "${var.project_name}-${var.environment}-valkey-params"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-params"
  }
}

# ElastiCache Valkey Replication Group
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = var.redis_cluster_id
  description                = "Valkey cluster for ${var.project_name}-${var.environment}"

  engine               = "valkey"
  engine_version       = "7.2"
  node_type            = var.redis_node_type
  port                 = var.redis_port
  parameter_group_name = aws_elasticache_parameter_group.redis.name

  # Single node configuration (no replication for cost optimization)
  num_cache_clusters         = 1
  automatic_failover_enabled = false
  multi_az_enabled          = false

  # Network settings
  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis_sg.id]

  # Maintenance and backup
  maintenance_window       = "sun:05:00-sun:06:00"
  snapshot_retention_limit = var.environment == "prod" ? 5 : 0
  snapshot_window         = var.environment == "prod" ? "06:00-07:00" : null


  tags = {
    Name = "${var.project_name}-${var.environment}-valkey"
  }
}
