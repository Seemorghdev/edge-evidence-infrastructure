variable "project_id" {
  description = "Target Google Cloud project ID. Supply explicitly; no live project is embedded here."
  type        = string
}

variable "region" {
  description = "Regional GKE location."
  type        = string
}

variable "cluster_name" {
  description = "Autopilot cluster name."
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
}

variable "resource_labels" {
  description = "Resource labels for the cluster."
  type        = map(string)
  default     = {}
}
