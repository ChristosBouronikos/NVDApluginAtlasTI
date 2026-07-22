# -*- coding: utf-8 -*-
"""Tests for documentation-catalogue and Windows capture reconciliation."""

import importlib.util
import json
import os
import unittest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "compare_ui_capture.py")
spec = importlib.util.spec_from_file_location("compare_ui_capture", SCRIPT)
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class CaptureParserTests(unittest.TestCase):
    def test_parses_nvda_log_repr_lines(self):
        text = "INFO Atlas.ti UI control: {'depth': 2, 'name': 'Save Project', " \
               "'role': 'BUTTON', 'automationId': 'SaveProject', " \
               "'className': 'Button', 'recognisedAs': 'saveProject'}"
        records = capture.parseCaptureText(text)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["automationId"], "SaveProject")

    def test_parses_json_capture(self):
        records = capture.parseCaptureText(
            '[{"name":"Home","role":"TAB","automationId":"HomeTab"}]')
        self.assertEqual(records[0]["name"], "Home")

    def test_ignores_unrelated_or_malformed_log_lines(self):
        self.assertEqual(capture.parseCaptureText("INFO unrelated\n{broken"), [])


class CaptureComparisonTests(unittest.TestCase):
    def test_known_control_matches_without_warnings(self):
        report = capture.compareRecords([{
            "depth": 1,
            "name": "Save Project",
            "role": "Role.BUTTON",
            "automationId": "SaveProject",
            "className": "Button",
            "recognisedAs": None,
        }])
        self.assertEqual(report["summary"]["matchedControls"], 1)
        self.assertEqual(report["summary"]["unknownControls"], 0)
        self.assertEqual(report["summary"]["wrongRoles"], 0)

    def test_unknown_control_is_reported(self):
        report = capture.compareRecords([{
            "depth": 1,
            "name": "Brand New ATLAS Control",
            "role": "BUTTON",
            "automationId": "NewControl2026",
            "className": "Button",
            "recognisedAs": None,
        }])
        self.assertEqual(report["summary"]["unknownControls"], 1)

    def test_role_mismatch_is_reported(self):
        report = capture.compareRecords([{
            "depth": 1,
            "name": "Change Color",
            "role": "BUTTON",
            "automationId": "ContextChangeColor",
            "className": "",
            "recognisedAs": "menuChangeColor",
        }])
        self.assertEqual(report["summary"]["wrongRoles"], 1)
        self.assertEqual(report["wrongRoles"][0]["expectedRoles"], ["MENUITEM"])

    def test_changed_id_is_reported_when_name_matches(self):
        report = capture.compareRecords([{
            "depth": 1,
            "name": "Save Project",
            "role": "BUTTON",
            "automationId": "SaveProjectV26Changed",
            "className": "",
            "recognisedAs": None,
        }])
        self.assertEqual(report["summary"]["changedAutomationIds"], 1)

    def test_ambiguous_name_uses_role_and_manager_context(self):
        report = capture.compareRecords([{
            "depth": 2,
            "name": "Comment",
            "role": "RADIOBUTTON",
            "automationId": "ChangedCommentSegmentId",
            "className": "",
            "recognisedAs": None,
            "contextKeys": ["managerCodes"],
        }])
        self.assertEqual(report["matched"][0]["key"], "managerCommentView")

    def test_markdown_report_contains_actionable_sections(self):
        report = capture.compareRecords([])
        markdown = capture.markdownReport(report)
        self.assertIn("Unknown controls", markdown)
        self.assertIn("Role mismatches", markdown)
        self.assertIn("Changed automation IDs", markdown)

    def test_checked_in_json_catalogue_is_current(self):
        path = os.path.join(ROOT, "docs", "atlasti26_ui_catalogue.json")
        with open(path, "r", encoding="utf-8") as stream:
            payload = json.load(stream)
        self.assertEqual(payload["manualVersion"], capture.uiData.MANUAL_VERSION)
        self.assertEqual(len(payload["controls"]), len(capture.uiData.ELEMENTS))
        self.assertEqual(
            {item["key"] for item in payload["controls"]},
            set(capture.uiData.ELEMENTS),
        )
        expected = json.loads(json.dumps({
            "schemaVersion": 1,
            "manualVersion": capture.uiData.MANUAL_VERSION,
            "manualRoot": capture.uiData.MANUAL_ROOT,
            "surfaces": capture.uiData.DOCUMENTED_SURFACES,
            "controls": capture.uiData.catalogueRecords(),
        }, ensure_ascii=False))
        self.assertEqual(payload, expected)


if __name__ == "__main__":
    unittest.main()
