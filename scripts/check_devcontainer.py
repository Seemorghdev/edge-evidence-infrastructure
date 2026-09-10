#!/usr/bin/env python3
"""Fail closed on the credential-free Codespaces evaluator contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".devcontainer/devcontainer.json"
DOCKERFILE = ROOT / ".devcontainer/Dockerfile"
WORKFLOW = ROOT / ".github/workflows/devcontainer-smoke.yml"
README = ROOT / "README.md"
DEMO_DOC = ROOT / "docs/DEMO.md"

EXPECTED_CONFIG_KEYS = {"name", "build", "features", "remoteUser"}
DOCKER_FEATURE = "ghcr.io/devcontainers/features/docker-in-docker:4"
EXPECTED_DOCKER_OPTIONS = {
    "version": "latest",
    "moby": True,
    "dockerDashComposeVersion": "none",
    "installDockerBuildx": False,
    "installDockerComposeSwitch": False,
}

PROHIBITED = {
    "Google Cloud CLI execution": re.compile(r"(?m)^\s*(?:run:\s*)?gcloud\s+", re.I),
    "Google auth action": re.compile(r"google-github-actions/auth", re.I),
    "OIDC write permission": re.compile(r"id-token\s*:\s*write", re.I),
    "Terraform live action": re.compile(
        r"\bterraform\s+(?:plan|apply|import|destroy|state|force-unlock)\b", re.I
    ),
    "kubectl mutation": re.compile(
        r"\bkubectl\s+(?:apply|create|delete|patch|replace|rollout|scale|set|exec|run)\b",
        re.I,
    ),
    "Helm mutation": re.compile(
        r"\bhelm\s+(?:install|upgrade|uninstall|rollback)\b", re.I
    ),
    "Skaffold mutation": re.compile(r"\bskaffold\s+(?:run|deploy|dev|delete)\b", re.I),
    "gcp-ops command authority": re.compile(r"/gcp-ops\b", re.I),
    "GitHub Actions secret reference": re.compile(r"\bsecrets\.", re.I),
    "provider credential transport": re.compile(
        r"\b(?:access_token|impersonate_service_account)\b", re.I
    ),
}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    for path in (CONFIG, DOCKERFILE, WORKFLOW, README, DEMO_DOC):
        require(path.is_file(), f"missing evaluator surface: {path.relative_to(ROOT)}", failures)
    if failures:
        return report(failures)

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    require(set(config) == EXPECTED_CONFIG_KEYS, "devcontainer top-level surface drift", failures)
    require(
        config.get("build") == {"dockerfile": "Dockerfile"},
        "devcontainer must build only .devcontainer/Dockerfile",
        failures,
    )
    require(config.get("remoteUser") == "vscode", "devcontainer remoteUser must remain vscode", failures)
    features = config.get("features")
    require(
        isinstance(features, dict) and set(features) == {DOCKER_FEATURE},
        "devcontainer must contain only the Docker-in-Docker feature",
        failures,
    )
    if isinstance(features, dict) and DOCKER_FEATURE in features:
        require(
            features[DOCKER_FEATURE] == EXPECTED_DOCKER_OPTIONS,
            "Docker-in-Docker options drifted from evaluator-only contract",
            failures,
        )

    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    for required in (
        "FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm",
        "ARG TERRAFORM_VERSION=1.9.8",
        "186e0145f5e5f2eb97cbd785bc78f21bae4ef15119349f6ad4fa535b83b10df8",
        "f85868798834558239f6148834884008f2722548f84034c9b0f62934b2d73ebb",
        '"PyYAML>=6,<7"',
        '"pytest>=8,<9"',
        "sha256sum -c -",
    ):
        require(required in dockerfile, f"Dockerfile evaluator invariant missing: {required}", failures)

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "uses: devcontainers/ci@v0.3\n"
        "        with:\n"
        "          inheritEnv: false\n"
        "          push: never\n" in workflow,
        "devcontainer smoke must explicitly disable image publication with push: never",
        failures,
    )
    require(
        re.search(r"(?mi)^\s*imageName\s*:", workflow) is None,
        "devcontainer smoke must not configure an imageName publication target",
        failures,
    )
    for required in (
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "uses: devcontainers/ci@v0.3",
        "inheritEnv: false",
        'for tool in gcloud kubectl helm kustomize skaffold; do ! command -v "$tool"; done',
        'test -z "${GOOGLE_APPLICATION_CREDENTIALS:-}"',
        'test -z "${CLOUDSDK_CONFIG:-}"',
        'test -z "${GOOGLE_CLOUD_PROJECT:-}"',
        "python scripts/portfolio_demo.py",
        "python scripts/check_infrastructure_manifest.py",
        "python scripts/check_platform_authority.py",
        "python scripts/validate_surfaces.py",
        "python scripts/check_portfolio.py",
        "python scripts/check_devcontainer.py",
        "python -m unittest discover -s tests -v",
        "bash scripts/run_heavy_validation.sh terraform",
        "bash scripts/run_heavy_validation.sh kubernetes",
    ):
        require(required in workflow, f"devcontainer smoke invariant missing: {required}", failures)

    scan_text = "\n".join((CONFIG.read_text(encoding="utf-8"), dockerfile, workflow))
    for label, pattern in PROHIBITED.items():
        if pattern.search(scan_text):
            failures.append(f"evaluator surface contains prohibited authority: {label}")

    readme = README.read_text(encoding="utf-8")
    demo_doc = DEMO_DOC.read_text(encoding="utf-8")
    require("python scripts/portfolio_demo.py" in readme, "README lost primary demo command", failures)
    require("## Codespaces evaluator" in demo_doc, "demo docs missing Codespaces evaluator section", failures)

    if failures:
        return report(failures)
    print(
        "devcontainer evaluator policy passed: Python 3.12 + Terraform 1.9.8 + "
        "Docker-backed offline validation, with no live/cloud authority configured"
    )
    return 0


def report(failures: list[str]) -> int:
    print("devcontainer evaluator policy FAILED", file=sys.stderr)
    for failure in failures:
        print(f"- {failure}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
