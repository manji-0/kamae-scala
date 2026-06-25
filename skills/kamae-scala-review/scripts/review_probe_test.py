"""Regression tests for review_probe.py."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from review_probe import probe_paths


ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "skills/kamae-scala/examples/src/main/scala/kamae/examples/TaxiRequest.scala"


class ReviewProbeTest(unittest.TestCase):
    def test_taxi_request_emits_expected_categories(self) -> None:
        output = probe_paths([EXAMPLE])
        self.assertEqual(len(output.scanned_files), 1)
        self.assertIn("persistence-events", output.summary.leads_by_category)
        self.assertGreaterEqual(output.summary.public_items, 8)
        self.assertGreater(output.summary.public_items_missing_docs, 0)

    def test_json_output_shape(self) -> None:
        output = probe_paths([EXAMPLE])
        payload = json.loads(json.dumps(
            {
                "scanned_files": output.scanned_files,
                "summary": output.summary.__dict__,
                "suggested_commands": output.suggested_commands,
                "leads": [lead.__dict__ for lead in output.leads],
                "public_items": [item.__dict__ for item in output.public_items],
            }
        ))
        self.assertIn("scanned_files", payload)
        self.assertIn("summary", payload)
        self.assertIn("suggested_commands", payload)
        self.assertIn("leads", payload)
        self.assertIn("public_items", payload)

    def test_skips_target_directory(self) -> None:
        output = probe_paths([ROOT / "skills/kamae-scala/examples"])
        scanned = "\n".join(output.scanned_files)
        self.assertNotIn("/target/", scanned.replace("\\", "/"))


if __name__ == "__main__":
    unittest.main()
