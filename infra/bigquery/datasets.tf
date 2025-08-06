resource "google_bigquery_dataset" "analytics" {
  dataset_id = "analytics_${var.property_id}"
  project    = var.project_id
  location   = var.location
}

resource "google_bigquery_dataset" "datamart" {
  dataset_id = "datamart"
  project    = var.project_id
  location   = var.location
}
