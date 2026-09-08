mock_provider "google" {}

run "plans_inert_synthetic_example" {
  command = plan

  assert {
    condition = (
      output.workflow.name == "example-private-workflow" &&
      output.workflow.region == "europe-west1"
    )
    error_message = "The example must remain obviously synthetic and parameter-driven."
  }

  assert {
    condition     = output.invoker_target_count == 1
    error_message = "The example must compose exactly one synthetic Cloud Run target."
  }
}
