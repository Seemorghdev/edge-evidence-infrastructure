# Repository-wide Infrastructure extraction — Phase 7

Issue #21 expands Infrastructure ownership beyond Terraform into the reusable platform-state surfaces of the pinned Reference Platform. This wave is repository-only; it does not transfer Project 03 live authority.

## Pinned inputs

- Destination baseline: `fda277f9f69a7eaa095dd22266ea736e5c434d93`.
- Source commit: `403ee070fcf31120c3f715bc32bb1643b428f7d2`.
- Source root tree: `c4a810b4288ad1f4092224feea947cdfc357869e`.
- Accepted Phase 6 Terraform subset: 39 source files, source tree `74073fec6df9f3324313fc60739d77762c4ed4de`, staging inventory SHA-256 `708a3f27625efb6eb319750d1fae8b5207cf2ca7b06b68b50f50fd36a9356008`.
- Fresh Phase 7 non-Terraform/mixed inventory: 78 candidates.
- Repository-wide accounted source paths: **117**.

## Physical staging and publication safety

All **21 selected fresh source files** were physically materialized outside destination Git before modification. Every staged byte stream reproduced its pinned source Git blob SHA. The deterministic fresh staging inventory SHA-256 is `861395ff5961602ea985e52cbff46f928a074283e1cfdaa1236994d11fcf2512`. Raw unsanitized source bytes were not committed.

Literal public-safe primitives remain byte-identical: the namespace and NEG annotation pattern, reusable Kustomize network-policy/OTel/Istio components, standalone OTel config, Helm chart/helper/Istio/OTel plumbing, the observability overlay, and the thin deployment-surface test. Mixed files are retained only after bounded removal of application or Operations coupling.

## Ownership boundary

Reference Platform retains application Deployments/Services/config, application ingress routes, local/dev overlays, load-generator composition, Skaffold application orchestration, and application Helm templates. Operations retains authorization, WIF consumption, credentials, live provider readback, Terraform plan/apply/bootstrap, GKE credentials, cluster mutation, workload deploy, publication, verification/evidence and rollback semantics.

The pure backend bucket contract parser is the deliberate mixed-file exception: its schema normalization and policy comparison are retained in `scripts/backend_contract.py`; the source runner's `gcloud`, credential, state/evidence, retry and mutation code is not.

## Deterministic proof

`docs/infrastructure-discovery-snapshot.json` pins the discovery rules and every mandatory non-Terraform candidate family. `docs/infrastructure-source-manifest.json` classifies each of those 78 candidates exactly once and references the accepted 39-file Phase 6 Terraform manifest. `scripts/check_infrastructure_manifest.py` fails closed on omissions, duplicate accounting, wrong pinned hashes, broken literal identity, unbounded modified-file identity, or missing Phase 6 accounting.

`python scripts/check_platform_authority.py` scans the retained platform surfaces for live execution/auth/state/application authority. `python scripts/validate_surfaces.py` validates the retained YAML/JSON/Kustomize/Helm/OTel structures without cluster access. CI remains credential-free and read-only.

No Terraform live plan/apply/import/destroy, backend migration, provider read/write, WIF/OIDC consumption, credential acquisition, `gcloud`, `kubectl`/Helm/Skaffold deployment, cluster/workload mutation, DNS/TLS/address mutation, GitHub command authority, publication, source deletion, or authority cutover is authorized by this repository.
