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
            "terraform/modules/cloud-run-service",
            "terraform/modules/gke-autopilot-cluster",
        ])

    def test_reference_platform_remains_declared_live_authority(self) -> None:
        readme = (ROOT / "README.md").read_text()
        self.assertIn("remains the live Project 03 authority", readme)
        self.assertIn("desired-state", readme)

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

if __name__ == "__main__":
    unittest.main()
