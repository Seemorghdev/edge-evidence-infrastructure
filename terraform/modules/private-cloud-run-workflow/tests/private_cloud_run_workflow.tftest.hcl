mock_provider "google" {}

override_resource {
  target = google_service_account.workflow
  values = {
    email = "example-workflow\u0040example-workflow-12345.iam.gserviceaccount.com"
  }
}

variables {
  project_id                           = "example-workflow-12345"
  region                               = "europe-west1"
  workflow_name                        = "example-private-workflow"
  workflow_description                 = "Synthetic workflow resource for offline infrastructure review."
  workflow_service_account_id          = "example-workflow"
  workflow_service_account_display_name = "Example private workflow"
  workflow_service_account_description = "Synthetic workflow identity for offline infrastructure review."
  workflow_source_contents             = <<-YAML
    main:
      steps:
        - done:
            return: "synthetic-only"
  YAML
  cloud_run_targets = {
    alpha = {
      name = "example-private-service"
    }
    beta = {
      name     = "example-private-service-two"
      location = "europe-west2"
    }
  }
}

run "plans_bounded_workflow_substrate" {
  command = plan

  assert {
    condition = (
      google_service_account.workflow.project == "example-workflow-12345" &&
      google_service_account.workflow.account_id == "example-workflow"
    )
    error_message = "Workflow service-account inputs must flow through generically."
  }

  assert {
    condition = (
      google_workflows_workflow.this.project == "example-workflow-12345" &&
      google_workflows_workflow.this.region == "europe-west1" &&
      google_workflows_workflow.this.name == "example-private-workflow" &&
      google_workflows_workflow.this.source_contents == var.workflow_source_contents &&
      google_workflows_workflow.this.call_log_level == "LOG_NONE" &&
      google_workflows_workflow.this.execution_history_level == "EXECUTION_HISTORY_BASIC" &&
      google_workflows_workflow.this.deletion_protection == false
    )
    error_message = "Workflow desired state must preserve the generic provisioning substrate."
  }

  assert {
    condition     = length(google_cloud_run_v2_service_iam_member.workflow_invoker) == 2
    error_message = "Exactly one Cloud Run IAM member must be planned per supplied target."
  }

  assert {
    condition = alltrue([
      google_cloud_run_v2_service_iam_member.workflow_invoker["alpha"].project == "example-workflow-12345",
      google_cloud_run_v2_service_iam_member.workflow_invoker["alpha"].location == "europe-west1",
      google_cloud_run_v2_service_iam_member.workflow_invoker["alpha"].name == "example-private-service",
      google_cloud_run_v2_service_iam_member.workflow_invoker["alpha"].role == "roles/run.invoker",
      google_cloud_run_v2_service_iam_member.workflow_invoker["beta"].location == "europe-west2",
      google_cloud_run_v2_service_iam_member.workflow_invoker["beta"].name == "example-private-service-two",
      google_cloud_run_v2_service_iam_member.workflow_invoker["beta"].role == "roles/run.invoker",
    ])
    error_message = "Cloud Run IAM bindings must preserve caller target identities and the fixed invoker role."
  }
}

# Terraform 1.9 keeps mocked computed service-account attributes unknown during
# plan. This provider-isolated apply proves the final IAM members without any
# provider authentication or GCP operation.
run "proves_workflow_identity_invoker_members" {
  command = apply

  assert {
    condition = alltrue([
      google_cloud_run_v2_service_iam_member.workflow_invoker["alpha"].member == "serviceAccount:example-workflow\u0040example-workflow-12345.iam.gserviceaccount.com",
      google_cloud_run_v2_service_iam_member.workflow_invoker["beta"].member == "serviceAccount:example-workflow\u0040example-workflow-12345.iam.gserviceaccount.com",
    ])
    error_message = "Every target must bind the workflow service account as roles/run.invoker."
  }
}

run "allows_empty_target_set" {
  command = plan

  variables {
    cloud_run_targets = {}
  }

  assert {
    condition     = length(google_cloud_run_v2_service_iam_member.workflow_invoker) == 0
    error_message = "An empty target set must create no Cloud Run IAM members."
  }
}

run "rejects_malformed_project" {
  command = plan
  variables { project_id = "BAD" }
  expect_failures = [var.project_id]
}

run "rejects_malformed_region" {
  command = plan
  variables { region = "west" }
  expect_failures = [var.region]
}

run "rejects_malformed_workflow_name" {
  command = plan
  variables { workflow_name = "Bad Workflow" }
  expect_failures = [var.workflow_name]
}

run "rejects_malformed_service_account" {
  command = plan
  variables { workflow_service_account_id = "x" }
  expect_failures = [var.workflow_service_account_id]
}

run "rejects_empty_workflow_source" {
  command = plan
  variables { workflow_source_contents = "   " }
  expect_failures = [var.workflow_source_contents]
}

run "rejects_malformed_target" {
  command = plan
  variables {
    cloud_run_targets = {
      bad = { name = "Bad Service" }
    }
  }
  expect_failures = [var.cloud_run_targets]
}

run "rejects_malformed_target_location" {
  command = plan
  variables {
    cloud_run_targets = {
      bad = {
        name     = "example-private-service"
        location = "nowhere"
      }
    }
  }
  expect_failures = [var.cloud_run_targets]
}
