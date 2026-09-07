#!/usr/bin/env python3
"""Offline Phase-1 authority and publication-safety checks."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TF_ROOT = ROOT / "terraform"
ENV_ROOT = TF_ROOT / "environments" / "gke-autopilot"
MODULE_ROOT = TF_ROOT / "modules" / "gke-autopilot-cluster"

# Build WIF tokens from fragments so the scanner can inspect its own source without
# falsely flagging the policy definitions themselves.
WIF_COORDINATE = re.compile(
    "workloadIdentity" + "Pools/|" + "workload" + "_identity_pool",
    re.I,
)

PRIVATE_PATTERNS = {
    "segmented project coordinate": re.compile(
        r"\bproject-[0-9a-f]{8}(?:-[0-9a-f]{3,12}){2,5}\b",
        re.I,
    ),
    "service-account email": re.compile(
        r"\b[^\s@]+@[^\s@]+\.iam\.gserviceaccount\.com\b",
        re.I,
    ),
    "WIF provider coordinate": WIF_COORDINATE,
    "private registry coordinate": re.compile(r"\.pkg\.dev/", re.I),
    "private key material": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
}

FORBIDDEN_TERRAFORM = (
    'resource "google_project_service"',
    'resource "google_compute_global_address"',
    'resource "google_compute_network"',
    'resource "google_compute_subnetwork"',
    'resource "google_container_node_pool"',
    'resource "google_service_account"',
    'resource "google_iam_',
    'resource "google_project_iam',
    'resource "kubernetes_',
    'resource "helm_',
    "workload" + "_identity_pool",
)

FORBIDDEN_CI = (
    "id-token: write",
    "google-github-actions/auth",
    "terraform apply",
    "terraform import",
    "gcloud ",
    "/gcp-ops",
)


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode() for item in output.split(b"\0") if item]


def text_files() -> list[Path]:
    result = []
    for path in tracked_files():
        if path.name == "LICENSE":
            continue
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        result.append(path)
    return result


def main() -> int:
    failures: list[str] = []
    files = tracked_files()

    forbidden_suffixes = (".tfstate", ".tfplan", ".plan", ".pem", ".key", ".p12")
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if rel.endswith(forbidden_suffixes) or ".tfstate." in rel or rel.endswith(".auto.tfvars"):
            failures.append(f"tracked sensitive artifact: {rel}")
        if rel.endswith(".tfvars") and not rel.endswith(".example.tfvars"):
            failures.append(f"tracked non-example tfvars: {rel}")

    for path in text_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for label, pattern in PRIVATE_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{rel}: {label}")

    terraform_text = "\n".join(path.read_text() for path in TF_ROOT.rglob("*.tf"))
    if terraform_text.count('resource "google_container_cluster" "this"') != 1:
        failures.append("Terraform must contain exactly one google_container_cluster.this resource")
    for fragment in FORBIDDEN_TERRAFORM:
        if fragment in terraform_text:
            failures.append(f"forbidden Terraform authority: {fragment}")

    module = (MODULE_ROOT / "main.tf").read_text()
    for required in (
        "enable_autopilot = true",
        "deletion_protection = true",
        "prevent_destroy = true",
        "network          = var.network",
        "subnetwork       = var.subnetwork",
        "channel = var.release_channel",
    ):
        if required not in module:
            failures.append(f"module invariant missing: {required}")

    versions = (ENV_ROOT / "versions.tf").read_text()
    if 'backend "gcs" {}' not in versions:
        failures.append("environment backend must remain an empty externally configured gcs block")
    if re.search(r"\b(bucket|prefix)\s*=", versions):
        failures.append("backend coordinates must not be committed")
    if "access_token" in versions:
        failures.append("explicit provider access-token transport is forbidden")

    lockfile = ENV_ROOT / ".terraform.lock.hcl"
    lock_text = lockfile.read_text() if lockfile.is_file() else ""
    if 'version     = "7.31.0"' not in lock_text:
        failures.append("provider lockfile missing or not pinned to 7.31.0")
    if '"h1:' not in lock_text or lock_text.count('"zh:') < 2:
        failures.append("provider lockfile must contain the complete generated checksum set")

    workflow_root = ROOT / ".github" / "workflows"
    for path in workflow_root.glob("*.yml"):
        text = path.read_text()
        for fragment in FORBIDDEN_CI:
            if fragment in text:
                failures.append(f"{path.relative_to(ROOT)}: forbidden CI authority {fragment!r}")

    required_workflow = workflow_root / "required.yml"
    required_text = required_workflow.read_text() if required_workflow.is_file() else ""
    if "-backend=false" not in required_text or "-lockfile=readonly" not in required_text:
        failures.append("required CI must initialize with backend disabled and committed lock readonly")

    if failures:
        print("Phase-1 infrastructure policy FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Phase-1 infrastructure policy passed: desired-state only; no live Project 03 authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
