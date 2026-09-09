# Offline portfolio demo

The primary reviewer entry point is:

```bash
python scripts/portfolio_demo.py
```

It is intentionally small, deterministic, and credential-free. It uses only Python's standard library, Git metadata from the checkout, checked-in repository assets, and existing validation logic.

## What it proves

The script runs three accepted repository checks as subprocesses and treats any non-zero result as a demo failure:

1. `scripts/check_terraform_completion.py` — accepted Terraform product/source accounting.
2. `scripts/check_infrastructure_manifest.py` — repository-wide retained-source/provenance accounting.
3. `scripts/check_policy.py` — Terraform authority and publication-safety invariants.

It then verifies that representative Kubernetes/Kustomize/Helm/OpenTelemetry primitives are present and exercises `scripts/backend_contract.py` with a fully synthetic bucket payload.

The script does **not** run Terraform, contact a provider, read a backend, request credentials, exchange an OIDC/WIF token, call a Kubernetes API, or render/deploy through live Helm/Skaffold.

## Expected output

The successful output contract is checked into [`examples/portfolio-demo.txt`](examples/portfolio-demo.txt) and CI verifies byte-for-byte equality:

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

A failure returns a non-zero exit code and names the failed stage.

## Deeper validation

The demo is a fast review path, not a replacement for CI. The complete Terraform and platform checks are listed in [`EVIDENCE.md`](EVIDENCE.md) and run in `.github/workflows/required.yml` plus `.github/workflows/platform-offline.yml`.
