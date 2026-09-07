variable "project_id" {
  description = "Existing Google Cloud project in which the global address would be managed by an authorized execution plane."
  type        = string
}

variable "name" {
  description = "Global address resource name."
  type        = string
}

variable "labels" {
  description = "Non-sensitive labels to apply to the global address."
  type        = map(string)
  default     = {}
}

variable "desired_address" {
  description = "Optional desired IPv4 address. Leave null to allow provider allocation when an authorized apply occurs elsewhere."
  type        = string
  default     = null
  nullable    = true
}
