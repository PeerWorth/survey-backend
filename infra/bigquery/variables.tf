variable "project_id" {
  type        = string
  description = "GCP 프로젝트 ID"
}

variable "property_id" {
  type        = string
  description = "GA4 property ID (예: 12345678)"
}

variable "location" {
  type        = string
  default     = "asia-northeast3"
  description = "BigQuery location (리전과 일치해야 함)"
}

variable "region" {
  type        = string
  default     = "asia-northeast3"
  description = "GCP 리전 (예: asia-northeast3)"
}
