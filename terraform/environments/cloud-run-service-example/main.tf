module "service" {
  source = "../../modules/cloud-run-service"

  project_id          = var.project_id
  region              = var.region
  name                = var.service_name
  image               = var.image
  port                = var.port
  health_path         = var.health_path
  environment         = var.environment
  ingress             = var.ingress
  deletion_protection = var.deletion_protection
  max_instances       = var.max_instances
  cpu                 = var.cpu
  memory              = var.memory
}
