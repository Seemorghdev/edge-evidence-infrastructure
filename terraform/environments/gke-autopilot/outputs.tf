output "cluster_name" {
  description = "Desired cluster name."
  value       = module.cluster.name
}

output "cluster_location" {
  description = "Desired cluster location."
  value       = module.cluster.location
}

output "autopilot_enabled" {
  description = "Autopilot desired-state invariant."
  value       = module.cluster.autopilot_enabled
}

output "deletion_protection" {
  description = "Deletion-protection desired-state invariant."
  value       = module.cluster.deletion_protection
}
