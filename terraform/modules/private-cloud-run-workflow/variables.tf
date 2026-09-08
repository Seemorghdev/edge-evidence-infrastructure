variable "project_id" {
  description = "Existing Google Cloud project containing the workflow and target Cloud Run services."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid Google Cloud project ID."
  }
}

variable "region" {
  description = "Google Cloud region for the workflow; also the default target region."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z]+-[a-z0-9-]+[0-9]$", var.region))
    error_message = "region must look like a Google Cloud region such as europe-west1."
  }
}

variable "workflow_name" {
  description = "Google Workflow name."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9_-]{0,62}$", var.workflow_name))
    error_message = "workflow_name must start with a lowercase letter and contain at most 63 lowercase letters, digits, hyphens, or underscores."
  }
}

variable "workflow_description" {
  description = "Human-readable workflow resource description."
  type        = string
  nullable    = false

  validation {
    condition     = length(trimspace(var.workflow_description)) >= 1 && length(var.workflow_description) <= 256
    error_message = "workflow_description must contain 1 through 256 characters."
  }
}

variable "workflow_service_account_id" {
  description = "Account ID for the workflow service account."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.workflow_service_account_id))
    error_message = "workflow_service_account_id must be a valid 6-30 character service-account ID."
  }
}

variable "workflow_service_account_display_name" {
  description = "Display name for the workflow service account."
  type        = string
  nullable    = false

  validation {
    condition     = length(trimspace(var.workflow_service_account_display_name)) >= 1 && length(var.workflow_service_account_display_name) <= 100
    error_message = "workflow_service_account_display_name must contain 1 through 100 characters."
  }
}

variable "workflow_service_account_description" {
  description = "Description for the workflow service account."
  type        = string
  nullable    = false

  validation {
    condition     = length(trimspace(var.workflow_service_account_description)) >= 1 && length(var.workflow_service_account_description) <= 256
    error_message = "workflow_service_account_description must contain 1 through 256 characters."
  }
}

variable "workflow_source_contents" {
  description = "Caller-owned workflow source. Infrastructure stores it on the workflow resource but does not define its execution policy."
  type        = string
  nullable    = false

  validation {
    condition     = length(trimspace(var.workflow_source_contents)) >= 1 && length(var.workflow_source_contents) <= 65536
    error_message = "workflow_source_contents must contain 1 through 65536 characters."
  }
}

variable "cloud_run_targets" {
  description = "Bounded Cloud Run service identities that the workflow service account may invoke. Missing target locations use the workflow region."
  type = map(object({
    name     = string
    location = optional(string)
  }))
  default = {}

  validation {
    condition = length(var.cloud_run_targets) <= 16 && alltrue([
      for key in keys(var.cloud_run_targets) : can(regex("^[a-z][a-z0-9_-]{0,31}$", key))
    ])
    error_message = "cloud_run_targets must contain at most 16 stable lowercase keys."
  }

  validation {
    condition = alltrue([
      for target in values(var.cloud_run_targets) : can(regex("^[a-z](?:[a-z0-9-]{0,47}[a-z0-9])?$", target.name))
    ])
    error_message = "each Cloud Run target name must be a non-empty lowercase service identity that does not end in a hyphen."
  }

  validation {
    condition = alltrue([
      for target in values(var.cloud_run_targets) : target.location == null || can(regex("^[a-z]+-[a-z0-9-]+[0-9]$", target.location))
    ])
    error_message = "each optional Cloud Run target location must look like a Google Cloud region."
  }
}
