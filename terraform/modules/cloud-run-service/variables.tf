variable "project_id" {
  description = "Existing Google Cloud project containing the Cloud Run service."
  type        = string
}

variable "region" {
  description = "Cloud Run region."
  type        = string
}

variable "name" {
  description = "Cloud Run service name."
  type        = string
}

variable "image" {
  description = "Immutable container image reference."
  type        = string
  validation {
    condition     = can(regex("@sha256:[0-9a-f]{64}$", var.image))
    error_message = "image must end in an immutable sha256 digest."
  }
}

variable "port" {
  description = "Container listening port."
  type        = number
  validation {
    condition     = var.port >= 1 && var.port <= 65535 && floor(var.port) == var.port
    error_message = "port must be an integer from 1 through 65535."
  }
}

variable "health_path" {
  description = "HTTP health endpoint used for startup and liveness probes."
  type        = string
  default     = "/healthz"
  validation {
    condition     = startswith(var.health_path, "/")
    error_message = "health_path must start with /."
  }
}

variable "environment" {
  description = "Non-secret environment variables."
  type        = map(string)
  default     = {}
  validation {
    condition = length(setintersection(toset(keys(var.environment)), toset([
      "PORT", "K_SERVICE", "K_REVISION", "K_CONFIGURATION"
    ]))) == 0
    error_message = "environment must not set reserved Cloud Run variables."
  }
}

variable "ingress" {
  description = "Cloud Run ingress; internal-only is the default."
  type        = string
  default     = "INGRESS_TRAFFIC_INTERNAL_ONLY"
  validation {
    condition = contains([
      "INGRESS_TRAFFIC_INTERNAL_ONLY",
      "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
      "INGRESS_TRAFFIC_ALL",
    ], var.ingress)
    error_message = "ingress must use one reviewed Cloud Run ingress value."
  }
}

variable "deletion_protection" {
  description = "Protect the service from accidental deletion."
  type        = bool
  default     = true
}

variable "max_instances" {
  description = "Maximum Cloud Run instance count."
  type        = number
  default     = 2
  validation {
    condition     = var.max_instances >= 1 && var.max_instances <= 100 && floor(var.max_instances) == var.max_instances
    error_message = "max_instances must be an integer from 1 through 100."
  }
}

variable "cpu" {
  description = "Container CPU limit."
  type        = string
  default     = "1"
  validation {
    condition     = contains(["1", "2", "4", "8"], var.cpu)
    error_message = "cpu must be one of 1, 2, 4, or 8."
  }
}

variable "memory" {
  description = "Container memory limit."
  type        = string
  default     = "512Mi"
  validation {
    condition     = can(regex("^[1-9][0-9]*(Mi|Gi)$", var.memory))
    error_message = "memory must be a positive Mi or Gi quantity."
  }
}
