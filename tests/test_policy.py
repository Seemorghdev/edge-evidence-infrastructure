from __future__ import annotations
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
            "terraform/environments/gke-autopilot",
            "terraform/modules/cloud-run-service",
            "terraform/modules/gke-autopilot-cluster",
        ])

    def test_reference_platform_remains_declared_live_authority(self) -> None:
        readme = (ROOT / "README.md").read_text()
        self.assertIn("remains the live Project 03 authority", readme)
        self.assertIn("desired-state", readme)

if __name__ == "__main__":
    unittest.main()
