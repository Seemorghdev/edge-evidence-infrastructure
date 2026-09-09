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

The initial **21 selected fresh source files** were physically materialized outside destination Git before modification. Every staged byte stream reproduced its pinned source Git blob SHA. The deterministic initial staging inventory SHA-256 is `861395ff5961602ea985e52cbff46f928a074283e1cfdaa1236994d11fcf2512`.

Reviewer A's retention-first repair selected two additional mixed helpers. Their pinned source bytes were materialized in temporary worker storage before adaptation and matched source blobs `e62ddadc974e1038190711c43c1da3b2a9e47f8d` (`scripts/check_authority_boundary.py`) and `66ae0ea48ecea64d3b31c36c8a85c04b05d298b6` (`scripts/run_heavy_validation.sh`). The deterministic repair staging inventory SHA-256 over sorted `source_path<TAB>source_blob_sha` records is `28ab7c99782277b43196f5036920468edf1c0681dd7d649e09da2297d77427f1`. The combined selected set is therefore **23 source files**. Raw unsanitized source bytes were not committed.

Literal public-safe primitives remain byte-identical: the namespace and NEG annotation pattern, reusable Kustomize network-policy/OTel/Istio components, standalone OTel config, Helm chart/helper/Istio/OTel plumbing, the observability overlay, and the thin deployment-surface test. Mixed files are retained only after bounded removal of application or Operations coupling.

## Retained mixed validation helpers

`scripts/run_heavy_validation.sh` is source-derived from blob `66ae0ea48ecea64d3b31c36c8a85c04b05d298b6`. Destination blob `e7734f548a14dffb15400f85959cb7d6ebdf5e14` / SHA-256 `dbe5f95fd449c37719e1ede481491dd0b81eef794d0d0b75e49b51a65558c4ce` preserves the source error/resource-report structure plus `phase_kubernetes` and `phase_terraform`. Application package/devcontainer/Compose/component-proof phases, local/dev overlays, Skaffold application orchestration, source Cloud Run composition, synthetic access-token transport, and Terraform plan behavior are removed. The retained Kubernetes phase performs only Helm lint/template and Kustomize build; the retained Terraform phase performs fmt, backend-disabled init, validate, and native mocked tests over accepted roots.

`scripts/check_platform_authority.py` is source-derived from `scripts/check_authority_boundary.py` blob `e62ddadc974e1038190711c43c1da3b2a9e47f8d`. Destination blob `31ba46725f75895118b9bacffa046eb51c729097` / SHA-256 `2ae49c54c03ed75b4c33a0b28dc9a40ff514870e099dee8023dfa240ce8e2ac0` preserves scan-root iteration, prohibited-pattern scanning, backend validation, resource-type checking, and fail-closed aggregation. Project03/private-probe/gcp-ops allowlists and live bucket/prefix constants are replaced by the accepted destination Terraform root/resource inventory, empty externally configured GCS backend checks, retained platform topology checks, and no-live-execution checks.

`scripts/select_heavy_validation.py` remains unretained for a concrete destination reason: both source-derived Infrastructure heavy phases are run unconditionally on every PR/push by `required` and `platform-offline`. Retaining the Travis path selector would reduce coverage and would also carry application-only package/devcontainer/Compose/proof routing that has no destination role.

## Ownership boundary

Reference Platform retains application Deployments/Services/config, application ingress routes, local/dev overlays, load-generator composition, Skaffold application orchestration, and application Helm templates. Operations retains authorization, WIF consumption, credentials, live provider readback, Terraform plan/apply/bootstrap, GKE credentials, cluster mutation, workload deploy, publication, verification/evidence and rollback semantics.

The pure backend bucket contract parser is the deliberate mixed-file exception: its schema normalization and policy comparison are retained in `scripts/backend_contract.py`; the source runner's `gcloud`, credential, state/evidence, retry and mutation code is not.

## Deterministic proof

`docs/infrastructure-discovery-snapshot.json` pins the discovery rules and every mandatory non-Terraform candidate family. `docs/infrastructure-source-manifest.json` classifies each of those 78 candidates exactly once and references the accepted 39-file Phase 6 Terraform manifest. `scripts/check_infrastructure_manifest.py` fails closed on omissions, duplicate accounting, wrong pinned hashes, broken literal identity, unbounded modified-file identity, missing staging proof, or missing Phase 6 accounting.

`python scripts/check_platform_authority.py` uses the source-derived authority-scanning structure to reject live execution/auth/state/application authority. `python scripts/validate_surfaces.py` validates retained YAML/JSON/Kustomize/Helm/OTel structures without cluster access. CI invokes the source-derived heavy helper directly for Kubernetes rendering and Terraform offline validation.

No Terraform live plan/apply/import/destroy, backend migration, provider read/write, WIF/OIDC consumption, credential acquisition, `gcloud`, `kubectl`/Helm/Skaffold deployment, cluster/workload mutation, DNS/TLS/address mutation, GitHub command authority, publication, source deletion, or authority cutover is authorized by this repository.
