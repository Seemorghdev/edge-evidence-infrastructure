resource "google_compute_global_address" "this" {
  project      = var.project_id
  name         = var.name
  address      = var.desired_address
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
  labels       = var.labels

  lifecycle {
    prevent_destroy = true
  }
}
