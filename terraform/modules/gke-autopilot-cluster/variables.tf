variable "project_id" {
  description = "Google Cloud project that will contain the cluster."
  type        = string
}

variable "region" {
  description = "Regional GKE location."
  type        = string
}

variable "name" {
  description = "GKE cluster name."
  type        = string
}

variable "network" {
  description = "Existing VPC network name or self link."
  type        = string
}

variable "subnetwork" {
  description = "Existing regional subnetwork name or self link."
  type        = string
}

variable "release_channel" {
  description = "GKE release channel."
  type        = string
  default     = "STABLE"

  validation {
    condition     = contains(["RAPID", "REGULAR", "STABLE", "EXTENDED"], var.release_channel)
    error_message = "release_channel must be RAPID, REGULAR, STABLE, or EXTENDED."
  }
}

variable "resource_labels" {
  description = "Resource labels applied to the cluster."
  type        = map(string)
  default     = {}
}
