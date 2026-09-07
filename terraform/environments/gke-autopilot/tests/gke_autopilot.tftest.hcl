mock_provider "google" {}

run "plans_guarded_autopilot_cluster" {
  command = plan

  variables {
    project_id      = "example-project"
    region          = "us-central1"
    cluster_name    = "example-autopilot"
    network         = "example-network"
    subnetwork      = "example-subnetwork"
    release_channel = "STABLE"
    resource_labels = { purpose = "offline-test" }
  }

  assert {
    condition     = output.cluster_name == "example-autopilot"
    error_message = "cluster name must remain input-bound"
  }

  assert {
    condition     = output.cluster_location == "us-central1"
    error_message = "cluster location must remain input-bound"
  }

  assert {
    condition     = output.autopilot_enabled == true
    error_message = "Autopilot must remain enabled"
  }

  assert {
    condition     = output.deletion_protection == true
    error_message = "deletion protection must remain enabled"
  }
}
