resource "google_bigquery_table" "page_view_daily" {
  dataset_id           = google_bigquery_dataset.datamart.dataset_id
  table_id             = "page_view_daily"
  project              = var.project_id
  deletion_protection  = false
  schema               = jsonencode([
    { name = "event_date", type = "DATE", mode = "REQUIRED" },
    { name = "page_id", type = "STRING", mode = "NULLABLE" },
    { name = "page_title", type = "STRING", mode = "NULLABLE" },
    { name = "utm_source", type = "STRING", mode = "NULLABLE" },
    { name = "utm_medium", type = "STRING", mode = "NULLABLE" },
    { name = "utm_campagin", type = "STRING", mode = "NULLABLE" },
    { name = "view_count", type = "INTEGER", mode = "NULLABLE" },
    { name = "user_count", type = "INTEGER", mode = "NULLABLE" }
  ])
}

resource "google_bigquery_table" "event_click_daily" {
  dataset_id           = google_bigquery_dataset.datamart.dataset_id
  table_id             = "event_click_daily"
  project              = var.project_id
  deletion_protection  = false
  schema               = jsonencode([
    { name = "event_date", type = "DATE", mode = "REQUIRED" },
    { name = "event_name", type = "STRING", mode = "NULLABLE" },
    { name = "event_label", type = "STRING", mode = "NULLABLE" },
    { name = "utm_source", type = "STRING", mode = "NULLABLE" },
    { name = "utm_medium", type = "STRING", mode = "NULLABLE" },
    { name = "utm_campagin", type = "STRING", mode = "NULLABLE" },
    { name = "click_count", type = "INTEGER", mode = "NULLABLE" },
    { name = "user_count", type = "INTEGER", mode = "NULLABLE" }
  ])
}

resource "google_bigquery_table" "user_profile_daily" {
  dataset_id           = google_bigquery_dataset.datamart.dataset_id
  table_id             = "user_profile_daily"
  project              = var.project_id
  deletion_protection  = false
  schema               = jsonencode([
    { name = "event_date", type = "DATE", mode = "REQUIRED" },
    { name = "user_id", type = "INTEGER", mode = "REQUIRED" },
    { name = "job_group", type = "STRING", mode = "NULLABLE" },
    { name = "job", type = "STRING", mode = "NULLABLE" },
    { name = "experience", type = "INTEGER", mode = "NULLABLE" },
    { name = "age", type = "INTEGER", mode = "NULLABLE" },
    { name = "save_rate", type = "INTEGER", mode = "NULLABLE" },
    { name = "has_car", type = "BOOLEAN", mode = "NULLABLE" },
    { name = "is_monthly_rent", type = "BOOLEAN", mode = "NULLABLE" }
  ])
}
