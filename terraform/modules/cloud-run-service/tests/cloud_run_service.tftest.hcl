mock_provider "google" {}

variables {
  project_id = "example-project"
  region     = "us-central1"
  name       = "generic-service"
  image      = "registry.example.invalid/generic/service@sha256:1111111111111111111111111111111111111111111111111111111111111111"
  port       = 8080
}

run "defaults_to_internal_only_ingress" {
  command = plan

  assert {
    condition     = google_cloud_run_v2_service.this.ingress == "INGRESS_TRAFFIC_INTERNAL_ONLY"
    error_message = "Cloud Run ingress must default to internal-only."
  }
}

run "rejects_mutable_image" {
  command = plan

  variables {
    image = "registry.example.invalid/generic/service:latest"
  }

  expect_failures = [
    var.image,
  ]
}

run "rejects_unreviewed_ingress" {
  command = plan

  variables {
    ingress = "INGRESS_TRAFFIC_INTERNAL_AND_CLOUD_LOAD_BALANCING"
  }

  expect_failures = [
    var.ingress,
  ]
}

run "flows_custom_runtime_configuration" {
  command = plan

  variables {
    port          = 9090
    max_instances = 7
    cpu           = "2"
    memory        = "1Gi"
    health_path   = "/readyz"
    environment = {
      APP_MODE = "review"
    }
  }

  assert {
    condition     = google_cloud_run_v2_service.this.template[0].containers[0].ports[0].container_port == 9090
    error_message = "Caller-supplied container port must flow into the planned service."
  }

  assert {
    condition     = google_cloud_run_v2_service.this.template[0].scaling[0].max_instance_count == 7
    error_message = "Caller-supplied max instance count must flow into the planned service."
  }

  assert {
    condition = (
      google_cloud_run_v2_service.this.template[0].containers[0].resources[0].limits["cpu"] == "2" &&
      google_cloud_run_v2_service.this.template[0].containers[0].resources[0].limits["memory"] == "1Gi"
    )
    error_message = "Caller-supplied CPU and memory limits must flow into the planned service."
  }

  assert {
    condition = (
      google_cloud_run_v2_service.this.template[0].containers[0].env[0].name == "APP_MODE" &&
      google_cloud_run_v2_service.this.template[0].containers[0].env[0].value == "review"
    )
    error_message = "A non-secret environment variable must flow into the planned service."
  }

  assert {
    condition = (
      google_cloud_run_v2_service.this.template[0].containers[0].startup_probe[0].http_get[0].path == "/readyz" &&
      google_cloud_run_v2_service.this.template[0].containers[0].liveness_probe[0].http_get[0].path == "/readyz"
    )
    error_message = "Startup and liveness HTTP probes must bind the configured health path."
  }
}

run "rejects_reserved_port_environment" {
  command = plan

  variables {
    environment = { PORT = "9090" }
  }

  expect_failures = [
    var.environment,
  ]
}

run "rejects_reserved_service_environment" {
  command = plan

  variables {
    environment = { K_SERVICE = "override" }
  }

  expect_failures = [
    var.environment,
  ]
}

run "rejects_reserved_revision_environment" {
  command = plan

  variables {
    environment = { K_REVISION = "override" }
  }

  expect_failures = [
    var.environment,
  ]
}

run "rejects_reserved_configuration_environment" {
  command = plan

  variables {
    environment = { K_CONFIGURATION = "override" }
  }

  expect_failures = [
    var.environment,
  ]
}
