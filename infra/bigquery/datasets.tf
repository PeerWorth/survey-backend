resource "google_bigquery_dataset" "datamart" {
  dataset_id = "datamart"
  project    = var.project_id
  location   = var.location
}
