module "private_workflow" {
  source = "../../modules/private-cloud-run-workflow"

  project_id                            = var.project_id
  region                                = var.region
  workflow_name                         = var.workflow_name
  workflow_description                  = var.workflow_description
  workflow_service_account_id           = var.workflow_service_account_id
  workflow_service_account_display_name = var.workflow_service_account_display_name
  workflow_service_account_description  = var.workflow_service_account_description
  workflow_source_contents              = var.workflow_source_contents
  cloud_run_targets                     = var.cloud_run_targets
}
