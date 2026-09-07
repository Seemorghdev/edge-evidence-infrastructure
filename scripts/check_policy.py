#!/usr/bin/env python3
"""Offline authority and publication-safety checks."""
from __future__ import annotations
import re
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TF_ROOT = ROOT / "terraform"
GKE_ENV = TF_ROOT / "environments" / "gke-autopilot"
GKE_MODULE = TF_ROOT / "modules" / "gke-autopilot-cluster"
RUN_ENV = TF_ROOT / "environments" / "cloud-run-service-example"
RUN_MODULE = TF_ROOT / "modules" / "cloud-run-service"
WIF_COORDINATE = re.compile("workloadIdentity" + "Pools/|" + "workload" + "_identity_pool", re.I)
PRIVATE_PATTERNS = {
    "segmented project coordinate": re.compile(r"\bproject-[0-9a-f]{8}(?:-[0-9a-f]{3,12}){2,5}\b", re.I),
    "service-account email": re.compile(r"\b[^\s@]+@[^\s@]+\.iam\.gserviceaccount\.com\b", re.I),
    "WIF provider coordinate": WIF_COORDINATE,
    "private registry coordinate": re.compile(r"\.pkg\.dev/", re.I),
    "private key material": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
FORBIDDEN_TERRAFORM = (
    'resource "google_project_service"', 'resource "google_compute_global_address"',
    'resource "google_compute_network"', 'resource "google_compute_subnetwork"',
    'resource "google_container_node_pool"', 'resource "google_service_account"',
    'resource "google_iam_', 'resource "google_project_iam', 'resource "kubernetes_',
    'resource "helm_', "workload" + "_identity_pool",
)
FORBIDDEN_CI = ("id-token: write", "google-github-actions/auth", "terraform apply", "terraform import", "gcloud ", "/gcp-ops")

def tracked_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode() for item in raw.split(b"\0") if item]

def main() -> int:
    failures: list[str] = []
    files = tracked_files()
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if rel.endswith((".tfstate", ".tfplan", ".plan", ".pem", ".key", ".p12")) or ".tfstate." in rel or rel.endswith(".auto.tfvars"):
            failures.append(f"tracked sensitive artifact: {rel}")
        if rel.endswith(".tfvars") and not rel.endswith(".example.tfvars"):
            failures.append(f"tracked non-example tfvars: {rel}")
        if path.name == "LICENSE":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        for label, pattern in PRIVATE_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{rel}: {label}")
    terraform_text = "\n".join(p.read_text() for p in TF_ROOT.rglob("*.tf"))
    if terraform_text.count('resource "google_container_cluster" "this"') != 1:
        failures.append("must contain exactly one Autopilot cluster resource")
    if terraform_text.count('resource "google_cloud_run_v2_service" "this"') != 1:
        failures.append("must contain exactly one reusable Cloud Run service resource")
    for fragment in FORBIDDEN_TERRAFORM:
        if fragment in terraform_text:
            failures.append(f"forbidden Terraform authority: {fragment}")
    gke = (GKE_MODULE / "main.tf").read_text()
    for required in ("enable_autopilot = true", "deletion_protection = true", "prevent_destroy = true"):
        if required not in gke:
            failures.append(f"GKE invariant missing: {required}")
    run_main = (RUN_MODULE / "main.tf").read_text()
    for required in ("google_cloud_run_v2_service", "deletion_protection = var.deletion_protection", "@sha256:[0-9a-f]{64}$", "startup_probe", "liveness_probe"):
        if required not in run_main:
            failures.append(f"Cloud Run invariant missing: {required}")
    run_vars = (RUN_MODULE / "variables.tf").read_text()
    for required in ("INGRESS_TRAFFIC_INTERNAL_ONLY", "K_SERVICE", "max_instances", "cpu", "memory"):
        if required not in run_vars:
            failures.append(f"Cloud Run input invariant missing: {required}")
    gke_versions = (GKE_ENV / "versions.tf").read_text()
    if 'backend "gcs" {}' not in gke_versions or re.search(r"\b(bucket|prefix)\s*=", gke_versions):
        failures.append("GKE backend must remain externally configured without coordinates")
    if "backend \"" in (RUN_ENV / "versions.tf").read_text():
        failures.append("Cloud Run example must not bind a remote backend")
    for env in (GKE_ENV, RUN_ENV):
        lock = (env / ".terraform.lock.hcl").read_text()
        if 'version     = "7.31.0"' not in lock or '"h1:' not in lock or lock.count('"zh:') < 2:
            failures.append(f"{env.relative_to(ROOT)}: incomplete provider lock")
    workflow = (ROOT / ".github" / "workflows" / "required.yml").read_text()
    for fragment in FORBIDDEN_CI:
        if fragment in workflow:
            failures.append(f"required CI contains forbidden authority {fragment!r}")
    for env_name in ("gke-autopilot", "cloud-run-service-example"):
        needle = f"terraform/environments/{env_name} init -backend=false -input=false -lockfile=readonly"
        if needle not in workflow:
            failures.append(f"required CI missing readonly offline init for {env_name}")
    if failures:
        print("Infrastructure policy FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Infrastructure policy passed: reusable desired state only; Reference Platform remains live Project 03 authority")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
