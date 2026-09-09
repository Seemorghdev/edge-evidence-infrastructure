#!/usr/bin/env python3
"""Deterministic, credential-free reviewer demo for the Infrastructure product."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from backend_contract import bucket_contract  # noqa: E402

VALIDATORS = (
    ("Terraform desired-state audit", "check_terraform_completion.py"),
    ("Repository-wide manifest audit", "check_infrastructure_manifest.py"),
    ("Authority/publication policy", "check_policy.py"),
)

PLATFORM_PRIMITIVES = (
    ROOT / "platform/kubernetes/namespace.yaml",
    ROOT / "platform/kubernetes/neg/service-neg-patch.json",
    ROOT / "kustomize/components/network-policies/policies.yaml",
    ROOT / "kustomize/components/service-mesh-istio/peer-authentication.yaml",
    ROOT / "kustomize/components/observability-otel/otel-collector.yaml",
    ROOT / "helm-chart/edge-evidence-platform/templates/istio.yaml",
    ROOT / "helm-chart/edge-evidence-platform/templates/otel-collector.yaml",
    ROOT / "observability/otel-collector-config.yaml",
)

SUCCESS_OUTPUT = """Edge Evidence Infrastructure — offline review
[PASS] Terraform desired-state audit
[PASS] Repository-wide manifest audit
[PASS] Authority/publication policy
[PASS] Retained platform primitives (Kubernetes, Kustomize, Helm, OpenTelemetry)
[PASS] Synthetic backend contract (uniform access, public-access prevention, versioning, soft delete)
[PASS] Live authority: not requested or exercised
RESULT: PASS — credential-free desired-state validation completed
"""


def run_validator(script_name: str) -> tuple[bool, str]:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / script_name)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    detail = (completed.stderr or completed.stdout).strip().splitlines()
    return completed.returncode == 0, (detail[0] if detail else "no diagnostic")


def synthetic_backend_is_safe() -> bool:
    payload = {
        "name": "example-state-bucket",
        "location": "us-central1",
        "default_storage_class": "STANDARD",
        "uniform_bucket_level_access": True,
        "public_access_prevention": "enforced",
        "versioning_enabled": True,
        "soft_delete_policy": {"retentionDurationSeconds": "604800"},
    }
    ready, drift = bucket_contract(
        payload,
        expected_name="example-state-bucket",
        expected_location="us-central1",
    )
    return ready and drift == []


def main() -> int:
    lines = ["Edge Evidence Infrastructure — offline review"]

    for label, script_name in VALIDATORS:
        ok, detail = run_validator(script_name)
        if not ok:
            lines.append(f"[FAIL] {label}: {detail}")
            print("\n".join(lines))
            return 1
        lines.append(f"[PASS] {label}")

    missing = [
        path.relative_to(ROOT).as_posix()
        for path in PLATFORM_PRIMITIVES
        if not path.is_file()
    ]
    if missing:
        lines.append(f"[FAIL] Retained platform primitives missing: {', '.join(missing)}")
        print("\n".join(lines))
        return 1
    lines.append(
        "[PASS] Retained platform primitives "
        "(Kubernetes, Kustomize, Helm, OpenTelemetry)"
    )

    if not synthetic_backend_is_safe():
        lines.append("[FAIL] Synthetic backend contract")
        print("\n".join(lines))
        return 1
    lines.append(
        "[PASS] Synthetic backend contract "
        "(uniform access, public-access prevention, versioning, soft delete)"
    )

    lines.append("[PASS] Live authority: not requested or exercised")
    lines.append("RESULT: PASS — credential-free desired-state validation completed")
    output = "\n".join(lines) + "\n"
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
