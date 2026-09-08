output "operations_service_account_email" {
  description = "Configured operations service-account email."
  value       = google_service_account.ops.email
}

output "workload_identity_pool_name" {
  description = "Provider-computed Workload Identity Pool resource name."
  value       = google_iam_workload_identity_pool.github.name
}

output "workload_identity_provider_name" {
  description = "Provider-computed GitHub Workload Identity Provider resource name."
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "repository_impersonation_principal" {
  description = "Repository-ID-scoped principalSet granted service-account impersonation."
  value       = google_service_account_iam_member.github_impersonation.member
}

output "trusted_repository" {
  description = "Caller-supplied trusted repository identity."
  value       = var.trusted_repository
}

output "trusted_workflow_ref" {
  description = "Caller-supplied exact trusted workflow ref."
  value       = var.trusted_workflow_ref
}

output "granted_project_roles" {
  description = "Explicit project roles requested by the caller; empty by default."
  value       = sort(tolist(var.project_roles))
}
