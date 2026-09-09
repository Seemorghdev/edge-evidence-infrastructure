# Edge Evidence Infrastructure

Reusable, reviewable **desired-state** infrastructure for the Edge Evidence portfolio.

## Authority boundary

This repository defines what provider/platform state *should* exist. It does not authorize or execute provider changes.

During the current extraction phase, `Seemorghdev/edge-evidence-reference-platform` at source baseline `403ee070fcf31120c3f715bc32bb1643b428f7d2` **remains the live Project 03 authority** for active state, backend bindings, operational workflows, accepted cloud evidence, the existing external address, current workflow/application behavior, current Kubernetes application topology, and current WIF/trust relationships. This repository is a sanitized copy/generalization target only.

Repository approval does **not** grant authority for cloud authentication, Terraform plan/apply/import against live state, state migration, workflow execution, WIF trust consumption/migration, Project 03 cutover, address adoption/promotion, Kubernetes deployment, DNS/TLS changes, or provider mutation.

## Desired-state products

- `terraform/modules/gke-autopilot-cluster` plus `terraform/environments/gke-autopilot`: one guarded GKE Autopilot cluster with externally supplied deployment and backend coordinates.
- `terraform/modules/cloud-run-service` plus `terraform/environments/cloud-run-service-example`: one generic Cloud Run v2 service requiring an immutable image digest, internal-only ingress by default, deletion protection, bounded runtime inputs, and health probes.
- `terraform/environments/gke-exposure-address`: one guarded global external IPv4 desired-state resource with generic caller-supplied coordinates, optional desired address, and an externally configured backend.
- `terraform/environments/github-ops-wif`: generic GitHub Actions OIDC → Google Workload Identity Federation **provisioning desired state** with caller-supplied repository trust coordinates and no project roles by default.
- `terraform/modules/private-cloud-run-workflow` plus `terraform/environments/private-cloud-run-workflow-example`: one generic Google Workflow identity/resource plus bounded `roles/run.invoker` bindings to caller-supplied private Cloud Run service identities.
- reusable platform-state primitives under `platform/`, `kustomize/`, `helm-chart/`, and `observability/`: namespace state, a generic NEG annotation patch, network policy, Istio mTLS/namespace injection, and OpenTelemetry collector/configuration surfaces. These are inert desired-state/rendering assets, not a Kubernetes execution plane.

The Cloud Run example deliberately composes one generic service. It is not the Reference Platform's three-service application topology and carries no application routes, image identities, or Project 03 coordinates.

The global-address environment is intentionally duplicated desired state during extraction. It does not identify, import, adopt, promote, bind, or otherwise claim the existing Project 03 address. Its desired-address input defaults to `null`, allowing provider allocation only if a separately authorized execution plane later applies it.

The GitHub WIF environment provisions only the generic trust resources: bootstrap APIs, one operations service account, one pool/provider, one repository-ID-scoped impersonation binding, and optional bounded project-role bindings. All repository/workflow/ref/event/visibility identities are required caller inputs; project roles default to empty. It contains no WIF consumption workflow, GitHub token exchange, provider credentials, or claim that current live trust has moved here.

The private Cloud Run workflow module provisions only a workflow service account, a Google Workflow resource, and zero or more Cloud Run service IAM members with the fixed `roles/run.invoker` role. Workflow source is required caller input and is outside Infrastructure execution/control ownership. The example source is inert and synthetic. No Project 03 service names, routes, target URIs, provider readback, GitHub WIF trust, token exchange, retry policy, probe program, or HTTP execution semantics were copied. The source workflow's `deletion_protection = false` is retained as generic desired-state semantics only; it does not authorize deletion or adoption of any existing workflow.

The Phase 7 platform-state surfaces are deliberately narrower than the Reference Platform's Kubernetes/application packaging. Application Deployments, Services, Ingress routes, local/dev overlays, load-generator composition, Skaffold orchestration, and application Helm templates remain Reference Platform-owned. The retained OTel Deployment/Service is platform observability plumbing only.

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
terraform -chdir=terraform/environments/github-ops-wif init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/github-ops-wif validate
terraform -chdir=terraform/environments/github-ops-wif test -no-color
terraform -chdir=terraform/environments/private-cloud-run-workflow-example init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform/environments/private-cloud-run-workflow-example validate
terraform -chdir=terraform/environments/private-cloud-run-workflow-example test -no-color
terraform -chdir=terraform/modules/cloud-run-service init -backend=false -input=false
terraform -chdir=terraform/modules/cloud-run-service validate
terraform -chdir=terraform/modules/cloud-run-service test -no-color
terraform -chdir=terraform/modules/private-cloud-run-workflow init -backend=false -input=false
terraform -chdir=terraform/modules/private-cloud-run-workflow validate
terraform -chdir=terraform/modules/private-cloud-run-workflow test -no-color
python scripts/check_terraform_completion.py
python scripts/check_infrastructure_manifest.py
python scripts/check_platform_authority.py
python scripts/validate_surfaces.py
python scripts/check_policy.py
python -m unittest discover -s tests -v
```

All Terraform test lanes use a mocked Google provider. The private-workflow module includes one mocked Terraform `apply` run solely to resolve synthetic computed service-account attributes for exact IAM-member proof; the mock provider performs no GCP operation. No GCP credentials are required or expected. The retained platform validation is structural and credential-free; it performs no cluster access or mutation.

## Deliberately absent

No live Project 03 coordinates, retained external IPv4, state/plan/import material, address adoption evidence, live workflow/service-account/Cloud Run target identities, live WIF pool/provider/service-account/repository coordinates, WIF consumption workflow, provider authentication, operational workflow program, application workloads/routes, application Ingress, application Helm/Kustomize/Skaffold orchestration, DNS/TLS/certificates, or cloud/Kubernetes execution are present.

A later explicit authority-cutover review is required before this repository can become canonical for existing live state, workflows, trust, or Kubernetes application deployment. Operations/execution governance, workflow runtime/control semantics, WIF consumption semantics, and live Kubernetes mutation remain outside this repository.

## Provenance

See [`docs/PROVENANCE.md`](docs/PROVENANCE.md) and [`docs/REPOSITORY_WIDE_EXTRACTION.md`](docs/REPOSITORY_WIDE_EXTRACTION.md).
