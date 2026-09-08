#!/usr/bin/env python3
"""Validate the Phase 6 pinned Terraform completion manifest offline."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "terraform-completion-manifest.json"

ALLOWED_DISPOSITIONS = {
    "already_transplanted_or_represented",
    "retain_literal",
    "retain_modified_minimally",
    "delete_application_owned",
    "delete_live_authority_state_backend",
    "delete_operations_owned",
    "delete_duplicate_or_superseded",
}
EXPECTED_SOURCE_BLOBS = {
    "terraform/README.md": "3974855327a8dca6e25c94f0a4e93e768be9cd52",
    "terraform/environments/cloud-run-demo/ci.tfvars": "7e3efa378b7ac635a0afb471cd7df405c4f0522c",
    "terraform/environments/cloud-run-demo/main.tf": "97655329367df9987a4b2e51107f12323185ae82",
    "terraform/environments/cloud-run-demo/outputs.tf": "3754c6986920d9d1a41e3704ace3c69caadcab92",
    "terraform/environments/cloud-run-demo/terraform.tfvars.example": "63704b9c29b87e889e4cfdaab2c1837945e1c1fd",
    "terraform/environments/cloud-run-demo/tests/cloud_run_demo.tftest.hcl": "84e96878d161af9f1add4290aa707955070bcc68",
    "terraform/environments/cloud-run-demo/tests/reserved_environment_variables.tftest.hcl": "22e5b4624ce5c8574984ced34434e3467b923af1",
    "terraform/environments/cloud-run-demo/variables.tf": "199d0f1d62a109c436172cb20652ab6e1452ed79",
    "terraform/environments/cloud-run-demo/versions.tf": "d932e9706526ac6341df52b4c102761b4c60c2ac",
    "terraform/environments/gcp-ops-bridge/README.md": "2f1142fecb09ad72e5d6c959033d2e93c3041d3a",
    "terraform/environments/gcp-ops-bridge/main.tf": "e2c49cf3ec27a4666290392cb979973043e26342",
    "terraform/environments/gcp-ops-bridge/outputs.tf": "e814e005692eeaede922c76f9fc12f9b89d233c1",
    "terraform/environments/gcp-ops-bridge/tests/gcp_ops_bridge.tftest.hcl": "9e0da3024f470a5aea46159d0110f4ec48221a95",
    "terraform/environments/gcp-ops-bridge/variables.tf": "68602ef77d76bb8829423ff758f893b19bedb1b6",
    "terraform/environments/gcp-ops-bridge/versions.tf": "2ff7a8e039a8076f57863c92b7afea879830796c",
    "terraform/environments/gke-autopilot/README.md": "661892b853ecb47d928243cea3da33b2ab0eba8c",
    "terraform/environments/gke-autopilot/main.tf": "9a6d7fac71499190cb05cc9698daac47e831e0b7",
    "terraform/environments/gke-autopilot/outputs.tf": "84da84881500d5c99d9f8daee8e4bd045b6fa3bb",
    "terraform/environments/gke-autopilot/tests/gke_autopilot.tftest.hcl": "5b8e4202bc125666f1272cfb281284ac9c475178",
    "terraform/environments/gke-autopilot/variables.tf": "b6a4f6e394baa8d7826c74f579784e6f78bfb8c8",
    "terraform/environments/gke-autopilot/versions.tf": "d1281a71d5537a3b316be108b5ee19a9b3640d68",
    "terraform/environments/gke-exposure-address/README.md": "f435f974d4363b8cff4d6ea84a8d2bcc3009cc99",
    "terraform/environments/gke-exposure-address/main.tf": "611e2e0e77d05f5e73946aaf0584a68a2da9d396",
    "terraform/environments/gke-exposure-address/outputs.tf": "5e7c2519d8c920f2a4123ab79720b5d1056d7729",
    "terraform/environments/gke-exposure-address/variables.tf": "b6a4f6e394baa8d7826c74f579784e6f78bfb8c8",
    "terraform/environments/gke-exposure-address/versions.tf": "90d9ef153c14798adc06b104fc147a96bfe40fb6",
    "terraform/environments/private-probe/main.tf": "22499cf20e2dc057da046e2493529d879924dea3",
    "terraform/environments/private-probe/outputs.tf": "29f623281d119c43c52dec43cc7f7ed93d0ae55a",
    "terraform/environments/private-probe/tests/private_probe.tftest.hcl": "1b63008d715423637d3ec45925ca801304004b7d",
    "terraform/environments/private-probe/variables.tf": "8692baae16cd8c73646da8ffef11376514950589",
    "terraform/environments/private-probe/versions.tf": "2ff7a8e039a8076f57863c92b7afea879830796c",
    "terraform/environments/private-probe/workflow.yaml.tpl": "a0e95780849a7740205d1a4b124caf10fa7f3b08",
    "terraform/modules/cloud-run-service/main.tf": "4d4ccc84e0eafe3b51b40ffa9095a8573f1746f3",
    "terraform/modules/cloud-run-service/outputs.tf": "182c773002de12c790d317986815852bfd74f341",
    "terraform/modules/cloud-run-service/variables.tf": "81e99a55150dae471a66325997e59cc90e3d4c48",
    "terraform/modules/cloud-run-service/versions.tf": "b0a37ffac30b6fb79353b8dca538878e9feb4cc6",
    "terraform/modules/gke-autopilot-cluster/main.tf": "86a0382c5e98121068b20373d475522fa42c0599",
    "terraform/modules/gke-autopilot-cluster/variables.tf": "693ea0afa418d54dea0f1d5825794dcf960a3fd2",
    "terraform/modules/gke-autopilot-cluster/versions.tf": "b0a37ffac30b6fb79353b8dca538878e9feb4cc6",
}
FORBIDDEN_RAW_ROOTS = (
    "terraform/environments/cloud-run-demo/",
    "terraform/environments/gcp-ops-bridge/",
    "terraform/environments/private-probe/",
)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def main() -> int:
    failures: list[str] = []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = data.get("entries", [])

    if data.get("source", {}).get("commit") != "403ee070fcf31120c3f715bc32bb1643b428f7d2":
        failures.append("manifest source commit drift")
    if data.get("source", {}).get("terraform_tree_sha") != "74073fec6df9f3324313fc60739d77762c4ed4de":
        failures.append("manifest source terraform tree drift")
    if data.get("destination", {}).get("accepted_baseline") != "03a424593913ea77ebc260008fcd4273ce11d30b":
        failures.append("manifest accepted destination baseline drift")
    if data.get("staging_proof", {}) != {
        "materialized_outside_git": True,
        "source_file_count": 39,
        "git_blob_sha_matches": 39,
        "raw_source_committed": False,
    }:
        failures.append("manifest staging proof drift")

    actual = {e.get("source_path"): e for e in entries}
    if len(entries) != len(actual):
        failures.append("manifest contains duplicate source paths")
    if set(actual) != set(EXPECTED_SOURCE_BLOBS):
        failures.append("manifest does not exhaustively cover the pinned terraform tree")

    for path, expected_sha in EXPECTED_SOURCE_BLOBS.items():
        entry = actual.get(path, {})
        if entry.get("source_blob_sha") != expected_sha:
            failures.append(f"source blob SHA drift: {path}")
        disposition = entry.get("disposition")
        if disposition not in ALLOWED_DISPOSITIONS:
            failures.append(f"invalid disposition for {path}: {disposition}")
        destinations = entry.get("accepted_destination_paths", [])
        if disposition == "already_transplanted_or_represented":
            represented = entry.get("represented_by", {})
            if not destinations or not represented.get("phase") or not represented.get("pull_request"):
                failures.append(f"represented path lacks phase/PR/destination mapping: {path}")
            for destination in destinations:
                if not (ROOT / destination).is_file():
                    failures.append(f"represented destination missing: {path} -> {destination}")
        elif disposition in {"retain_literal", "retain_modified_minimally"}:
            hashes = entry.get("destination_blob_shas", [])
            if len(destinations) != len(hashes) or not destinations:
                failures.append(f"retained path lacks destination hash proof: {path}")
            if disposition == "retain_modified_minimally" and not entry.get("reason"):
                failures.append(f"minimally modified path lacks reason: {path}")
            for destination, expected_destination_sha in zip(destinations, hashes):
                target = ROOT / destination
                if not target.is_file() or git_blob_sha(target) != expected_destination_sha:
                    failures.append(f"retained destination hash mismatch: {destination}")
            if disposition == "retain_literal" and hashes != [expected_sha] * len(hashes):
                failures.append(f"literal retention is not byte-identical: {path}")
        elif destinations:
            failures.append(f"deleted source path unexpectedly maps to destination: {path}")

    inventory = "".join(
        f"{path}\0{EXPECTED_SOURCE_BLOBS[path]}\n" for path in sorted(EXPECTED_SOURCE_BLOBS)
    )
    inventory_sha = hashlib.sha256(inventory.encode()).hexdigest()
    if inventory_sha != data.get("source", {}).get("verified_staging_inventory_sha256"):
        failures.append("verified staging inventory digest mismatch")

    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0")
    tracked_paths = [p.decode() for p in tracked if p]
    for prefix in FORBIDDEN_RAW_ROOTS:
        if any(path.startswith(prefix) for path in tracked_paths):
            failures.append(f"raw source family entered public tree: {prefix}")

    if data.get("retained_new_files") != {
        "retain_literal": [],
        "retain_modified_minimally": [],
    }:
        failures.append("Phase 6 unexpectedly retains new Terraform source files")

    if failures:
        print("Terraform completion audit FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Terraform completion audit passed: "
        f"{len(EXPECTED_SOURCE_BLOBS)} pinned source files classified exactly once; "
        "no new raw Terraform source retained"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
