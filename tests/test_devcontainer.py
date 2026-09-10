from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DevcontainerEvaluatorTests(unittest.TestCase):
    def test_devcontainer_policy_passes(self) -> None:
        subprocess.run(
            ["python", "scripts/check_devcontainer.py"],
            cwd=ROOT,
            check=True,
        )

    def test_evaluator_toolchain_is_minimal_and_pinned(self) -> None:
        config = json.loads((ROOT / ".devcontainer/devcontainer.json").read_text())
        self.assertEqual(config["remoteUser"], "vscode")
        self.assertEqual(config["build"], {"dockerfile": "Dockerfile"})
        self.assertEqual(
            set(config["features"]),
            {"ghcr.io/devcontainers/features/docker-in-docker:4"},
        )
        dockerfile = (ROOT / ".devcontainer/Dockerfile").read_text()
        self.assertIn("ARG TERRAFORM_VERSION=1.9.8", dockerfile)
        self.assertIn("python:1-3.12-bookworm", dockerfile)
        self.assertNotIn("gcloud", dockerfile.lower())
        self.assertNotIn("kubectl", dockerfile.lower())
        self.assertNotIn("skaffold", dockerfile.lower())


if __name__ == "__main__":
    unittest.main()
