"""Unit tests for the diagnostic tool."""

import json
import tempfile
import unittest
from pathlib import Path

from machine_diag.cli import (
    collect_diagnostics,
    format_text_report,
    inspect_disk,
    load_config,
)


class DiagnosticToolTests(unittest.TestCase):
    def test_disk_report_has_expected_fields(self):
        result = inspect_disk(".")
        self.assertIn("total_bytes", result)
        self.assertIn("free_bytes", result)
        self.assertIsInstance(result["free_gb"], (float, int))

    def test_config_not_requested(self):
        result = load_config(None)
        self.assertEqual(result["status"], "not_requested")

    def test_valid_config(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text(json.dumps({"project": "demo"}), encoding="utf-8")
            result = load_config(path)
            self.assertEqual(result["status"], "valid")
            self.assertEqual(result["data"]["project"], "demo")

    def test_missing_config(self):
        with tempfile.TemporaryDirectory() as folder:
            result = load_config(Path(folder) / "missing.json")
            self.assertEqual(result["status"], "missing")
            self.assertIsNotNone(result["error"])

    def test_malformed_config(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            path.write_text("{not valid json", encoding="utf-8")
            result = load_config(path)
            self.assertEqual(result["status"], "malformed")

    def test_report_contains_required_sections(self):
        report = collect_diagnostics()
        self.assertIn("system", report)
        self.assertIn("disk", report)
        self.assertIn("environment", report)
        self.assertIn("developer_tools", report)
        self.assertIn("configuration", report)

    def test_text_report_is_readable(self):
        report = collect_diagnostics()
        text = format_text_report(report)
        self.assertIn("PYTHON SYSTEM DIAGNOSTIC REPORT", text)
        self.assertIn("DEVELOPER TOOLS", text)


if __name__ == "__main__":
    unittest.main()
