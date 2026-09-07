mock_provider "google" {}

run "plans_one_guarded_generic_service" {
  command = plan

  variables {
    project_id   = "example-project"
    region       = "us-central1"
    service_name = "review-service"
    image        = "registry.example.invalid/review/service@sha256:0000000000000000000000000000000000000000000000000000000000000000"
    port         = 8080
  }

  assert {
    condition     = module.service.name == "review-service"
    error_message = "service name must flow through the generic composition root"
  }

  assert {
    condition     = module.service.deletion_protection == true
    error_message = "deletion protection must default on"
  }
}
