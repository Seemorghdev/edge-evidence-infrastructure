#!/usr/bin/env python3
"""Credential-free structural validation for retained Infrastructure surfaces."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

APP_NAMES = {"evidence-api", "edge-agent", "web-ui"}


def docs(path: Path) -> list[dict[str, object]]:
    return [document for document in yaml.safe_load_all(path.read_text()) if document]


def names(documents: list[dict[str, object]]) -> set[str]:
    result: set[str] = set()
    for document in documents:
        metadata = document.get("metadata")
        if isinstance(metadata, dict):
            name = metadata.get("name")
            if isinstance(name, str):
                result.add(name)
    return result


def main() -> int:
    namespace_docs = docs(Path("platform/kubernetes/namespace.yaml"))
    assert len(namespace_docs) == 1
    assert namespace_docs[0]["kind"] == "Namespace"
    assert namespace_docs[0]["metadata"]["name"] == "edge-evidence"

    neg = json.loads(Path("platform/kubernetes/neg/service-neg-patch.json").read_text())
    assert neg["metadata"]["annotations"]["cloud.google.com/neg"] == '{"ingress": true}'

    base = yaml.safe_load(Path("kustomize/base/kustomization.yaml").read_text())
    assert base["kind"] == "Kustomization"
    assert base["resources"] == ["../../platform/kubernetes/namespace.yaml"]

    for path in Path("kustomize").rglob("*.yaml"):
        docs(path)
    for path in Path("observability").glob("*.yaml"):
        docs(path)

    policies = docs(Path("kustomize/components/network-policies/policies.yaml"))
    assert {document["kind"] for document in policies} == {"NetworkPolicy"}
    assert {document["metadata"]["name"] for document in policies} == {
        "default-deny",
        "allow-reference-platform",
    }

    mesh = docs(Path("kustomize/components/service-mesh-istio/peer-authentication.yaml"))
    assert len(mesh) == 1
    assert mesh[0]["kind"] == "PeerAuthentication"
    assert mesh[0]["spec"]["mtls"]["mode"] == "STRICT"

    otel = docs(Path("kustomize/components/observability-otel/otel-collector.yaml"))
    assert {document["kind"] for document in otel} == {"ConfigMap", "Deployment", "Service"}
    assert names(otel) == {"otel-collector", "otel-collector-config"}

    standalone_otel = yaml.safe_load(Path("observability/otel-collector-config.yaml").read_text())
    pipelines = standalone_otel["service"]["pipelines"]
    assert set(pipelines) == {"traces", "metrics", "logs"}

    values = yaml.safe_load(Path("helm-chart/edge-evidence-platform/values.yaml").read_text())
    assert set(values) == {"namespaceOverride", "observability", "serviceMesh"}
    assert values["observability"]["enabled"] is False
    assert values["serviceMesh"]["enabled"] is False

    retained_text = "\n".join(
        path.read_text()
        for root in (
            Path("platform"),
            Path("kustomize"),
            Path("helm-chart"),
            Path("observability"),
        )
        for path in root.rglob("*")
        if path.is_file()
    )
    assert "kind: Ingress" not in retained_text
    for app_name in APP_NAMES:
        assert app_name not in retained_text

    print("retained Infrastructure surfaces structurally consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
