# Architecture and authority boundary

## Product responsibility

This repository defines reusable provider/platform **desired state**. It does not contain an execution plane.

The Phase-1 GKE product has two layers:

1. `terraform/modules/gke-autopilot-cluster` — the reusable cluster resource contract;
2. `terraform/environments/gke-autopilot` — a sanitized composition root whose deployment coordinates and backend configuration are supplied externally.

The module assumes an existing project, VPC network, and subnetwork. It deliberately does not create networks, APIs, IAM, WIF, node pools, Kubernetes workloads, Helm releases, DNS, certificates, or public addresses.

## Transitional authority

The copy/generalize phase does not transfer live authority. `Seemorghdev/edge-evidence-reference-platform` remains the active Project 03 source of truth for state, accepted operational evidence, repository-bound execution controls, and live provider relationships.

A future cutover would require separate review of destination CI parity, state/backend ownership, trust identity, provenance, and operational authority. None of those are implied by Phase 1.

## Infrastructure versus Operations

Infrastructure answers: **what provider/platform state should exist?**

Operations answers: **which reviewed actor may inspect or change that state, by which exact procedure, and what evidence must be retained?**

Accordingly this repository contains Terraform desired-state definitions but no GitHub issue listener, `/gcp-ops` router, OIDC/WIF consumer workflow, command history, runbook executor, provider credentials, or evidence-retention workflow.

## Application boundary

Reference Platform retains application services, application contracts, workload images, service ports/probes/environment semantics, same-origin route intent, local composition, and application-level Kubernetes packaging. Phase 1 contains no Kubernetes workload manifests.
