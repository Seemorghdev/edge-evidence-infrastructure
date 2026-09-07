mock_provider "google" {}

variables {
  project_id = "example-project"
  name       = "review-global-address"
  labels = {
    managed_by = "terraform"
  }
}

run "plans_one_guarded_global_external_ipv4" {
  command = plan

  assert {
    condition     = google_compute_global_address.this.project == "example-project"
    error_message = "The caller-supplied project must bind to the global address."
  }

  assert {
    condition     = google_compute_global_address.this.name == "review-global-address"
    error_message = "The caller-supplied resource name must bind to the global address."
  }

  assert {
    condition     = google_compute_global_address.this.address_type == "EXTERNAL"
    error_message = "The address must remain external."
  }

  assert {
    condition     = google_compute_global_address.this.ip_version == "IPV4"
    error_message = "The address must remain IPv4."
  }

  assert {
    condition     = google_compute_global_address.this.labels["managed_by"] == "terraform"
    error_message = "Caller-supplied non-sensitive labels must bind to the global address."
  }

  assert {
    condition     = var.desired_address == null
    error_message = "Provider allocation must remain the default desired-address behavior."
  }
}

run "binds_optional_synthetic_desired_address" {
  command = plan

  variables {
    desired_address = "192.0.2.42"
  }

  assert {
    condition     = google_compute_global_address.this.address == "192.0.2.42"
    error_message = "An explicitly supplied documentation-only IPv4 value must bind to the resource."
  }
}
