#!/usr/bin/env python3
"""Fail closed when retained platform state gains live/application authority."""
from __future__ import annotations

import ipaddress
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOTS = [ROOT / name for name in ("platform", "kustomize", "helm-chart", "observability")]
EXECUTION_FILES = [
    ROOT / "scripts/backend_contract.py",
    ROOT / "scripts/validate_surfaces.py",
    ROOT / ".github/workflows/platform-offline.yml",
]
APP_NAMES = ("evidence-api", "edge-agent", "web-ui")
PROHIBITED_TEXT = {
    "embedded private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    "service-account email": re.compile(r"\b[^\s@]+@[^\s@]+\.iam\.gserviceaccount\.com\b", re.I),
    "private registry coordinate": re.compile(r"\.pkg\.dev/", re.I),
    "concrete WIF coordinate": re.compile(r"projects/[0-9]+/locations/global/workloadIdentityPools/", re.I),
    "source project coordinate": re.compile(r"\bproject-[0-9a-f]{8}(?:-[0-9a-f]{3,12}){2,5}\b", re.I),
}
EXECUTION_PATTERNS = {
    "GitHub OIDC write authority": re.compile(r"id-token\s*:\s*write", re.I),
    "GitHub-to-Google auth adapter": re.compile(r"google-github-actions/auth", re.I),
    "gcloud execution": re.compile(r"(?m)^\s*(?:run:\s*)?gcloud\s+", re.I),
    "Terraform live execution": re.compile(r"\bterraform\s+(?:plan|apply|import|destroy|state|force-unlock)\b", re.I),
    "kubectl mutation": re.compile(r"\bkubectl\s+(?:apply|create|delete|patch|replace|rollout|scale|set|exec|run)\b", re.I),
    "Helm mutation": re.compile(r"\bhelm\s+(?:install|upgrade|uninstall|rollback)\b", re.I),
    "Skaffold mutation": re.compile(r"\bskaffold\s+(?:run|deploy|dev|delete)\b", re.I),
    "gcp-ops command authority": re.compile(r"/gcp-ops\b", re.I),
}
IPV4 = re.compile(r"(?<![0-9])(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})(?:\.(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}(?![0-9])")


def asset_files() -> list[Path]:
    return sorted(path for root in ASSET_ROOTS for path in root.rglob("*") if path.is_file())


def yaml_docs(path: Path):
    return [document for document in yaml.safe_load_all(path.read_text(encoding="utf-8")) if document]


def main() -> int:
    failures: list[str] = []
    assets = asset_files()
    for path in assets + EXECUTION_FILES:
        if not path.is_file():
            failures.append(f"missing retained proof surface: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for label, pattern in PROHIBITED_TEXT.items():
            if pattern.search(text):
                failures.append(f"{rel}: {label}")
        for match in IPV4.finditer(text):
            value = ipaddress.ip_address(match.group(0))
            if value.is_global:
                failures.append(f"{rel}: globally routable IPv4 literal")
        if path in EXECUTION_FILES:
            for label, pattern in EXECUTION_PATTERNS.items():
                if pattern.search(text):
                    failures.append(f"{rel}: {label}")

    aggregate = "\n".join(path.read_text(encoding="utf-8") for path in assets)
    for name in APP_NAMES:
        if name in aggregate:
            failures.append(f"retained platform assets contain application topology name: {name}")
    if re.search(r"(?m)^\s*kind:\s*Ingress\s*$", aggregate):
        failures.append("retained platform assets contain application Ingress")

    # Parse concrete YAML (not Helm Go templates) and bound workload kinds.
    for root in (ROOT / "platform", ROOT / "kustomize", ROOT / "observability"):
        for path in root.rglob("*.yaml"):
            try:
                documents = yaml_docs(path)
            except yaml.YAMLError as exc:
                failures.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
                continue
            for document in documents:
                kind = document.get("kind")
                if kind not in {"Deployment", "Service"}:
                    continue
                metadata = document.get("metadata") or {}
                name = metadata.get("name") if isinstance(metadata, dict) else None
                if name != "otel-collector":
                    failures.append(f"{path.relative_to(ROOT)}: unsupported retained workload {kind}/{name}")

    if failures:
        print("platform authority violations:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("platform authority intact: retained state is credential-free, offline, and application-topology-free")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
