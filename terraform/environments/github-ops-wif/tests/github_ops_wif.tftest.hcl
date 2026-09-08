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

run "plans_minimal_wif_provisioning" {
  command = plan

  assert {
    condition     = length(google_project_service.bootstrap) == 5
    error_message = "The WIF environment must enable exactly five reviewed bootstrap APIs."
  }

  assert {
    condition = (
      google_service_account.ops.account_id == "example-ops" &&
      google_iam_workload_identity_pool.github.workload_identity_pool_id == "example-github-pool" &&
      google_iam_workload_identity_pool_provider.github.workload_identity_pool_provider_id == "example-github-provider"
    )
    error_message = "Generic service-account, pool, and provider IDs must flow through the desired state."
  }

  assert {
    condition = alltrue([
      strcontains(google_iam_workload_identity_pool_provider.github.attribute_condition, "assertion.repository == 'example-org/example-repo'"),
      strcontains(google_iam_workload_identity_pool_provider.github.attribute_condition, "assertion.repository_id == '123456789'"),
      strcontains(google_iam_workload_identity_pool_provider.github.attribute_condition, "assertion.repository_owner_id == '987654321'"),
      strcontains(google_iam_workload_identity_pool_provider.github.attribute_condition, "assertion.repository_visibility == 'private'"),
      strcontains(google_iam_workload_identity_pool_provider.github.attribute_condition, "assertion.event_name == 'workflow_dispatch'"),
      strcontains(google_iam_workload_identity_pool_provider.github.attribute_condition, "assertion.ref == 'refs/heads/review'"),
      strcontains(google_iam_workload_identity_pool_provider.github.attribute_condition, "assertion.workflow_ref == 'example-org/example-repo/.github/workflows/ops.yml@refs/heads/review'"),
    ])
    error_message = "The WIF attribute condition must bind every supplied repository trust coordinate."
  }

  assert {
    condition     = google_service_account_iam_member.github_impersonation.role == "roles/iam.workloadIdentityUser"
    error_message = "Repository impersonation must use the workloadIdentityUser role."
  }

  assert {
    condition     = length(google_project_iam_member.project_roles) == 0
    error_message = "No project roles may be granted by default."
  }
}
