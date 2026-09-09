from __future__ import annotations
import re
import subprocess
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class InfrastructurePolicyTests(unittest.TestCase):
    def test_policy_script_passes(self) -> None:
        subprocess.run(["python", "scripts/check_policy.py"], cwd=ROOT, check=True)

    def test_only_approved_terraform_roots_exist(self) -> None:
        roots = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "terraform").glob("*/*") if path.is_dir())
        self.assertEqual(roots, [
            "terraform/environments/cloud-run-service-example",
            "terraform/environments/github-ops-wif",
            "terraform/environments/gke-autopilot",
            "terraform/environments/gke-exposure-address",
            "terraform/environments/private-cloud-run-workflow-example",
            "terraform/modules/cloud-run-service",
            "terraform/modules/gke-autopilot-cluster",
            "terraform/modules/private-cloud-run-workflow",
        ])

    def test_live_authority_remains_outside_repository(self) -> None:
        readme = (ROOT / "README.md").read_text()
        architecture = (ROOT / "docs/ARCHITECTURE.md").read_text()
        provenance = (ROOT / "docs/PROVENANCE.md").read_text()
        self.assertIn("desired-state", readme)
        self.assertIn(
            "Existing live environment, application, and operational authority remains separately governed",
            readme,
        )
        self.assertIn("does not authenticate to or mutate the live cloud/cluster", architecture)
        self.assertIn("Reference Platform remains the current live Project 03 authority", provenance)

    def test_global_address_is_sanitized_desired_state_only(self) -> None:
        address_main = (ROOT / "terraform/environments/gke-exposure-address/main.tf").read_text()
        self.assertEqual(address_main.count('resource "google_compute_global_address"'), 1)
        self.assertIn('address_type = "EXTERNAL"', address_main)
        self.assertIn('ip_version   = "IPV4"', address_main)
        self.assertIn("prevent_destroy = true", address_main)

    def test_wif_root_contains_only_reviewed_provisioning_resources(self) -> None:
        wif_root = ROOT / "terraform/environments/github-ops-wif"
        text = "\n".join(path.read_text() for path in wif_root.glob("*.tf"))
        resources = set(re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', text))
        self.assertEqual(resources, {
            ("google_project_service", "bootstrap"),
            ("google_service_account", "ops"),
            ("google_iam_workload_identity_pool", "github"),
            ("google_iam_workload_identity_pool_provider", "github"),
            ("google_service_account_iam_member", "github_impersonation"),
            ("google_project_iam_member", "project_roles"),
        })
        self.assertNotIn("access_token", text)
        self.assertNotIn("impersonate_service_account", text)

    def test_wif_repository_principal_is_derived_not_literal(self) -> None:
        main = (ROOT / "terraform/environments/github-ops-wif/main.tf").read_text()
        self.assertIn(
            'member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository_id/${var.trusted_repository_id}"',
            main,
        )

    def test_private_workflow_module_contains_only_provisioning_substrate(self) -> None:
        root = ROOT / "terraform/modules/private-cloud-run-workflow"
        text = "\n".join(path.read_text() for path in root.glob("*.tf"))
        resources = set(re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', text))
        self.assertEqual(resources, {
            ("google_service_account", "workflow"),
            ("google_workflows_workflow", "this"),
            ("google_cloud_run_v2_service_iam_member", "workflow_invoker"),
        })
        self.assertIn('role     = "roles/run.invoker"', text)
        self.assertIn("source_contents         = var.workflow_source_contents", text)
        self.assertNotIn('data "google_cloud_run_v2_service"', text)
        self.assertNotIn("templatefile(", text)
        self.assertNotIn("workload_identity_pool", text)

    def test_private_workflow_carries_no_project03_probe_topology(self) -> None:
        prefixes = (
            "terraform/modules/private-cloud-run-workflow/",
            "terraform/environments/private-cloud-run-workflow-example/",
        )
        tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
        paths = [ROOT / path for path in tracked if path.startswith(prefixes)]
        text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        for forbidden in ("evidence-api", "edge-agent", "web-ui", "/readyz", "/health", "token.actions.githubusercontent.com"):
            self.assertNotIn(forbidden, text)

if __name__ == "__main__":
    unittest.main()
