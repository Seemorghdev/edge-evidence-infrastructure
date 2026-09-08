#!/usr/bin/env python3
"""Offline authority and publication-safety checks."""

from __future__ import annotations

import ipaddress
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TF_ROOT = ROOT / "terraform"
GKE_ENV = TF_ROOT / "environments" / "gke-autopilot"
GKE_MODULE = TF_ROOT / "modules" / "gke-autopilot-cluster"
RUN_ENV = TF_ROOT / "environments" / "cloud-run-service-example"
RUN_MODULE = TF_ROOT / "modules" / "cloud-run-service"
ADDRESS_ENV = TF_ROOT / "environments" / "gke-exposure-address"
WIF_ENV = TF_ROOT / "environments" / "github-ops-wif"
PRIVATE_WORKFLOW_ENV = TF_ROOT / "environments" / "private-cloud-run-workflow-example"
PRIVATE_WORKFLOW_MODULE = TF_ROOT / "modules" / "private-cloud-run-workflow"

APPROVED_TERRAFORM_ROOTS = {
    "terraform/environments/cloud-run-service-example",
    "terraform/environments/github-ops-wif",
    "terraform/environments/gke-autopilot",
    "terraform/environments/gke-exposure-address",
    "terraform/environments/private-cloud-run-workflow-example",
    "terraform/modules/cloud-run-service",
    "terraform/modules/gke-autopilot-cluster",
    "terraform/modules/private-cloud-run-workflow",
}
EXPECTED_RESOURCES = {
    GKE_ENV: set(),
    RUN_ENV: set(),
    ADDRESS_ENV: {("google_compute_global_address", "this")},
    WIF_ENV: {
        ("google_project_service", "bootstrap"),
        ("google_service_account", "ops"),
        ("google_iam_workload_identity_pool", "github"),
        ("google_iam_workload_identity_pool_provider", "github"),
        ("google_service_account_iam_member", "github_impersonation"),
        ("google_project_iam_member", "project_roles"),
    },
    PRIVATE_WORKFLOW_ENV: set(),
    GKE_MODULE: {("google_container_cluster", "this")},
    RUN_MODULE: {("google_cloud_run_v2_service", "this")},
    PRIVATE_WORKFLOW_MODULE: {
        ("google_service_account", "workflow"),
        ("google_workflows_workflow", "this"),
        ("google_cloud_run_v2_service_iam_member", "workflow_invoker"),
    },
}
FORBIDDEN_PATH_PREFIXES = (
    "deploy/kubernetes/",
    "kubernetes/",
    "ops/",
    "terraform/environments/gcp-ops-bridge/",
)
CONCRETE_WIF_COORDINATE = re.compile(
    r"projects/[0-9]+/locations/global/"
    + "workloadIdentity"
    + r"Pools/[A-Za-z0-9-]+(?:/providers/[A-Za-z0-9-]+)?",
    re.I,
)
IPV4_LITERAL = re.compile(
    r"(?<![0-9])(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})"
    r"(?:\.(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}(?![0-9])"
)
PRIVATE_PATTERNS = {
    "segmented project coordinate": re.compile(
        r"\bproject-[0-9a-f]{8}(?:-[0-9a-f]{3,12}){2,5}\b", re.I
    ),
    "service-account email": re.compile(
        r"\b[^\s@]+@[^\s@]+\.iam\.gserviceaccount\.com\b", re.I
    ),
    "concrete WIF provider coordinate": CONCRETE_WIF_COORDINATE,
    "private registry coordinate": re.compile(r"\.pkg\.dev/", re.I),
    "private key material": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
}
GLOBAL_FORBIDDEN_TERRAFORM = (
    'resource "google_compute_network"',
    'resource "google_compute_subnetwork"',
    'resource "google_container_node_pool"',
    'resource "kubernetes_',
    'resource "helm_',
    "access_token",
    "impersonate_service_account",
)
FORBIDDEN_CI = (
    "id-token: write",
    "google-github-actions/auth",
    "terraform apply",
    "terraform import",
    "gcloud ",
    "/gcp-ops",
)
TRUST_INPUTS = (
    "trusted_repository",
    "trusted_repository_id",
    "trusted_repository_owner_id",
    "trusted_workflow_ref",
    "trusted_ref",
    "trusted_event",
    "trusted_visibility",
)


def tracked_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode() for item in raw.split(b"\0") if item]


def variable_block(text: str, name: str) -> str:
    marker = f'variable "{name}"'
    start = text.find(marker)
    if start < 0:
        return ""
    next_start = text.find('\nvariable "', start + len(marker))
    return text[start:] if next_start < 0 else text[start:next_start]


