# Extraction provenance

This repository is a repository-only extraction product derived from reviewed material in `Seemorghdev/edge-evidence-reference-platform` at source commit `403ee070fcf31120c3f715bc32bb1643b428f7d2`.

Phase 1 semantically ported/generalized `terraform/modules/gke-autopilot-cluster/**`. Phase 2 semantically ports/generalizes `terraform/modules/cloud-run-service/**` into a single generic service example. The reusable resource semantics are preserved while application composition and live/project-specific coordinates are intentionally excluded.

Project-specific environments, live Terraform state/backend bindings, accepted operational evidence, runbooks, WIF trust, application manifests, the three-service Reference Platform topology, and Project 03 execution authority are not copied.

The Reference Platform remains the current live Project 03 authority. This repository defines reusable desired state only; repository approval grants no provider execution authority.
