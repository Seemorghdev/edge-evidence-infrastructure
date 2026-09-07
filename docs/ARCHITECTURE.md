# Architecture and authority boundary

## Product responsibility

This repository defines reusable provider/platform **desired state**. It does not contain an execution plane.

The repository currently contains two deliberately small desired-state products:

1. `terraform/modules/gke-autopilot-cluster` plus `terraform/environments/gke-autopilot` — one guarded GKE Autopilot cluster with deployment coordinates and backend configuration supplied externally;
2. `terraform/modules/cloud-run-service` plus `terraform/environments/cloud-run-service-example` — one reusable Cloud Run v2 service contract and a credential-free, single-service example composition.

The GKE module assumes an existing project, VPC network, and subnetwork. It deliberately does not create networks, APIs, IAM, WIF, node pools, Kubernetes workloads, Helm releases, DNS, certificates, or public addresses. Its accepted Phase-1 contract keeps Autopilot enabled, deletion protection and Terraform `prevent_destroy` enabled, and network, subnetwork, and release-channel selections caller-controlled.

The Cloud Run module assumes an existing project and accepts only resource-level desired-state inputs: region, service name, immutable image digest, container port, non-secret environment values, health path, ingress, deletion protection, and bounded scaling/resource settings. Internal-only ingress and deletion protection are defaults. The module owns no service account, IAM grant, API enablement, VPC, DNS, certificate, scheduler, WIF trust, provider credential, public-principal policy, or application topology.

The Cloud Run example composes exactly one generic service with synthetic test coordinates. It has no remote backend binding and its tests mock the Google provider, so repository validation requires no cloud credentials.

## Transitional authority

The copy/generalize phase does not transfer live authority. `Seemorghdev/edge-evidence-reference-platform` remains the active Project 03 source of truth for state, accepted operational evidence, repository-bound execution controls, and live provider relationships.

A future cutover would require separate review of destination CI parity, state/backend ownership, trust identity, provenance, and operational authority. None of those are implied by the current extraction phases.

## Infrastructure versus Operations

Infrastructure answers: **what provider/platform state should exist?**

Operations answers: **which reviewed actor may inspect or change that state, by which exact procedure, and what evidence must be retained?**

Accordingly this repository contains Terraform desired-state definitions but no GitHub issue listener, `/gcp-ops` router, OIDC/WIF consumer workflow, command history, runbook executor, provider credentials, or evidence-retention workflow.

## Application boundary

Reference Platform retains concrete application services and contracts: service names, application routes, workload identities, real image coordinates, application-specific port/probe choices, environment values, same-origin behavior, local composition, and application Kubernetes packaging.

Infrastructure owns only the generic Cloud Run resource contract and its validation rules. Supplying a port, health path, environment map, or immutable image reference to that contract does not transfer ownership of the application behavior represented by those values.
