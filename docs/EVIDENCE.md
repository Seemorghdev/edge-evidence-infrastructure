# Evidence and validation

This document maps portfolio-facing claims to concrete repository evidence. All commands below are repository-only and credential-free unless explicitly described as an architectural boundary.

## Primary evidence

```bash
python scripts/portfolio_demo.py
```

Expected output is versioned at [`examples/portfolio-demo.txt`](examples/portfolio-demo.txt).

| Claim | Evidence |
| --- | --- |
| Terraform products have bounded resource inventories and safe defaults | Terraform-native mocked tests under each module/environment; `scripts/check_policy.py` |
| Repository source/retention accounting is deterministic | `scripts/check_terraform_completion.py`; `scripts/check_infrastructure_manifest.py` |
| Platform assets are reusable and application-topology-free | `scripts/check_platform_authority.py`; `scripts/validate_surfaces.py`; `tests/test_deployment_surfaces.py` |
| Backend contract logic is pure and credential-free | `scripts/backend_contract.py`; `tests/test_backend_contract.py`; synthetic demo payload |
| Demo and recruiter-facing docs stay reproducible/sanitized | `scripts/check_portfolio.py`; `tests/test_portfolio.py` |
| No live authority is exercised by CI | workflow permissions, backend-disabled init, mocked provider tests, authority-policy scans |

## Synthetic backend contract example

The demo supplies an in-memory payload with:

```json
{
  "name": "example-state-bucket",
  "location": "us-central1",
  "default_storage_class": "STANDARD",
  "uniform_bucket_level_access": true,
  "public_access_prevention": "enforced",
  "versioning_enabled": true,
  "soft_delete_policy": {
    "retentionDurationSeconds": "604800"
  }
}
```

`bucket_contract(...)` normalizes that payload and returns:

```text
ready=True
drift=[]
```

No provider is queried; the parser accepts already-observed data only.

## Terraform validation

CI pins Terraform 1.9.8. Representative local review commands are:

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
```

Module-native lanes additionally validate/test `terraform/modules/cloud-run-service` and `terraform/modules/private-cloud-run-workflow` with backend-disabled, credential-free initialization.

All Terraform test provider interactions are mocked. One private-workflow test uses Terraform's mocked `apply` command only to resolve synthetic computed values; it performs no GCP operation.

## Platform validation

The source-derived platform lane runs safe Helm lint/template and Kustomize build operations without a cluster:

```bash
bash scripts/run_heavy_validation.sh kubernetes
```

Python structural/authority checks are:

```bash
python scripts/check_platform_authority.py
python scripts/validate_surfaces.py
python -m pytest -q tests/test_deployment_surfaces.py tests/test_backend_contract.py
```

`platform-offline` runs these on Python 3.12 and 3.13.

## Portfolio/readiness checks

```bash
python scripts/check_portfolio.py
python -m unittest discover -s tests -v
```

The portfolio checker verifies:

- README navigation and the exact demo command;
- relative Markdown links in recruiter-facing docs;
- deterministic example output;
- no private/live coordinate or credential patterns in docs/examples;
- no live-authority command surface in the primary demo.

## Interpreting the evidence

Passing these checks means the repository's **desired-state definitions and offline safety contracts** are internally consistent at that commit.

It does not mean a live environment was provisioned, that current live state is owned here, or that cloud/Kubernetes operational behavior was exercised. Those actions remain separately authorized and are intentionally outside this portfolio repository.
