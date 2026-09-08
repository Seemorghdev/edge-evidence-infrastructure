mock_provider "google" {}

override_resource {
  target = google_iam_workload_identity_pool.github
  values = {
    name = "synthetic-pool-resource-name"
  }
}

override_resource {
  target = google_service_account.ops
  values = {
    name  = "synthetic-service-account-resource-name"
    email = "synthetic-ops@example.invalid"
  }
}

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
    condition = setequals(toset(keys(google_project_service.bootstrap)), toset([
      "cloudresourcemanager.googleapis.com",
      "iam.googleapis.com",
      "iamcredentials.googleapis.com",
      "serviceusage.googleapis.com",
      "sts.googleapis.com",
    ]))
    error_message = "Bootstrap API inventory must match the reviewed WIF provisioning set."
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
    condition     = one(google_iam_workload_identity_pool_provider.github.oidc).issuer_uri == "https://token.actions.githubusercontent.com"
    error_message = "The WIF provider must use the GitHub Actions OIDC issuer."
  }

  assert {
    condition = google_iam_workload_identity_pool_provider.github.attribute_mapping == {
      "google.subject"                  = "assertion.sub"
      "attribute.repository"            = "assertion.repository"
      "attribute.repository_id"         = "assertion.repository_id"
      "attribute.repository_owner_id"   = "assertion.repository_owner_id"
      "attribute.event_name"            = "assertion.event_name"
      "attribute.ref"                   = "assertion.ref"
      "attribute.workflow_ref"          = "assertion.workflow_ref"
      "attribute.repository_visibility" = "assertion.repository_visibility"
    }
    error_message = "GitHub OIDC claim mapping must retain the reviewed trust claims."
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
    condition = (
      google_service_account_iam_member.github_impersonation.role == "roles/iam.workloadIdentityUser" &&
      google_service_account_iam_member.github_impersonation.member == "principalSet://iam.googleapis.com/synthetic-pool-resource-name/attribute.repository_id/123456789"
    )
    error_message = "Repository impersonation must derive from the generic pool and immutable repository ID."
  }

  assert {
    condition     = length(google_project_iam_member.project_roles) == 0
    error_message = "No project roles may be granted by default."
  }
}

run "plans_one_bounded_project_role" {
  command = plan

  variables {
    project_roles = ["roles/logging.viewer"]
  }

  assert {
    condition = (
      length(google_project_iam_member.project_roles) == 1 &&
      one(values(google_project_iam_member.project_roles)).role == "roles/logging.viewer" &&
      one(values(google_project_iam_member.project_roles)).member == "serviceAccount:synthetic-ops@example.invalid"
    )
    error_message = "A supplied project role must create only its corresponding service-account IAM member."
  }
}

run "rejects_malformed_repository" {
  command = plan

  variables {
    trusted_repository = "example-org"
  }

  expect_failures = [var.trusted_repository]
}

run "rejects_malformed_repository_id" {
  command = plan

  variables {
    trusted_repository_id = "not-numeric"
  }

  expect_failures = [var.trusted_repository_id]
}

run "rejects_malformed_owner_id" {
  command = plan

  variables {
    trusted_repository_owner_id = "0"
  }

  expect_failures = [var.trusted_repository_owner_id]
}

run "rejects_malformed_workflow_ref" {
  command = plan

  variables {
    trusted_workflow_ref = "example-org/example-repo/.github/workflows/ops.yml"
  }

  expect_failures = [var.trusted_workflow_ref]
}

run "rejects_malformed_ref" {
  command = plan

  variables {
    trusted_ref = "main"
  }

  expect_failures = [var.trusted_ref]
}

run "rejects_unreviewed_event" {
  command = plan

  variables {
    trusted_event = "pull_request"
  }

  expect_failures = [var.trusted_event]
}

run "rejects_invalid_visibility" {
  command = plan

  variables {
    trusted_visibility = "secret"
  }

  expect_failures = [var.trusted_visibility]
}
