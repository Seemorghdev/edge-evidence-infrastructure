# Edge Evidence Infrastructure

Reusable **desired-state cloud and platform infrastructure** for the Edge Evidence portfolio, designed to be reviewable without granting a repository live cloud authority.

The project separates infrastructure design from infrastructure execution. Terraform modules describe guarded GKE, Cloud Run, static-address, Workload Identity Federation, and private-workflow relationships; Kubernetes/Kustomize/Helm/OpenTelemetry assets describe reusable platform primitives. CI proves those contracts with mocked providers, structural validation, provenance checks, and fail-closed authority scans.

## Why this project is interesting

- **Least-authority by design.** Desired state lives here; provider credentials, live Terraform execution, WIF consumption, cluster mutation, and application operations do not.
- **Portable Terraform contracts.** Live project, network, backend, repository, workflow, and address coordinates are caller-supplied or intentionally absent.
- **Guardrails are executable.** Immutable Cloud Run images, internal ingress defaults, deletion protection, bounded IAM/WIF inputs, `prevent_destroy`, and exact resource inventories are tested.
- **Platform state is composable.** Kubernetes namespace/NEG primitives, Kustomize network-policy/mesh/OTel components, and platform-only Helm/OTel plumbing can be reviewed independently of application workloads.
- **The review path is credential-free.** A clean checkout can run a deterministic portfolio demo using only Python, Git, checked-in assets, and existing repository validators.

## 60-second offline demo

```bash
python scripts/portfolio_demo.py
```

Representative output:

```text
Edge Evidence Infrastructure — offline review
[PASS] Terraform desired-state audit
[PASS] Repository-wide manifest audit
[PASS] Authority/publication policy
[PASS] Retained platform primitives (Kubernetes, Kustomize, Helm, OpenTelemetry)
[PASS] Synthetic backend contract (uniform access, public-access prevention, versioning, soft delete)
[PASS] Live authority: not requested or exercised
RESULT: PASS — credential-free desired-state validation completed
```

The demo performs no network request, cloud authentication, Terraform live action, WIF/OIDC exchange, or Kubernetes deployment. See [`docs/DEMO.md`](docs/DEMO.md) for the exact checks and [`docs/examples/portfolio-demo.txt`](docs/examples/portfolio-demo.txt) for the CI-guarded output contract.

## What is in the repository

| Layer | Purpose | Start here |
| --- | --- | --- |
| Terraform modules | Reusable GKE Autopilot, Cloud Run, and private Cloud Run Workflow contracts | [`terraform/modules/`](terraform/modules/) |
| Terraform examples | Synthetic/offline compositions for GKE, Cloud Run, static address, WIF provisioning, and private workflow | [`terraform/environments/`](terraform/environments/) |
| Kubernetes platform primitives | Namespace and generic GKE NEG desired state | [`platform/kubernetes/`](platform/kubernetes/) |
| Kustomize | Network policy, Istio mTLS/injection, OpenTelemetry components and an observability overlay | [`kustomize/`](kustomize/) |
| Helm / OpenTelemetry | Platform-only mesh/collector rendering and standalone collector configuration | [`helm-chart/`](helm-chart/), [`observability/`](observability/) |
| Validation | Source-derived validation, provenance, authority and publication checks | [`scripts/`](scripts/), [`tests/`](tests/) |
| CI | Complete Terraform/offline policy gate plus Python 3.12/3.13 platform validation | [required](.github/workflows/required.yml), [platform-offline](.github/workflows/platform-offline.yml) |

## Desired-state contracts

### GKE Autopilot

`terraform/modules/gke-autopilot-cluster` owns exactly one guarded Autopilot cluster. Network, subnetwork, and release channel are caller inputs; deletion protection and Terraform `prevent_destroy` remain enabled. The module does not create networks, node pools, workloads, DNS, certificates, or execution credentials.

### Cloud Run

`terraform/modules/cloud-run-service` owns exactly one Cloud Run v2 service. Images must be immutable digests, ingress defaults to internal-only, deletion protection is enabled by default, runtime resources/scaling are bounded, and startup/liveness probes are explicit. IAM, service accounts, APIs, VPC, DNS, certificates, and public principals remain outside this module.

