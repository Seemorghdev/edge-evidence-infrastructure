variable "project_id" {
  description = "Synthetic project ID used only for offline example validation."
  type        = string
  default     = "example-workflow-12345"
}

variable "region" {
  description = "Synthetic workflow region."
  type        = string
  default     = "europe-west1"
}

variable "workflow_name" {
  description = "Synthetic workflow name."
  type        = string
  default     = "example-private-workflow"
}

variable "workflow_description" {
  description = "Synthetic workflow description."
  type        = string
  default     = "Synthetic workflow resource for offline infrastructure review."
}

variable "workflow_service_account_id" {
  description = "Synthetic workflow service-account ID."
  type        = string
  default     = "example-workflow"
}

variable "workflow_service_account_display_name" {
  description = "Synthetic workflow service-account display name."
  type        = string
  default     = "Example private workflow"
}

variable "workflow_service_account_description" {
  description = "Synthetic workflow service-account description."
  type        = string
  default     = "Synthetic workflow identity for offline infrastructure review."
}

variable "workflow_source_contents" {
  description = "Inert synthetic workflow source used only to satisfy the provider resource contract."
  type        = string
  default     = <<-YAML
    main:
      steps:
        - done:
            return: "synthetic-only"
  YAML
}

variable "cloud_run_targets" {
  description = "Synthetic target identities used only for offline planning."
  type = map(object({
    name     = string
    location = optional(string)
  }))
  default = {
    synthetic = {
      name = "example-private-service"
    }
  }
}
