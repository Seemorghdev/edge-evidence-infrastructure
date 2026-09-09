from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "docs/examples/portfolio-demo.txt"


class PortfolioReadinessTests(unittest.TestCase):
    def test_primary_demo_matches_checked_in_output(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/portfolio_demo.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertEqual(completed.stdout, EXPECTED.read_text(encoding="utf-8"))

    def test_portfolio_readiness_check_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/check_portfolio.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

    def test_demo_source_contains_no_live_execution_surface(self) -> None:
        text = (ROOT / "scripts/portfolio_demo.py").read_text(encoding="utf-8").lower()
        for forbidden in (
            "terraform plan",
            "terraform apply",
            "terraform import",
            "terraform destroy",
            "terraform state",
            "gcloud ",
            "kubectl ",
            "helm install",
            "helm upgrade",
            "skaffold deploy",
            "id-token: write",
            "google-github-actions/auth",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
