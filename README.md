# Edge Evidence Infrastructure

Reusable, reviewable **desired-state** infrastructure for the Edge Evidence portfolio.

## Authority boundary

This repository defines what provider/platform state *should* exist. It does not authorize or execute provider changes.

During the current extraction phase, `Seemorghdev/edge-evidence-reference-platform` at source baseline `403ee070fcf31120c3f715bc32bb1643b428f7d2` **remains the live Project 03 authority** for active state, backend bindings, operational workflows, accepted cloud evidence, and the existing external address. This repository is a sanitized copy/generalization target only.

Repository approval does **not** grant authority for cloud authentication, Terraform plan/apply/import against live state, state migration, WIF trust changes, Project 03 cutover, address adoption/promotion, DNS/TLS changes, or provider mutation.

## Desired-state products

- `terraform/modules/gke-autopilot-cluster` plus `terraform/environments/gke-autopilot`: one guarded GKE Autopilot cluster with externally supplied deployment and backend coordinates.
- `terraform/modules/cloud-run-service` plus `terraform/environments/cloud-run-service-example`: one generic Cloud Run v2 service requiring an immutable image digest, internal-only ingress by default, deletion protection, bounded runtime inputs, and health probes.
- `terraform/environments/gke-exposure-address`: one guarded global external IPv4 desired-state resource with generic caller-supplied coordinates, optional desired address, and an externally configured backend.

The Cloud Run example deliberately composes one generic service. It is not the Reference Platform's three-service application topology and carries no application routes, image identities, or Project 03 coordinates.

The global-address environment is intentionally duplicated desired state during extraction. It does not identify, import, adopt, promote, bind, or otherwise claim the existing Project 03 address. Its desired-address input defaults to `null`, allowing provider allocation only if a separately authorized execution plane later applies it.

## Credential-free review

```bash
terraform fmt -check -recursive
terraform -chdir=terraform/environments/gke-autopilot init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/gke-autopilot validate
terraform -chdir=terraform/environments/gke-autopilot test -no-color
terraform -chdir=terraform/environments/cloud-run-service-example init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/cloud-run-service-example validate
terraform -chdir=terraform/environments/cloud-run-service-example test -no-color
terraform -chdir=terraform/environments/gke-exposure-address init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/gke-exposure-address validate
terraform -chdir=terraform/environments/gke-exposure-address test -no-color
terraform -chdir=terraform/modules/cloud-run-service init -backend=false -input=false
terraform -chdir=terraform/modules/cloud-run-service validate
terraform -chdir=terraform/modules/cloud-run-service test -no-color
python scripts/check_policy.py
python -m unittest discover -s tests -v
```

All Terraform test lanes use a mocked Google provider. No GCP credentials are required or expected.

## Deliberately absent

No live Project 03 coordinates, retained external IPv4, state/plan/import material, address adoption evidence, WIF/IAM/API-enablement resources, operational workflows, Kubernetes workloads/Ingress/Service/NEG, DNS/TLS/certificates, provider-authenticated CI, or cloud execution are present.

A later explicit authority-cutover review is required before this repository can become canonical for existing live state. Operations/execution governance belongs to the separate Operations product.

## Provenance

See [`docs/PROVENANCE.md`](docs/PROVENANCE.md).
