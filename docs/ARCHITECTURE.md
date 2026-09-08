# Architecture and authority boundary

## Product responsibility

This repository defines reusable provider/platform **desired state**. It does not contain an execution plane.

The repository contains five accepted Terraform desired-state products plus a repository-wide platform-state layer:

1. `terraform/modules/gke-autopilot-cluster` plus `terraform/environments/gke-autopilot` — one guarded GKE Autopilot cluster with deployment coordinates and backend configuration supplied externally;
2. `terraform/modules/cloud-run-service` plus `terraform/environments/cloud-run-service-example` — one reusable Cloud Run v2 service contract and a credential-free, single-service example composition;
3. `terraform/environments/gke-exposure-address` — one guarded global external IPv4 resource contract with project, name, labels, and optional desired address supplied by the caller;
4. `terraform/environments/github-ops-wif` — generic GitHub Actions OIDC trust provisioning: required bootstrap APIs, one operations service account, one WIF pool/provider, one repository-ID-scoped impersonation binding, and optional bounded project roles;
5. `terraform/modules/private-cloud-run-workflow` plus `terraform/environments/private-cloud-run-workflow-example` — one generic workflow service account, one Google Workflow resource, and zero or more bounded Cloud Run `roles/run.invoker` IAM bindings;
6. `platform/`, reusable `kustomize/` components, retained platform-only Helm templates, and `observability/` — namespace, NEG annotation, network-policy, Istio mTLS/namespace-injection, and OpenTelemetry desired-state/rendering primitives.

The GKE module assumes an existing project, VPC network, and subnetwork. It deliberately does not create networks, APIs, IAM, WIF, node pools, Kubernetes application workloads, Helm releases, DNS, certificates, or public addresses. Its accepted Phase-1 contract keeps Autopilot enabled, deletion protection and Terraform `prevent_destroy` enabled, and network, subnetwork, and release-channel selections caller-controlled.

The Cloud Run module assumes an existing project and accepts only resource-level desired-state inputs: region, service name, immutable image digest, container port, non-secret environment values, health path, ingress, deletion protection, and bounded scaling/resource settings. Internal-only ingress and deletion protection are defaults. The module owns no service account, IAM grant, API enablement, VPC, DNS, certificate, scheduler, WIF trust, provider credential, public-principal policy, or application topology.

The Cloud Run example composes exactly one generic service with synthetic test coordinates. It has no remote backend binding and its tests mock the Google provider, so repository validation requires no cloud credentials.

The global-address environment preserves only the reviewed resource shape: exactly one `google_compute_global_address`, `EXTERNAL`/`IPV4`, and Terraform `prevent_destroy`. It carries no live Project 03 address or project coordinate. Its desired-address input defaults to `null`; its GCS backend declaration is empty and externally configured; its tests use only a mocked provider and documentation-only synthetic input. The environment does not read, import, migrate, adopt, promote, or bind existing state.

The GitHub WIF environment owns **provisioning desired state only**. It maps reviewed GitHub OIDC claims and constructs a fail-closed condition from required caller-supplied repository name/ID, owner ID, workflow ref, branch ref, event, and visibility. Project roles are an explicit bounded set and default to empty. The root carries no current live trust coordinate, backend coordinate, access-token transport, credential file, GitHub token, consumer workflow, or provider-authenticated action. Provisioning definitions do not authorize consumption or migrate existing trust.

The private Cloud Run workflow module owns only the provider/platform provisioning relationship retained from the source private-probe graph: one workflow service account, one Google Workflow resource, and bounded Cloud Run service IAM members. Target service identities are explicit caller inputs; missing target locations inherit the workflow region. No provider service lookup is retained, and target URIs are neither read nor output. `roles/run.invoker` is fixed in module code and cannot be selected by callers.

Workflow source contents are a required bounded caller input because the provider requires source on the workflow resource. Infrastructure does not define or interpret that source as execution policy. The example supplies an inert synthetic workflow that only returns a synthetic value. The source `workflow.yaml.tpl` program, application routes, HTTP methods, authenticated probe behavior, retry/error semantics, and evidence logic remain outside Infrastructure ownership. The source workflow's `deletion_protection = false` is retained to minimize semantic transformation; repository approval still grants no deletion, adoption, or provider execution authority.

## Platform-state layer

Phase 7 expands Infrastructure ownership beyond Terraform without transferring application deployment authority. The retained Kubernetes/Kustomize/Helm/observability layer is intentionally primitive and reusable:

- a namespace desired-state manifest;
- a generic GKE NEG annotation patch, detached from the source application Ingress route;
- default-deny plus same-platform network policy;
- OpenTelemetry collector configuration and optional collector Deployment/Service plumbing;
- Istio namespace injection and STRICT `PeerAuthentication` mTLS;
- Kustomize component/overlay relationships and Helm helper/toggle templates needed to render those primitives.

No application Deployment, application Service, application Ingress route, live address binding, load generator, local/dev application overlay, or Skaffold deployment orchestration is retained. `scripts/validate_surfaces.py` and the platform policy checks validate these assets without cluster access.

The backend bucket parser retained in `scripts/backend_contract.py` is a pure contract-normalization helper extracted from a mixed Operations bootstrap file. It accepts already-observed payloads as input and contains no provider read, credential, subprocess, state, retry, or mutation behavior.

## Transitional authority

The copy/generalize phase does not transfer live authority. `Seemorghdev/edge-evidence-reference-platform` remains the active Project 03 source of truth for state, accepted operational evidence, repository-bound execution controls, live provider relationships, the existing external address, current workflow/application behavior, current Kubernetes application topology, and current WIF/trust relationships.

A future cutover would require separate review of destination CI parity, state/backend ownership, trust identity, workflow identity, Kubernetes deployment ownership, provenance, and operational authority. None of those are implied by the current extraction phases.

## Infrastructure versus Operations

Infrastructure answers: **what provider/platform state should exist?**

Operations answers: **which reviewed actor may inspect, execute, or change that state, by which exact procedure, and what evidence must be retained?**

Accordingly this repository may define generic WIF provisioning resources, a generic Workflow resource, and inert Kubernetes/Helm/Kustomize desired-state assets, but contains no GitHub issue listener, `/gcp-ops` router, OIDC/WIF consumer workflow, token exchange, command history, workflow runtime procedure, retry/rollback policy, runbook executor, provider credentials, cluster credential acquisition, `kubectl apply`, Helm install/upgrade, Skaffold deploy, or evidence-retention workflow.

## Application boundary

Reference Platform retains concrete application services and contracts: service names, application routes, workload identities, real image coordinates, application-specific port/probe choices, environment values, same-origin behavior, local composition, application Kubernetes Deployments/Services/Ingress, application Helm templates, load-generator/Skaffold composition, and current private-probe target composition.

Infrastructure owns generic provider/platform resource contracts and reusable platform primitives plus their validation rules. Supplying a port, health path, environment map, immutable image reference, project, address name, labels, optional desired address, generic WIF trust coordinates, workflow source, generic Cloud Run service identity, namespace, policy, mesh, NEG, or observability configuration does not transfer ownership of application behavior, operational execution, or existing live provider state represented by those values.
