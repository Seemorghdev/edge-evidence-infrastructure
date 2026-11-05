# Edge Evidence Infrastructure

Reusable desired-state cloud and platform infrastructure for the Edge Evidence portfolio, for engineers reviewing infrastructure contracts without granting this repository live cloud authority.

**Status.** Built: Terraform modules, offline examples and reusable platform assets. Evidence: the `required`, `platform-offline` and `devcontainer-smoke` workflows passed on 10 September 2026 at `092a205`. Limits: these are desired-state definitions and offline checks, not a live deployment or cloud execution plane. Existing live environment, application, and operational authority remains separately governed.

## Quick-start

Needs Python 3.12 or 3.13 and pip. From a fresh clone:

```bash
python3 -m venv .venv
export PATH="$PWD/.venv/bin:$PATH"
python3 -m pip install "PyYAML>=6,<7"
python3 scripts/portfolio_demo.py
python3 -m unittest discover -s tests -v
```

The demo prints `RESULT: PASS` when its offline checks complete. It does not authenticate to cloud services or perform live infrastructure actions.

## Tests

Run `python3 -m unittest discover -s tests -v`: 17 tests passed locally on Python 3.12.13. The latest default-branch runs of the three workflows below passed on the recorded base. CI invokes `python scripts/portfolio_demo.py` in its configured Python environment.

## How it fits

This is the infrastructure layer for [Edge Evidence](https://mehridian.tech/projects/edge-evidence). It keeps reusable desired-state contracts separate from live execution. Start with [the architecture](docs/ARCHITECTURE.md), [demo and evidence](docs/DEMO.md), [claim-to-proof mapping](docs/EVIDENCE.md), [provenance](docs/PROVENANCE.md), or the [full portfolio overview](docs/portfolio-overview.md).

- Terraform: [`terraform/modules/`](terraform/modules/) and [`terraform/environments/`](terraform/environments/)
- Platform assets: [`platform/`](platform/), [`kustomize/`](kustomize/), [`helm-chart/`](helm-chart/), [`observability/`](observability/)
- Validation: [`scripts/`](scripts/) and [`tests/`](tests/)
- CI: [required](.github/workflows/required.yml), [platform-offline](.github/workflows/platform-offline.yml), [devcontainer-smoke](.github/workflows/devcontainer-smoke.yml)

## Licence

Apache-2.0. See [`LICENSE`](LICENSE).
