module "cluster" {
  source = "../../modules/gke-autopilot-cluster"

  project_id      = var.project_id
  region          = var.region
  name            = var.cluster_name
  network         = var.network
  subnetwork      = var.subnetwork
  release_channel = var.release_channel
  resource_labels = var.resource_labels
}
