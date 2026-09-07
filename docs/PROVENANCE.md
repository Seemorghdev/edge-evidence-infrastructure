# Extraction provenance

This repository is a repository-only extraction product derived from reviewed material in `Seemorghdev/edge-evidence-reference-platform` at source commit `403ee070fcf31120c3f715bc32bb1643b428f7d2`.

Phase 1 semantically ported/generalized `terraform/modules/gke-autopilot-cluster/**`. Phase 2 semantically ported/generalized `terraform/modules/cloud-run-service/**` into a single generic service example. Phase 3 semantically ports/generalizes the guarded `google_compute_global_address` resource shape from `terraform/environments/gke-exposure-address/main.tf` into a sanitized standalone desired-state environment.

For Phase 3, the reusable resource semantics retained are one global external IPv4 address and Terraform `prevent_destroy`. The source project's concrete project coordinate, retained IPv4, resource identity, labels, backend bucket/prefix, provider access-token transport, promotion/adoption language, import/state material, and operational evidence are intentionally not copied. The standalone environment accepts generic inputs, defaults the optional desired address to `null`, uses an empty externally configured GCS backend declaration, and validates only with a mocked provider.

Live Terraform state/backend bindings, accepted operational evidence, runbooks, WIF trust, application manifests, the three-service Reference Platform topology, retained address evidence, and Project 03 execution authority are not copied.

The Reference Platform remains the current live Project 03 authority, including for the existing external address. This repository defines reusable desired state only; repository approval grants no provider execution or state-adoption authority.
