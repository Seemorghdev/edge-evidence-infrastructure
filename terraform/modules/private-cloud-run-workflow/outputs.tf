output "workflow" {
  description = "Generic workflow resource identity; no runtime target URI is exposed."
  value = {
    name   = google_workflows_workflow.this.name
    region = google_workflows_workflow.this.region
  }
}

output "workflow_service_account" {
  description = "Workflow service-account identity created by this module."
  value = {
    account_id = google_service_account.workflow.account_id
    email      = google_service_account.workflow.email
  }
}

output "invoker_target_count" {
  description = "Number of caller-supplied Cloud Run service identities receiving roles/run.invoker."
  value       = length(local.cloud_run_targets)
}
