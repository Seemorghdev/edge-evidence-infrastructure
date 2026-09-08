variable "project_id" {
  description = "Existing Google Cloud project in which generic GitHub WIF trust should be provisioned."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid Google Cloud project ID."
  }
}

variable "service_account_id" {
  description = "Operations service-account ID to provision."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.service_account_id))
    error_message = "service_account_id must be 6-30 lowercase letters, digits, or hyphens and start with a letter."
  }
}

variable "service_account_display_name" {
  description = "Human-readable operations service-account display name."
  type        = string
  nullable    = false

  validation {
    condition     = length(trimspace(var.service_account_display_name)) >= 3 && length(var.service_account_display_name) <= 100
    error_message = "service_account_display_name must contain 3-100 characters."
  }
}

variable "service_account_description" {
  description = "Optional non-sensitive description for the operations service account."
  type        = string
  default     = null

  validation {
    condition     = var.service_account_description == null || length(var.service_account_description) <= 256
    error_message = "service_account_description must be null or at most 256 characters."
  }
}

variable "pool_id" {
  description = "Workload Identity Pool ID."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}[a-z0-9]$", var.pool_id))
    error_message = "pool_id must be 4-32 lowercase letters, digits, or hyphens and start with a letter."
  }
}

variable "provider_id" {
  description = "GitHub OIDC Workload Identity Pool Provider ID."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}[a-z0-9]$", var.provider_id))
    error_message = "provider_id must be 4-32 lowercase letters, digits, or hyphens and start with a letter."
  }
}

variable "trusted_repository" {
  description = "Trusted GitHub repository in owner/name form."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.trusted_repository))
    error_message = "trusted_repository must use owner/name form."
  }
}

variable "trusted_repository_id" {
  description = "Immutable numeric GitHub repository ID represented as a string."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[1-9][0-9]*$", var.trusted_repository_id))
    error_message = "trusted_repository_id must contain only a positive numeric GitHub repository ID."
  }
}

variable "trusted_repository_owner_id" {
  description = "Immutable numeric GitHub repository owner ID represented as a string."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[1-9][0-9]*$", var.trusted_repository_owner_id))
    error_message = "trusted_repository_owner_id must contain only a positive numeric GitHub owner ID."
  }
}

variable "trusted_workflow_ref" {
  description = "Exact trusted workflow ref in owner/repository/.github/workflows/file.yml@refs/heads/branch form."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/\\.github/workflows/[A-Za-z0-9_.-]+\\.ya?ml@refs/heads/[A-Za-z0-9._/-]+$", var.trusted_workflow_ref))
    error_message = "trusted_workflow_ref must identify an exact branch-bound GitHub workflow ref."
  }
}

variable "trusted_ref" {
  description = "Exact trusted Git ref."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^refs/heads/[A-Za-z0-9._/-]+$", var.trusted_ref))
    error_message = "trusted_ref must identify an exact refs/heads/... branch ref."
  }
}

variable "trusted_event" {
  description = "Allowed GitHub Actions event for this operations trust."
  type        = string
  nullable    = false

  validation {
    condition     = contains(["workflow_dispatch", "push"], var.trusted_event)
    error_message = "trusted_event must be workflow_dispatch or push."
  }
}

variable "trusted_visibility" {
  description = "Expected GitHub repository visibility claim."
  type        = string
  nullable    = false

  validation {
    condition     = contains(["private", "internal", "public"], var.trusted_visibility)
    error_message = "trusted_visibility must be private, internal, or public."
  }
}

variable "project_roles" {
  description = "Optional bounded project roles granted to the operations service account. Empty by default."
  type        = set(string)
  default     = []

  validation {
    condition = length(var.project_roles) <= 8 && alltrue([
      for role in var.project_roles :
      can(regex("^roles/[A-Za-z0-9_.]+$", role)) &&
      !contains(["roles/owner", "roles/editor", "roles/iam.serviceAccountKeyAdmin"], role)
    ])
    error_message = "project_roles may contain at most eight explicit roles/... values and must not include primitive owner/editor or service-account key administration."
  }
}
