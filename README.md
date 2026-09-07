# Edge Evidence Infrastructure

Reusable, reviewable **desired-state** infrastructure for the Edge Evidence portfolio.

## Authority boundary

This repository defines what provider/platform state *should* exist. It does not authorize or execute provider changes.

During the current extraction phase, `Seemorghdev/edge-evidence-reference-platform` at source baseline `403ee070fcf31120c3f715bc32bb1643b428f7d2` **remains the live Project 03 authority** for active state, backend bindings, operational workflows, and accepted cloud evidence. This repository is a sanitized copy/generalization target only.

Repository approval does **not** grant authority for cloud authentication, Terraform plan/apply/import against live state, state migration, WIF trust changes, Project 03 cutover, DNS/TLS changes, or provider mutation.

## Phase 1 product

Phase 1 contains one narrow desired-state product:

- `terraform/modules/gke-autopilot-cluster` — one guarded GKE Autopilot cluster resource;
- `terraform/environments/gke-autopilot` — a sanitized composition root with externally supplied project/network/backend coordinates;
- mocked Terraform tests and offline policy/privacy checks;
- credential-free CI.

The module preserves these application-independent platform guarantees:

- Autopilot enabled;
- regional cluster location supplied by input;
- existing network/subnetwork supplied by input;
- explicit GKE release channel;
- deletion protection enabled;
- Terraform `prevent_destroy` lifecycle protection.

## What is deliberately absent

Phase 1 contains no:

- live Project 03 project, cluster, registry, endpoint, address, account, or backend coordinates;
- Terraform state, plan files, imports, or migration commands;
- exposure-address desired state;
- WIF pools/providers, IAM bindings, service accounts, or API-enablement resources;
- GitHub OIDC consumption or operational command workflows;
- Kubernetes workload, namespace, Ingress, NEG, service-mesh, or application manifests;
- DNS, hostname, TLS, certificate, or public endpoint state;
- provider-authenticated CI or cloud execution.

## Credential-free review

With Terraform 1.9.x installed:

```bash
terraform fmt -check -recursive
terraform -chdir=terraform/environments/gke-autopilot init \
  -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/gke-autopilot validate
terraform -chdir=terraform/environments/gke-autopilot test -no-color
python scripts/check_policy.py
python -m unittest discover -s tests -v
```

The Terraform test uses a mocked Google provider. No GCP credentials are required or expected.

## Backend and execution model

The example root declares an empty `backend "gcs" {}` block only to establish backend *type*. Bucket/prefix/state coordinates are intentionally external and absent. CI disables backend initialization entirely.

A later authority-cutover review would be required before this repository could become canonical for any existing live state. Operations/execution governance belongs to the separate Operations product, not to this desired-state repository.

## Provenance

See [`docs/PROVENANCE.md`](docs/PROVENANCE.md). The reusable Autopilot module is a sanitized semantic extraction from the reviewed Reference Platform source baseline; no live environment bytes were copied verbatim.
