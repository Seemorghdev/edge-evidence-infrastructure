from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "terraform-completion-manifest.json"


class TerraformCompletionTests(unittest.TestCase):
    def test_completion_checker_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/check_terraform_completion.py"],
            cwd=ROOT,
            check=True,
        )

    def test_manifest_is_exhaustive_and_prunes_all_new_source(self) -> None:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(39, len(data["entries"]))
        self.assertEqual(
            {
                "already_transplanted_or_represented": 22,
                "delete_application_owned": 6,
                "delete_duplicate_or_superseded": 3,
                "delete_live_authority_state_backend": 3,
                "delete_operations_owned": 5,
            },
            dict(Counter(entry["disposition"] for entry in data["entries"])),
        )
        self.assertEqual([], data["retained_new_files"]["retain_literal"])
        self.assertEqual([], data["retained_new_files"]["retain_modified_minimally"])
        self.assertFalse(data["staging_proof"]["raw_source_committed"])

    def test_every_represented_source_has_phase_pr_and_destination(self) -> None:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        represented = [
            entry
            for entry in data["entries"]
            if entry["disposition"] == "already_transplanted_or_represented"
        ]
        self.assertTrue(represented)
        for entry in represented:
            self.assertIn("represented_by", entry)
            self.assertGreater(entry["represented_by"]["phase"], 0)
            self.assertGreater(entry["represented_by"]["pull_request"], 0)
            self.assertTrue(entry["accepted_destination_paths"])


if __name__ == "__main__":
    unittest.main()
