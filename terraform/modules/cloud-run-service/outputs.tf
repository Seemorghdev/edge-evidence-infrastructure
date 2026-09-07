output "name" {
  description = "Configured Cloud Run service name."
  value       = google_cloud_run_v2_service.this.name
}

output "location" {
  description = "Configured Cloud Run service location."
  value       = google_cloud_run_v2_service.this.location
}

output "deletion_protection" {
  description = "Whether deletion protection is enabled."
  value       = google_cloud_run_v2_service.this.deletion_protection
}
