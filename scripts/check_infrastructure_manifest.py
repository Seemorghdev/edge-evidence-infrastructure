#!/usr/bin/env python3
"""Fail closed on repository-wide Infrastructure extraction provenance drift."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPO = "Seemorghdev/edge-evidence-reference-platform"
SOURCE_SHA = "403ee070fcf31120c3f715bc32bb1643b428f7d2"
SOURCE_TREE = "c4a810b4288ad1f4092224feea947cdfc357869e"
DEST_BASE = "fda277f9f69a7eaa095dd22266ea736e5c434d93"
TF_TREE = "74073fec6df9f3324313fc60739d77762c4ed4de"
TF_STAGE = "708a3f27625efb6eb319750d1fae8b5207cf2ca7b06b68b50f50fd36a9356008"
FRESH_STAGE = "861395ff5961602ea985e52cbff46f928a074283e1cfdaa1236994d11fcf2512"
FAMILY_COUNTS = {
    "deploy_kubernetes": 13,
    "kustomize": 13,
    "helm": 9,
    "observability": 1,
    "skaffold": 1,
    "workflows": 4,
    "scripts": 11,
    "tests": 25,
    "dependency_followed": 1,
}
DISPOSITIONS = {
    "retain_literal",
    "retain_modified_minimally",
    "already_transplanted_or_represented",
    "delete_operations_owned",
    "delete_reference_application_owned",
    "delete_showcase_owned",
    "delete_live_authority_or_state_only",
    "delete_duplicate_or_superseded",
}
MANDATORY = {
    "deploy/kubernetes/base/namespace.yaml",
    "deploy/kubernetes/project03/exposure-v1/service-neg-patch.json",
    "deploy/kubernetes/project03/exposure-v1/ingress.yaml",
    "kustomize/components/network-policies/policies.yaml",
    "kustomize/components/observability-otel/otel-collector.yaml",
    "kustomize/components/service-mesh-istio/namespace-injection.yaml",
    "kustomize/components/service-mesh-istio/peer-authentication.yaml",
    "observability/otel-collector-config.yaml",
    "skaffold.yaml",
    "scripts/check_authority_boundary.py",
    "scripts/check_architecture.py",
    "scripts/check_provenance.py",
    "scripts/validate_surfaces.py",
    "tests/test_terraform.py",
    "tests/test_deployment_surfaces.py",
    "tests/test_gcp_ambient_terraform_lock_portability.py",
    "tests/test_gcp_terraform_plan_remote_state_v1.py",
    "tests/test_gcp_terraform_state_backend_readback_parser_v1.py",
    "tests/test_gcp_gke_autopilot_cluster_create_v1.py",
    "ops/runbooks/gcp-terraform-state-backend-bootstrap-v1.py",
}
REQUIRED_EDGES = {
    "kustomize/base/kustomization.yaml -> platform/kubernetes/namespace.yaml",
    "kustomize/overlays/observability/kustomization.yaml -> kustomize/base",
    "kustomize/overlays/observability/kustomization.yaml -> kustomize/components/observability-otel",
    "templates/istio.yaml -> templates/_helpers.tpl",
    "templates/otel-collector.yaml -> templates/_helpers.tpl",
    "tests/test_deployment_surfaces.py -> scripts/validate_surfaces.py",
    "tests/test_gcp_terraform_state_backend_readback_parser_v1.py -> ops/runbooks/gcp-terraform-state-backend-bootstrap-v1.py",
    "tests/test_backend_contract.py -> scripts/backend_contract.py",
}


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    snapshot = load("docs/infrastructure-discovery-snapshot.json")
    manifest = load("docs/infrastructure-source-manifest.json")
    terraform = load("docs/terraform-completion-manifest.json")

    require(snapshot["source_repository"] == SOURCE_REPO, "snapshot repository drift")
    require(snapshot["source_commit"] == SOURCE_SHA, "snapshot source SHA drift")
    require(snapshot["source_root_tree_sha"] == SOURCE_TREE, "snapshot source tree drift")
    require(snapshot["destination_baseline_sha"] == DEST_BASE, "destination baseline drift")
    require(snapshot["accounting"] == {
        "non_terraform_candidate_count": 78,
        "repository_wide_total": 117,
        "terraform_subset_count": 39,
    }, "repository-wide accounting drift")
    require({k: len(v) for k, v in snapshot["families"].items()} == FAMILY_COUNTS, "discovery family count drift")

    tf_source = terraform["source"]
    require(tf_source["repository"] == SOURCE_REPO and tf_source["commit"] == SOURCE_SHA, "Phase 6 source pin drift")
    require(tf_source["terraform_tree_sha"] == TF_TREE and tf_source["file_count"] == 39, "Phase 6 tree accounting drift")
    require(tf_source["verified_staging_inventory_sha256"] == TF_STAGE, "Phase 6 staging proof drift")
    tf_entries = terraform["entries"]
    tf_paths = {entry["source_path"] for entry in tf_entries}
    require(len(tf_entries) == len(tf_paths) == 39, "Phase 6 must account for 39 unique files")
    require(snapshot["terraform_subset"] == {
        "manifest_path": "docs/terraform-completion-manifest.json",
        "physical_staging_inventory_sha256": TF_STAGE,
        "source_file_count": 39,
        "source_tree_sha": TF_TREE,
    }, "Phase 7 Terraform subset drift")

    records = [record for family in snapshot["families"].values() for record in family]
    source_paths = {record["path"] for record in records}
    require(len(records) == len(source_paths) == 78, "fresh discovery must contain 78 unique paths")
    require(MANDATORY <= source_paths, "mandatory candidate omitted")
    for record in records:
        require(record["mode"] in {"100644", "100755"}, f"unsupported mode: {record['path']}")
        require(len(record["blob_sha"]) == 40, f"invalid blob SHA: {record['path']}")

    entries = manifest["entries"]
    by_path = {entry["source_path"]: entry for entry in entries}
    require(len(entries) == len(by_path) == 78, "manifest must classify 78 unique paths")
    require(set(by_path) == source_paths, "snapshot/manifest path sets differ")
    record_by_path = {record["path"]: record for record in records}

    fresh = snapshot["fresh_physical_staging"]
    require(fresh["selected_file_count"] == 21 and fresh["inventory_sha256"] == FRESH_STAGE, "fresh staging proof drift")
    require(fresh["materialized_outside_git"] and fresh["all_git_blob_matches"] and not fresh["raw_source_committed"], "fresh staging safety drift")
    staged = set(fresh["paths"])
    require(len(staged) == 21 and staged <= source_paths, "fresh staging path drift")
    selected = {entry["source_path"] for entry in entries if entry["selected"]}
    require(selected == staged, "selected set must equal physically staged set")

    edges: set[str] = set()
    for source_path, entry in by_path.items():
        source = record_by_path[source_path]
        require(entry["source_blob_sha"] == source["blob_sha"] and entry["source_mode"] == source["mode"], f"source identity drift: {source_path}")
        require(entry["disposition"] in DISPOSITIONS, f"unknown disposition: {source_path}")
        edges.update(entry.get("dependency_edges", []))
        retained = entry["disposition"] in {"retain_literal", "retain_modified_minimally"}
        require(retained == bool(entry["selected"]), f"selected/disposition mismatch: {source_path}")
        destinations = entry.get("destination_paths", [])
        if retained:
            require(bool(destinations), f"retained file has no destination: {source_path}")
        elif entry["disposition"] == "already_transplanted_or_represented":
            mapping = entry.get("represented_mapping", {})
            require(bool(mapping.get("baseline_sha")) and bool(mapping.get("destination_paths")), f"represented mapping incomplete: {source_path}")
        else:
            require(bool(entry.get("ownership_reason")), f"deletion lacks ownership/value reason: {source_path}")
        if entry["disposition"] == "retain_modified_minimally":
            require(bool(entry.get("bounded_delta")), f"modified retention lacks bounded delta: {source_path}")

        blobs = entry.get("destination_git_blob_shas", [])
        digests = entry.get("destination_sha256", [])
        require(len(destinations) == len(blobs) == len(digests), f"destination hash cardinality drift: {source_path}")
        for destination, expected_blob, expected_digest in zip(destinations, blobs, digests):
            path = ROOT / destination
            require(path.is_file(), f"retained destination missing: {destination}")
            actual_blob = blob_sha(path)
            require(actual_blob == expected_blob and sha256(path) == expected_digest, f"retained destination hash drift: {destination}")
            if entry["disposition"] == "retain_literal":
                require(actual_blob == entry["source_blob_sha"], f"literal identity lost: {source_path}")
            if entry["disposition"] == "retain_modified_minimally":
                require(actual_blob != entry["source_blob_sha"], f"modified file unexpectedly literal: {source_path}")

    require(REQUIRED_EDGES <= edges, "required dependency/reference edge omitted")
    require(not (tf_paths & source_paths), "fresh discovery overlaps Phase 6 Terraform subset")
    print("repository-wide Infrastructure manifest valid: 117 pinned source paths accounted")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Infrastructure manifest violation: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
