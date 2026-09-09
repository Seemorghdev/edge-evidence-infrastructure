#!/usr/bin/env python3
"""Fail when retained Infrastructure surfaces cross the bounded authority contract."""

from __future__ import annotations

import ipaddress
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (
    ROOT / "platform",
    ROOT / "kustomize",
    ROOT / "helm-chart",
    ROOT / "observability",
    ROOT / "terraform",
)
EXECUTION_FILES = (
    ROOT / "scripts" / "run_heavy_validation.sh",
    ROOT / ".github" / "workflows" / "required.yml",
    ROOT / ".github" / "workflows" / "platform-offline.yml",
)
TEXT_SUFFIXES = {".py", ".sh", ".yaml", ".yml", ".json", ".tf", ".tpl", ".toml", ".md"}
PROHIBITED = {
    "embedded private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential assignment": re.compile(
        r"(?im)^\s*(?:aws_secret_access_key|google_credentials|client_secret|private_key)"
        r"\s*=\s*[\"'][^<\n][^\n]*"
    ),
    "public Kubernetes load balancer": re.compile(r"(?im)^\s*type:\s*LoadBalancer\s*$"),
    "public principal assignment": re.compile(
        r"(?im)^\s*(?:member|members)\s*[:=].*\b(?:allUsers|allAuthenticatedUsers)\b"
    ),
    "hard-coded public Cloud Run ingress": re.compile(
        r'(?im)^\s*ingress\s*=\s*"INGRESS_TRAFFIC_ALL"\s*$'
    ),
    "public invoker bypass": re.compile(r"(?im)^\s*invoker_iam_disabled\s*=\s*true\s*$"),
    "private registry coordinate": re.compile(r"\.pkg\.dev/", re.I),
    "concrete WIF coordinate": re.compile(
        r"projects/[0-9]+/locations/global/workloadIdentityPools/", re.I
    ),
}
EXECUTION_PROHIBITED = {
    "GitHub OIDC write authority": re.compile(r"id-token\s*:\s*write", re.I),
    "GitHub-to-Google auth adapter": re.compile(r"google-github-actions/auth", re.I),
    "gcloud execution": re.compile(r"(?m)^\s*(?:run:\s*)?gcloud\s+", re.I),
    "Terraform live execution": re.compile(
        r"\bterraform\s+(?:plan|apply|import|destroy|state|force-unlock)\b", re.I
    ),
    "kubectl mutation": re.compile(
        r"\bkubectl\s+(?:apply|create|delete|patch|replace|rollout|scale|set|exec|run)\b",
        re.I,
    ),
    "Helm mutation": re.compile(r"\bhelm\s+(?:install|upgrade|uninstall|rollback)\b", re.I),
    "Skaffold mutation": re.compile(r"\bskaffold\s+(?:run|deploy|dev|delete)\b", re.I),
    "gcp-ops command authority": re.compile(r"/gcp-ops\b", re.I),
}
APP_NAMES = ("evidence-api", "edge-agent", "web-ui")
STATE_BACKEND = re.compile(r'(?m)^\s*backend\s+"([^"]+)"')
BACKEND_COORDINATE = re.compile(r"(?m)^\s*(?:bucket|prefix|credentials)\s*=")
RESOURCE = re.compile(r'(?m)^\s*resource\s+"([^"]+)"')
IPV4 = re.compile(
    r"(?<![0-9])(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})"
    r"(?:\.(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}(?![0-9])"
)

TERRAFORM_RESOURCE_ALLOWLIST = {
    ROOT / "terraform/modules/gke-autopilot-cluster": {"google_container_cluster"},
    ROOT / "terraform/environments/gke-autopilot": set(),
    ROOT / "terraform/modules/cloud-run-service": {"google_cloud_run_v2_service"},
    ROOT / "terraform/environments/cloud-run-service-example": set(),
    ROOT / "terraform/environments/gke-exposure-address": {"google_compute_global_address"},
    ROOT / "terraform/environments/github-ops-wif": {
        "google_project_service",
        "google_service_account",
        "google_iam_workload_identity_pool",
        "google_iam_workload_identity_pool_provider",
        "google_service_account_iam_member",
        "google_project_iam_member",
    },
    ROOT / "terraform/modules/private-cloud-run-workflow": {
        "google_service_account",
        "google_workflows_workflow",
        "google_cloud_run_v2_service_iam_member",
    },
    ROOT / "terraform/environments/private-cloud-run-workflow-example": set(),
}
EXTERNALLY_CONFIGURED_BACKEND_ROOTS = {
    ROOT / "terraform/environments/gke-autopilot",
    ROOT / "terraform/environments/gke-exposure-address",
    ROOT / "terraform/environments/github-ops-wif",
    ROOT / "terraform/environments/private-cloud-run-workflow-example",
}


def iter_files():
    for root in SCAN_ROOTS:
        if root.is_file():
            yield root
        elif root.exists():
            for path in root.rglob("*"):
                if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name == "Dockerfile"):
                    yield path


def is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def allowed_cloud_resources(path: Path) -> set[str]:
    for root, allowed in TERRAFORM_RESOURCE_ALLOWLIST.items():
        if is_within(path, root):
            return allowed
    return set()


def reviewed_backend_root(path: Path) -> Path | None:
    for root in EXTERNALLY_CONFIGURED_BACKEND_ROOTS:
        if is_within(path, root):
            return root
    return None


def check_state_backend(path: Path, text: str, failures: list[str]) -> None:
    backends = STATE_BACKEND.findall(text)
    if not backends:
        return
    if reviewed_backend_root(path) is None:
        failures.append(f"{path.relative_to(ROOT)}: state backend outside reviewed environment")
        return
    if backends != ["gcs"]:
        failures.append(f"{path.relative_to(ROOT)}: unsupported state backend {backends!r}")
    if BACKEND_COORDINATE.search(text):
        failures.append(f"{path.relative_to(ROOT)}: live backend coordinate")


def main() -> int:
    failures: list[str] = []
    scanned = list(iter_files())
    for path in scanned:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for label, pattern in PROHIBITED.items():
            if pattern.search(text):
                failures.append(f"{rel}: {label}")
        for match in IPV4.finditer(text):
            if ipaddress.ip_address(match.group(0)).is_global:
                failures.append(f"{rel}: globally routable IPv4 literal")
        check_state_backend(path, text, failures)
        if path.suffix == ".tf":
            allowed = allowed_cloud_resources(path)
            for resource_type in RESOURCE.findall(text):
                if resource_type.startswith(("google_", "aws_", "azurerm_")) and resource_type not in allowed:
                    failures.append(f"{rel}: unsupported cloud resource {resource_type}")

    for path in EXECUTION_FILES:
        if not path.is_file():
            failures.append(f"missing retained proof surface: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for label, pattern in EXECUTION_PROHIBITED.items():
            if pattern.search(text):
                failures.append(f"{rel}: {label}")

    asset_roots = (ROOT / "platform", ROOT / "kustomize", ROOT / "helm-chart", ROOT / "observability")
    aggregate = "\n".join(
        path.read_text(encoding="utf-8")
        for root in asset_roots
        for path in root.rglob("*")
        if path.is_file()
    )
    for name in APP_NAMES:
        if name in aggregate:
            failures.append(f"retained platform assets contain application topology name: {name}")
    if re.search(r"(?m)^\s*kind:\s*Ingress\s*$", aggregate):
        failures.append("retained platform assets contain application Ingress")

    if failures:
        print("authority boundary violations:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(
        "authority boundary intact: retained platform state and source-derived validation "
        "remain credential-free, offline, application-topology-free, and fail closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
