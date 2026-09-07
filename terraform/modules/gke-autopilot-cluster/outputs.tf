output "name" {
  description = "Configured cluster name."
  value       = google_container_cluster.this.name
}

output "location" {
  description = "Configured cluster location."
  value       = google_container_cluster.this.location
}

output "autopilot_enabled" {
  description = "Whether Autopilot is enabled on the cluster."
  value       = google_container_cluster.this.enable_autopilot
}

output "deletion_protection" {
  description = "Whether deletion protection is enabled."
  value       = google_container_cluster.this.deletion_protection
}
