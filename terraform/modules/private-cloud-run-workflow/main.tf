locals {
  cloud_run_targets = {
    for key, target in var.cloud_run_targets : key => {
      name     = target.name
      location = coalesce(target.location, var.region)
    }
  }
}

resource "google_service_account" "workflow" {
  project      = var.project_id
  account_id   = var.workflow_service_account_id
  display_name = var.workflow_service_account_display_name
  description  = var.workflow_service_account_description
}

resource "google_workflows_workflow" "this" {
  project                 = var.project_id
  region                  = var.region
  name                    = var.workflow_name
  description             = var.workflow_description
  service_account         = google_service_account.workflow.email
  call_log_level          = "LOG_NONE"
  execution_history_level = "EXECUTION_HISTORY_BASIC"
  deletion_protection     = false
  source_contents         = var.workflow_source_contents
}

resource "google_cloud_run_v2_service_iam_member" "workflow_invoker" {
  for_each = local.cloud_run_targets

  project  = var.project_id
  location = each.value.location
  name     = each.value.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.workflow.email}"
}
