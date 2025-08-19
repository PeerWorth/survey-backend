resource "google_bigquery_table" "user_journey_daily" {
  dataset_id           = google_bigquery_dataset.datamart.dataset_id
  table_id             = "user_journey_daily"
  project              = var.project_id
  deletion_protection  = false

  schema               = jsonencode([
    # 기본 필드
    { name = "event_date", type = "DATE", mode = "REQUIRED" },
    { name = "user_pseudo_id", type = "STRING", mode = "REQUIRED" },

    # 페이지뷰 카운트
    { name = "intro_page", type = "INTEGER", mode = "NULLABLE" },
    { name = "salary_job", type = "INTEGER", mode = "NULLABLE" },
    { name = "salary_experience", type = "INTEGER", mode = "NULLABLE" },
    { name = "salary_salary", type = "INTEGER", mode = "NULLABLE" },
    { name = "profile_age", type = "INTEGER", mode = "NULLABLE" },
    { name = "profile_invest_ratio", type = "INTEGER", mode = "NULLABLE" },
    { name = "profile_car", type = "INTEGER", mode = "NULLABLE" },
    { name = "profile_rent", type = "INTEGER", mode = "NULLABLE" },

    # 핵심 액션 카운트
    { name = "terms_agreed", type = "INTEGER", mode = "NULLABLE" },
    { name = "share_button", type = "INTEGER", mode = "NULLABLE" },

    # UTM 파라미터 (첫 세션 기준)
    { name = "utm_source", type = "STRING", mode = "NULLABLE" },
    { name = "utm_medium", type = "STRING", mode = "NULLABLE" },
    { name = "utm_campaign", type = "STRING", mode = "NULLABLE" },
    { name = "utm_content", type = "STRING", mode = "NULLABLE" },
    { name = "utm_term", type = "STRING", mode = "NULLABLE" }
  ])
}

resource "google_bigquery_table" "user_profile_daily" {
  dataset_id           = google_bigquery_dataset.datamart.dataset_id
  table_id             = "user_profile_daily"
  project              = var.project_id
  deletion_protection  = false
  schema               = jsonencode([
    { name = "event_date", type = "DATE", mode = "REQUIRED" },
    { name = "user_id", type = "INTEGER", mode = "NULLABLE" },
    { name = "job_group", type = "STRING", mode = "NULLABLE" },
    { name = "job", type = "STRING", mode = "NULLABLE" },
    { name = "email", type = "STRING", mode = "NULLABLE" },
    { name = "salary", type = "INTEGER", mode = "NULLABLE" },
    { name = "experience", type = "INTEGER", mode = "NULLABLE" },
    { name = "age", type = "INTEGER", mode = "NULLABLE" },
    { name = "save_rate", type = "INTEGER", mode = "NULLABLE" },
    { name = "has_car", type = "BOOLEAN", mode = "NULLABLE" },
    { name = "is_monthly_rent", type = "BOOLEAN", mode = "NULLABLE" }
  ])
}
