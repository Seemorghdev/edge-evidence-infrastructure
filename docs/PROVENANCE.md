# Extraction provenance

This repository is a repository-only extraction product derived from reviewed material in `Seemorghdev/edge-evidence-reference-platform` at source commit `403ee070fcf31120c3f715bc32bb1643b428f7d2`.

Phase 1 semantically ported/generalized `terraform/modules/gke-autopilot-cluster/**`. Phase 2 semantically ported/generalized `terraform/modules/cloud-run-service/**` into a single generic service example. Phase 3 semantically ported/generalized the guarded `google_compute_global_address` resource shape from `terraform/environments/gke-exposure-address/main.tf` into a sanitized standalone desired-state environment. Phase 4 semantically ported/generalized WIF **provisioning** semantics from `terraform/environments/gcp-ops-bridge/**` into `terraform/environments/github-ops-wif/**`. Phase 5 uses a copy-first extraction from `terraform/environments/private-probe/**` into `terraform/modules/private-cloud-run-workflow/**` plus a synthetic credential-free example.

For Phase 3, the reusable resource semantics retained are one global external IPv4 address and Terraform `prevent_destroy`. The source project's concrete project coordinate, retained IPv4, resource identity, labels, backend bucket/prefix, provider access-token transport, promotion/adoption language, import/state material, and operational evidence are intentionally not copied.

For Phase 4, the retained provisioning semantics are the five reviewed IAM/WIF bootstrap APIs, one operations service account, one Workload Identity Pool, one GitHub OIDC provider using `https://token.actions.githubusercontent.com`, the reviewed GitHub claim mapping, a fail-closed condition over repository/workflow/ref/event/visibility claims, one repository-ID-scoped `roles/iam.workloadIdentityUser` binding, and parameterized project-role IAM members. The source service-account ID, pool/provider IDs, repository identity and numeric IDs, workflow ref, project coordinate, region, broad Project 03 project-role inventory, provider access-token transport, backend/state coordinates, and operational WIF consumption/control material are intentionally not copied. Project roles default to empty in the standalone root.

## Phase 5 COPY → REMOVE → PARAMETERIZE → SANITIZE → PROVE

**COPY:** the implementation starts from the reviewed `private-probe/main.tf` resource relationships at source SHA `403ee070fcf31120c3f715bc32bb1643b428f7d2`: a workflow service account, a Google Workflow resource using that identity, and Cloud Run service IAM members granting workflow invocation.

**REMOVE:** the source `data "google_cloud_run_v2_service"` URI lookups, `workflow.yaml.tpl`, all Project 03 service labels/names/routes, the source GitHub WIF pool/provider, GitHub claim mapping and attribute condition, `google_project_iam_member.github_workflow_invoker`, repository coordinates, provider access-token transport, and URI-bearing outputs are not copied.

**PARAMETERIZE:** project, region, workflow name/description, workflow service-account metadata, workflow source contents, and a bounded map of Cloud Run service names/locations become caller inputs. Target location may inherit the workflow region. The IAM role does not become an input: `roles/run.invoker` remains fixed in module code.

**SANITIZE:** the example uses only obviously synthetic project/workflow/service/identity values and an inert workflow program that returns a synthetic string. The example GCS backend has no bucket or prefix. No current Project 03 project/account/repository/workflow/service identity, service URI, private endpoint, provider credential, state coordinate, or retained operational payload is present.

**PROVE:** Terraform-native tests use a mocked Google provider to prove exact resource inventory, generic input flow, fixed `roles/run.invoker` target bindings, zero IAM members for an empty target set, and fail-closed malformed inputs. A mocked `apply` run is used only to resolve a synthetic computed service-account email for exact IAM-member proof; it performs no provider operation. Repository policy independently restricts the new resource types and IAM exception to the exact new module and forbids copied Project 03 probe topology, WIF trust, provider credentials, and target URI readback.

The source workflow's `deletion_protection = false` is retained as a copy-first generic desired-state semantic. This repository does not claim ownership of an existing Project 03 workflow and grants no deletion or provider execution authority.

Live Terraform state/backend bindings, accepted operational evidence, runbooks, current WIF trust/consumption, current workflow execution/control semantics, application manifests, the three-service Reference Platform topology, retained address evidence, and Project 03 execution authority are not copied.

The Reference Platform remains the current live Project 03 authority, including for the existing external address, current private workflow/application behavior, and current GitHub WIF/trust relationships. This repository defines reusable desired state only; repository approval grants no provider execution, workflow execution, state-adoption, trust-consumption, trust-migration, or authority-cutover permission.
