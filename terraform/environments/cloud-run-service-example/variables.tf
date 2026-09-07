variable "project_id" { type = string }
variable "region" { type = string }
variable "service_name" { type = string }
variable "image" { type = string }
variable "port" { type = number }
variable "health_path" { type = string default = "/healthz" }
variable "environment" { type = map(string) default = {} }
variable "ingress" { type = string default = "INGRESS_TRAFFIC_INTERNAL_ONLY" }
variable "deletion_protection" { type = bool default = true }
variable "max_instances" { type = number default = 2 }
variable "cpu" { type = string default = "1" }
variable "memory" { type = string default = "512Mi" }
