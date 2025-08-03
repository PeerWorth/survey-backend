# S3 Bucket for Elastic Beanstalk deployments
resource "aws_s3_bucket" "eb_deployments" {
  bucket = "${var.project_name}-${var.environment}-eb-deployments"

  tags = {
    Name = "${var.project_name}-${var.environment}-eb-deployments"
  }
}

# S3 Bucket versioning
resource "aws_s3_bucket_versioning" "eb_deployments_versioning" {
  bucket = aws_s3_bucket.eb_deployments.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "eb_deployments_encryption" {
  bucket = aws_s3_bucket.eb_deployments.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "eb_deployments_lifecycle" {
  bucket = aws_s3_bucket.eb_deployments.id

  rule {
    id     = "delete_old_versions"
    status = "Enabled"

    # 필터 추가 (필수)
    filter {
      prefix = ""
    }

    # 30일 후 이전 버전 삭제 (dev는 7일)
    noncurrent_version_expiration {
      noncurrent_days = var.environment == "prod" ? 30 : 7
    }

    # 불완전한 멀티파트 업로드 정리
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

# S3 Bucket public access block
resource "aws_s3_bucket_public_access_block" "eb_deployments_pab" {
  bucket = aws_s3_bucket.eb_deployments.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
