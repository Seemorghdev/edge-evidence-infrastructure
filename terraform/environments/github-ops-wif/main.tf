locals {
  required_apis = toset([
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "serviceusage.googleapis.com",
    "sts.googleapis.com",
  ])
}

resource "google_project_service" "bootstrap" {
  for_each = local.required_apis

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_service_account" "ops" {
  project      = var.project_id
  account_id   = var.service_account_id
  display_name = var.service_account_display_name
  description  = var.service_account_description

  depends_on = [google_project_service.bootstrap]
}

resource "google_iam_workload_identity_pool" "github" {
  project                   = var.project_id
  workload_identity_pool_id = var.pool_id
  display_name              = "GitHub Actions operations"
  description               = "Generic GitHub Actions OIDC trust provisioning desired state."

  depends_on = [google_project_service.bootstrap]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = var.provider_id
  display_name                       = "GitHub Actions operations"
  description                        = "GitHub OIDC provider restricted to caller-supplied repository trust coordinates."

  attribute_mapping = {
    "google.subject"                  = "assertion.sub"
    "attribute.repository"            = "assertion.repository"
    "attribute.repository_id"         = "assertion.repository_id"
    "attribute.repository_owner_id"   = "assertion.repository_owner_id"
    "attribute.event_name"            = "assertion.event_name"
    "attribute.ref"                   = "assertion.ref"
    "attribute.workflow_ref"          = "assertion.workflow_ref"
    "attribute.repository_visibility" = "assertion.repository_visibility"
  }

  attribute_condition = join(" && ", [
    "assertion.repository == '${var.trusted_repository}'",
    "assertion.repository_id == '${var.trusted_repository_id}'",
    "assertion.repository_owner_id == '${var.trusted_repository_owner_id}'",
    "assertion.repository_visibility == '${var.trusted_visibility}'",
    "assertion.event_name == '${var.trusted_event}'",
    "assertion.ref == '${var.trusted_ref}'",
    "assertion.workflow_ref == '${var.trusted_workflow_ref}'",
  ])

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  depends_on = [google_project_service.bootstrap]
}

resource "google_service_account_iam_member" "github_impersonation" {
  service_account_id = google_service_account.ops.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository_id/${var.trusted_repository_id}"

  depends_on = [google_iam_workload_identity_pool_provider.github]
}

resource "google_project_iam_member" "project_roles" {
  for_each = var.project_roles

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.ops.email}"
}