### Static external address

`terraform/environments/gke-exposure-address` models one guarded global external IPv4 resource with caller-supplied identity and optional desired address. It does not import, adopt, release, or claim any existing live address.

### GitHub WIF provisioning

`terraform/environments/github-ops-wif` defines **provisioning desired state** for GitHub OIDC federation: required APIs, one service account, one pool/provider, fail-closed claim conditions, one repository-ID-scoped impersonation binding, and optional bounded project roles. It contains no token exchange or WIF consumer workflow.

### Private Cloud Run workflow substrate

`terraform/modules/private-cloud-run-workflow` defines one workflow service account, one Google Workflow resource, and bounded Cloud Run `roles/run.invoker` bindings to caller-supplied targets. Workflow source is a bounded input; runtime procedure, target URI discovery, WIF consumption, and application probe behavior are not owned here.

### Platform primitives

`platform/`, `kustomize/`, `helm-chart/`, and `observability/` retain reusable namespace, NEG, network-policy, Istio mTLS/injection, and OpenTelemetry desired state. They do not include application Deployments/Services/Ingress routes or a live deployment plane.

## Validation model

The repository proves design claims at several levels:

1. Terraform-native tests use the mocked Google provider and validate exact resource inventories and fail-closed inputs.
2. `scripts/check_policy.py` rejects authority/publication drift and unapproved Terraform surface growth.
3. `scripts/check_platform_authority.py` and `scripts/validate_surfaces.py` validate retained platform assets without cluster access.
4. `scripts/check_infrastructure_manifest.py` and `scripts/check_terraform_completion.py` keep source/provenance accounting deterministic.
5. `scripts/check_portfolio.py` validates recruiter-facing links, output examples, sanitation, and the demo's no-live-authority contract.

See [`docs/EVIDENCE.md`](docs/EVIDENCE.md) for claim-to-proof mapping and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the engineering story.

## What this repository does not do

This repository is **not a live execution plane**. It does not:

- run Terraform plan/apply/import/destroy/state against a provider;
- read or migrate live Terraform state/backends;
- hold cloud/provider credentials;
- consume GitHub OIDC/WIF or exchange tokens;
- run `gcloud` or mutate a Kubernetes cluster;
- install/upgrade Helm releases or deploy with Skaffold;
- own application workloads, routes, DNS, TLS, or current live infrastructure identities;
- publish evidence to live systems or change repository visibility.

Existing live environment, application, and operational authority remains separately governed. This repository provides reusable desired-state definitions and offline evidence for review.

## Navigation

- **Architecture / engineering story:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Runnable demo:** [`docs/DEMO.md`](docs/DEMO.md)
- **Evidence / examples:** [`docs/EVIDENCE.md`](docs/EVIDENCE.md), [`docs/examples/portfolio-demo.txt`](docs/examples/portfolio-demo.txt)
- **Terraform modules and examples:** [`terraform/modules/`](terraform/modules/), [`terraform/environments/`](terraform/environments/)
- **Platform surfaces:** [`platform/`](platform/), [`kustomize/`](kustomize/), [`helm-chart/`](helm-chart/), [`observability/`](observability/)
- **Tests / CI:** [`tests/`](tests/), [required](.github/workflows/required.yml), [platform-offline](.github/workflows/platform-offline.yml)
- **Authority / limitations:** [`docs/ARCHITECTURE.md#authority-model`](docs/ARCHITECTURE.md#authority-model)
- **Provenance / extraction history:** [`docs/PROVENANCE.md`](docs/PROVENANCE.md), [`docs/REPOSITORY_WIDE_EXTRACTION.md`](docs/REPOSITORY_WIDE_EXTRACTION.md), [`docs/TERRAFORM_COMPLETION.md`](docs/TERRAFORM_COMPLETION.md)

## Full local validation

The primary demo is intentionally fast. To reproduce the broader CI checks, use the commands in [`docs/EVIDENCE.md`](docs/EVIDENCE.md). Terraform initialization is always backend-disabled for review, provider tests are mocked, and no credentials are expected.
