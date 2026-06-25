"""Regression tests for review_probe.py."""

from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from review_probe import probe_paths


ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "skills/kamae-scala/examples/src/main/scala/kamae/examples/TaxiRequest.scala"


class ReviewProbeTest(unittest.TestCase):
    def test_taxi_request_emits_expected_categories(self) -> None:
        output = probe_paths([EXAMPLE])
        self.assertEqual(len(output.scanned_files), 1)
        self.assertIn("persistence-events", output.summary.leads_by_checklist)
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

    def test_empty_file_produces_no_leads(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".scala", mode="w", delete=False) as f:
            f.write("package empty\n\nobject Empty\n")
            f.flush()
            output = probe_paths([Path(f.name)])
        self.assertEqual(len(output.scanned_files), 1)
        self.assertEqual(len(output.leads), 0)

    def test_throw_detected_as_error_handling_lead(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".scala", mode="w", delete=False) as f:
            f.write(textwrap.dedent("""\
                package probe.test

                object BadService:
                  def process(x: String): String =
                    if x.isEmpty then throw new IllegalArgumentException("empty")
                    else x.toUpperCase
            """))
            f.flush()
            output = probe_paths([Path(f.name)])
        categories = output.summary.leads_by_checklist
        self.assertTrue(
            "error-handling" in categories,
            f"Expected error-handling lead, got: {categories}",
        )

    def test_nowarn_detected_as_fmt_lint_lead(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".scala", mode="w", delete=False) as f:
            f.write(textwrap.dedent("""\
                package probe.test

                import scala.annotation.nowarn

                @nowarn("msg=unused")
                object Suppressed:
                  val x = 42
            """))
            f.flush()
            output = probe_paths([Path(f.name)])
        categories = output.summary.leads_by_checklist
        self.assertTrue(
            "fmt-lint" in categories,
            f"Expected fmt-lint lead, got: {categories}",
        )

    def test_pii_term_detected(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".scala", mode="w", delete=False) as f:
            f.write(textwrap.dedent("""\
                package probe.test

                final case class User(
                    id: String,
                    email: String,
                    socialSecurityNumber: String
                )
            """))
            f.flush()
            output = probe_paths([Path(f.name)])
        categories = output.summary.leads_by_checklist
        self.assertTrue(
            "pii-protection" in categories,
            f"Expected pii-protection lead, got: {categories}",
        )

    def test_suggested_commands_present(self) -> None:
        output = probe_paths([EXAMPLE])
        self.assertGreater(len(output.suggested_commands), 0)
        self.assertTrue(
            any("scalafmt" in cmd for cmd in output.suggested_commands),
            f"Expected scalafmt command, got: {output.suggested_commands}",
        )
