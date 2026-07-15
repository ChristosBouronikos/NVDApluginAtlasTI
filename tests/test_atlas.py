# -*- coding: utf-8 -*-
import os
import sys
import unittest

import nvda_stubs

nvda_stubs.install()

_APPMODULES_DIR = os.path.join(os.path.dirname(__file__), "..", "addon", "appModules")
if _APPMODULES_DIR not in sys.path:
    sys.path.insert(0, _APPMODULES_DIR)

import atlas  # noqa: E402  (must follow stub install)


def _newAppModule():
    """Build an AppModule instance without running NVDA's real __init__."""
    mod = atlas.AppModule.__new__(atlas.AppModule)
    mod._lastPanel = None
    mod._panelCache = {}
    return mod


class FakeObj:
    def __init__(self, role=None, name="", automationId="", className="", parent=None, children=None):
        self.role = role
        self.name = name
        self.UIAAutomationId = automationId
        self.windowClassName = className
        self.parent = parent
        self._children = children or []

    @property
    def recursiveDescendants(self):
        for child in self._children:
            yield child
            for grandchild in child.recursiveDescendants:
                yield grandchild


class NormalizeTokenTests(unittest.TestCase):
    def setUp(self):
        self.mod = _newAppModule()

    def test_lowercases_and_strips_punctuation(self):
        self.assertEqual(self.mod._normalizeToken("Document Manager!"), "documentmanager")

    def test_strips_periods_and_digits_kept(self):
        self.assertEqual(self.mod._normalizeToken("Atlas.ti25"), "atlasti25")

    def test_handles_non_string_input(self):
        self.assertEqual(self.mod._normalizeToken(123), "123")


class TokensMatchTests(unittest.TestCase):
    def setUp(self):
        self.mod = _newAppModule()

    def test_matches_substring_case_insensitive(self):
        tokens = ["CodeManager", "Codes"]
        values = [self.mod._normalizeToken("btnCodeManagerPanel")]
        self.assertTrue(self.mod._tokensMatch(tokens, values))

    def test_no_match_returns_false(self):
        tokens = ["MemoManager"]
        values = [self.mod._normalizeToken("DocumentsPanel")]
        self.assertFalse(self.mod._tokensMatch(tokens, values))

    def test_ignores_falsy_tokens(self):
        self.assertFalse(self.mod._tokensMatch([None, ""], ["documents"]))


class GetPanelTokensTests(unittest.TestCase):
    def setUp(self):
        self.mod = _newAppModule()

    def test_includes_known_tokens_id_and_display_name(self):
        tokens = self.mod._getPanelTokens("DocumentManager", "Documents Panel")
        self.assertIn("DocumentManager", tokens)
        self.assertIn("Documents", tokens)
        self.assertIn("Documents Panel", tokens)

    def test_unknown_panel_id_still_includes_id(self):
        tokens = self.mod._getPanelTokens("Unknown", "Something")
        self.assertEqual(tokens, ["Unknown", "Something"])


class FindPanelByTokensTests(unittest.TestCase):
    def setUp(self):
        self.mod = _newAppModule()

    def test_finds_panel_by_automation_id(self):
        target = FakeObj(automationId="CodeManager")
        container = FakeObj(children=[FakeObj(automationId="Other"), target])
        found = self.mod._findPanelByTokens(container, ["CodeManager", "Codes"])
        self.assertIs(found, target)

    def test_returns_none_when_no_match(self):
        container = FakeObj(children=[FakeObj(automationId="Other")])
        found = self.mod._findPanelByTokens(container, ["CodeManager"])
        self.assertIsNone(found)


class EventForegroundTests(unittest.TestCase):
    """Covers the stale-panel-cache fix: a foreground change must drop
    cached panel references rather than let a wrong-but-alive one survive."""

    def test_clears_panel_cache_and_last_panel(self):
        mod = _newAppModule()
        mod._panelCache = {"DocumentManager": object()}
        mod._lastPanel = "DocumentManager"

        called = []
        mod.event_foreground(obj=None, nextHandler=lambda: called.append(True))

        self.assertEqual(mod._panelCache, {})
        self.assertIsNone(mod._lastPanel)
        self.assertEqual(called, [True])


if __name__ == "__main__":
    unittest.main()
