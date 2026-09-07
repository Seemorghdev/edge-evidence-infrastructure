resource "google_container_cluster" "this" {
  project          = var.project_id
  name             = var.name
  location         = var.region
  enable_autopilot = true
  network          = var.network
  subnetwork       = var.subnetwork

  deletion_protection = true
  resource_labels     = var.resource_labels

  release_channel {
    channel = var.release_channel
  }

  lifecycle {
    prevent_destroy = true
  }
}
