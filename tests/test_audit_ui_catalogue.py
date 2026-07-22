# -*- coding: utf-8 -*-
"""Tests for the release-time bilingual catalogue audit."""

import importlib.util
import os
import unittest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "audit_ui_catalogue.py")
spec = importlib.util.spec_from_file_location("audit_ui_catalogue", SCRIPT)
auditModule = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditModule)


class CatalogueAuditTests(unittest.TestCase):
    def test_catalogue_has_no_release_blocking_issues(self):
        self.assertEqual(auditModule.audit(), [])

    def test_summary_covers_requested_inventory(self):
        summary = auditModule.summary()
        self.assertGreaterEqual(summary["kinds"]["button"], 116)
        self.assertGreaterEqual(summary["kinds"]["column"], 22)
        self.assertGreaterEqual(summary["kinds"]["panel"], 18)
        self.assertEqual(summary["kinds"]["manager"], 11)
        self.assertEqual(summary["kinds"]["tab"], 11)
        self.assertEqual(summary["unresolvedCollisions"], 0)


if __name__ == "__main__":
    unittest.main()
