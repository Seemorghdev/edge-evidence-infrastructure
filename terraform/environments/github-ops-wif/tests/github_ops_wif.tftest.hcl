mock_provider "google" {}

variables {
  project_id                   = "example-wif-12345"
  service_account_id           = "example-ops"
  service_account_display_name = "Example GitHub operations"
  pool_id                      = "example-github-pool"
  provider_id                  = "example-github-provider"
  trusted_repository           = "example-org/example-repo"
  trusted_repository_id        = "123456789"
  trusted_repository_owner_id  = "987654321"
  trusted_workflow_ref         = "example-org/example-repo/.github/workflows/ops.yml@refs/heads/review"
  trusted_ref                  = "refs/heads/review"
  trusted_event                = "workflow_dispatch"
  trusted_visibility           = "private"
}

run "plans_sanitized_wif_provisioning" {
  command = plan
}