def root_resources(root: Path) -> set[tuple[str, str]]:
    text = "\n".join(path.read_text() for path in root.glob("*.tf"))
    return set(re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', text))


def main() -> int:
    failures: list[str] = []
    files = tracked_files()

    actual_roots = {
        path.relative_to(ROOT).as_posix()
        for path in TF_ROOT.glob("*/*")
        if path.is_dir()
    }
    if actual_roots != APPROVED_TERRAFORM_ROOTS:
        failures.append(f"Terraform root inventory drift: {sorted(actual_roots)}")

    for root, expected in EXPECTED_RESOURCES.items():
        actual = root_resources(root)
        if actual != expected:
            failures.append(
                f"{root.relative_to(ROOT)} resource inventory drift: {sorted(actual)}"
            )

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(FORBIDDEN_PATH_PREFIXES):
            failures.append(f"forbidden authority path: {rel}")
        if (
            rel.endswith((".tfstate", ".tfplan", ".plan", ".pem", ".key", ".p12"))
            or ".tfstate." in rel
            or rel.endswith(".auto.tfvars")
        ):
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
        for match in IPV4_LITERAL.finditer(text):
            if ipaddress.ip_address(match.group(0)).is_global:
                failures.append(f"{rel}: globally routable IPv4 literal is forbidden")

    terraform_files = list(TF_ROOT.rglob("*.tf"))
    terraform_text = "\n".join(path.read_text() for path in terraform_files)
    for fragment in GLOBAL_FORBIDDEN_TERRAFORM:
        if fragment in terraform_text:
            failures.append(f"forbidden Terraform authority: {fragment}")

    gke = (GKE_MODULE / "main.tf").read_text()
    for required in (
        "enable_autopilot = true",
        "deletion_protection = true",
        "prevent_destroy = true",
        "network          = var.network",
        "subnetwork       = var.subnetwork",
        "channel = var.release_channel",
    ):
        if required not in gke:
            failures.append(f"GKE invariant missing: {required}")

    run_main = (RUN_MODULE / "main.tf").read_text()
    for required in (
        'resource "google_cloud_run_v2_service" "this"',
        "deletion_protection = var.deletion_protection",
        "@sha256:[0-9a-f]{64}$",
        "startup_probe",
        "liveness_probe",
    ):
        if required not in run_main:
            failures.append(f"Cloud Run invariant missing: {required}")
    run_vars = (RUN_MODULE / "variables.tf").read_text()
    for required in (
        "INGRESS_TRAFFIC_INTERNAL_ONLY",
        "K_SERVICE",
        "K_REVISION",
        "K_CONFIGURATION",
        "PORT",
        "max_instances",
        "cpu",
        "memory",
    ):
        if required not in run_vars:
            failures.append(f"Cloud Run input invariant missing: {required}")

    address_main = (ADDRESS_ENV / "main.tf").read_text()
    for required in (
        'resource "google_compute_global_address" "this"',
        "project      = var.project_id",
        "name         = var.name",
        "address      = var.desired_address",
        'address_type = "EXTERNAL"',
        'ip_version   = "IPV4"',
        "labels       = var.labels",
        "prevent_destroy = true",
    ):
        if required not in address_main:
            failures.append(f"global-address invariant missing: {required}")
    address_tf = "\n".join(path.read_text() for path in ADDRESS_ENV.rglob("*.tf"))
    for forbidden in ('data "', 'import {', 'moved {'):
        if forbidden in address_tf:
            failures.append(f"global-address forbidden authority: {forbidden}")
    address_vars = (ADDRESS_ENV / "variables.tf").read_text()
    if 'variable "desired_address"' not in address_vars or "default     = null" not in address_vars:
        failures.append("global-address desired_address must remain optional with a null default")

    wif_main = (WIF_ENV / "main.tf").read_text()
    wif_vars = (WIF_ENV / "variables.tf").read_text()
    wif_tf = "\n".join(path.read_text() for path in WIF_ENV.rglob("*.tf"))
    for forbidden in ('data "', 'import {', 'moved {', "access_token", "impersonate_service_account"):
        if forbidden in wif_tf:
            failures.append(f"github-ops-wif forbidden execution authority: {forbidden}")
    for required in (
        "cloudresourcemanager.googleapis.com",
        "iam.googleapis.com",
        "iamcredentials.googleapis.com",
        "serviceusage.googleapis.com",
        "sts.googleapis.com",
        'issuer_uri = "https://token.actions.githubusercontent.com"',
        'role               = "roles/iam.workloadIdentityUser"',
        "/attribute.repository_id/${var.trusted_repository_id}",
        "for_each = var.project_roles",
    ):
        if required not in wif_main:
            failures.append(f"github-ops-wif invariant missing: {required}")
    if set(re.findall(r'"(roles/[A-Za-z0-9_.]+)"', wif_main)) != {"roles/iam.workloadIdentityUser"}:
        failures.append("github-ops-wif main.tf must not embed project-role inventory")
    for name in TRUST_INPUTS:
        block = variable_block(wif_vars, name)
        if not block or "default" in block or "nullable    = false" not in block or "validation {" not in block:
            failures.append(f"github-ops-wif trust input must be required and validated: {name}")
    role_block = variable_block(wif_vars, "project_roles")
    if "default     = []" not in role_block or "length(var.project_roles) <= 8" not in role_block:
        failures.append("github-ops-wif project_roles must default empty and remain bounded")

    private_main = (PRIVATE_WORKFLOW_MODULE / "main.tf").read_text()
    private_vars = (PRIVATE_WORKFLOW_MODULE / "variables.tf").read_text()
    private_tf = "\n".join(path.read_text() for path in PRIVATE_WORKFLOW_MODULE.rglob("*.tf"))
    for required in (
        'resource "google_service_account" "workflow"',
        'resource "google_workflows_workflow" "this"',
        'resource "google_cloud_run_v2_service_iam_member" "workflow_invoker"',
        "source_contents         = var.workflow_source_contents",
        "service_account         = google_service_account.workflow.email",
        "for_each = local.cloud_run_targets",
        'role     = "roles/run.invoker"',
        'member   = "serviceAccount:${google_service_account.workflow.email}"',
        "location = coalesce(target.location, var.region)",
    ):
        if required not in private_main:
            failures.append(f"private workflow invariant missing: {required}")
    private_roles = set(re.findall(r'"(roles/[A-Za-z0-9_.]+)"', private_main))
    if private_roles != {"roles/run.invoker"}:
        failures.append(f"private workflow must embed only roles/run.invoker: {sorted(private_roles)}")
    for forbidden in (
        'data "',
        "templatefile(",
        ".uri",
        "token.actions.githubusercontent.com",
        "workload_identity_pool",
        'resource "google_project_iam',
        'resource "google_iam_',
        "access_token",
        "impersonate_service_account",
        "evidence-api",
        "edge-agent",
        "web-ui",
        "/readyz",
        "/health",
    ):
        if forbidden in private_tf:
            failures.append(f"private workflow contains forbidden copied authority/topology: {forbidden}")
    source_block = variable_block(private_vars, "workflow_source_contents")
    if "nullable    = false" not in source_block or "65536" not in source_block or "validation {" not in source_block:
        failures.append("private workflow source must be required and bounded")
    targets_block = variable_block(private_vars, "cloud_run_targets")
    if "default = {}" not in targets_block or "length(var.cloud_run_targets) <= 16" not in targets_block:
        failures.append("private workflow targets must default empty and remain cardinality-bounded")

    backend_envs = (GKE_ENV, ADDRESS_ENV, WIF_ENV, PRIVATE_WORKFLOW_ENV)
    for env in backend_envs:
        versions = (env / "versions.tf").read_text()
        if 'backend "gcs" {}' not in versions or re.search(r"\b(bucket|prefix)\s*=", versions):
            failures.append(f"{env.relative_to(ROOT)} backend must be externally configured without coordinates")
        for forbidden in ("access_token", "impersonate_service_account", "credentials"):
            if forbidden in versions:
                failures.append(f"{env.relative_to(ROOT)} provider authority is forbidden: {forbidden}")

    run_versions = (RUN_ENV / "versions.tf").read_text()
    if 'backend "' in run_versions:
        failures.append("Cloud Run example must not bind a remote backend")

    for env in (GKE_ENV, RUN_ENV, ADDRESS_ENV, WIF_ENV, PRIVATE_WORKFLOW_ENV):
        lock = (env / ".terraform.lock.hcl").read_text()
        if 'version     = "7.31.0"' not in lock or '"h1:' not in lock or lock.count('"zh:') < 2:
            failures.append(f"{env.relative_to(ROOT)}: incomplete provider lock")

    workflow = (ROOT / ".github" / "workflows" / "required.yml").read_text()
    for fragment in FORBIDDEN_CI:
        if fragment in workflow:
            failures.append(f"required CI contains forbidden authority {fragment!r}")
    for env_name in (
        "gke-autopilot",
        "cloud-run-service-example",
        "gke-exposure-address",
        "github-ops-wif",
        "private-cloud-run-workflow-example",
    ):
        needle = f"terraform/environments/{env_name} init -backend=false -input=false -lockfile=readonly"
        if needle not in workflow:
            failures.append(f"required CI missing readonly offline init for {env_name}")
    for module_name in ("cloud-run-service", "private-cloud-run-workflow"):
        if f"terraform/modules/{module_name} init -backend=false -input=false" not in workflow:
            failures.append(f"required CI missing credential-free init for {module_name}")
        if f"terraform/modules/{module_name} test -no-color" not in workflow:
            failures.append(f"required CI missing native test lane for {module_name}")

    if failures:
        print("Infrastructure policy FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Infrastructure policy passed: reusable desired state only; "
        "Reference Platform remains live Project 03 authority"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
