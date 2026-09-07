# Edge Evidence Infrastructure

Reusable, reviewable **desired-state** infrastructure for the Edge Evidence portfolio.

## Authority boundary

This repository defines what provider/platform state *should* exist. It does not authorize or execute provider changes.

During the current extraction phase, `Seemorghdev/edge-evidence-reference-platform` at source baseline `403ee070fcf31120c3f715bc32bb1643b428f7d2` **remains the live Project 03 authority** for active state, backend bindings, operational workflows, and accepted cloud evidence. This repository is a sanitized copy/generalization target only.

Repository approval does **not** grant authority for cloud authentication, Terraform plan/apply/import against live state, state migration, WIF trust changes, Project 03 cutover, DNS/TLS changes, or provider mutation.

## Desired-state products

- `terraform/modules/gke-autopilot-cluster` plus `terraform/environments/gke-autopilot`: one guarded GKE Autopilot cluster with externally supplied deployment and backend coordinates.
- `terraform/modules/cloud-run-service` plus `terraform/environments/cloud-run-service-example`: one generic Cloud Run v2 service requiring an immutable image digest, internal-only ingress by default, deletion protection, bounded runtime inputs, and health probes.

The Cloud Run example deliberately composes one generic service. It is not the Reference Platform's three-service application topology and carries no application routes, image identities, or Project 03 coordinates.

## Credential-free review

```bash
terraform fmt -check -recursive
terraform -chdir=terraform/environments/gke-autopilot init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/gke-autopilot validate
terraform -chdir=terraform/environments/gke-autopilot test -no-color
terraform -chdir=terraform/environments/cloud-run-service-example init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/cloud-run-service-example validate
terraform -chdir=terraform/environments/cloud-run-service-example test -no-color
python scripts/check_policy.py
python -m unittest discover -s tests -v
```

Both Terraform tests use a mocked Google provider. No GCP credentials are required or expected.

## Deliberately absent

No live Project 03 coordinates, state/plan/import material, exposure-address state, WIF/IAM/API-enablement resources, operational workflows, Kubernetes workloads/Ingress/NEG, DNS/TLS/certificates, provider-authenticated CI, or cloud execution are present.

A later explicit authority-cutover review is required before this repository can become canonical for existing live state. Operations/execution governance belongs to the separate Operations product.

## Provenance

See [`docs/PROVENANCE.md`](docs/PROVENANCE.md).
