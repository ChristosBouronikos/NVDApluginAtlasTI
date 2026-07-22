# -*- coding: utf-8 -*-
"""Tests for executable registration performed by the global plugin."""
import importlib.util
import os
import sys
import unittest

import nvda_stubs

nvda_stubs.install()

_ADDON_DIR = os.path.join(os.path.dirname(__file__), "..", "addon")
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

from globalPlugins import atlastiHelper  # noqa: E402
import appModuleHandler  # noqa: E402


class ExecutableRegistrationTests(unittest.TestCase):
    def setUp(self):
        appModuleHandler.registeredExecutableAppModules.clear()

    def test_registers_every_normalised_executable_with_atlas_module(self):
        plugin = atlastiHelper.GlobalPlugin()
        expected = {name.lower() for name in atlastiHelper.ATLAS_TI_EXECUTABLES}
        self.assertEqual(
            set(appModuleHandler.registeredExecutableAppModules), expected)
        self.assertEqual(
            set(appModuleHandler.registeredExecutableAppModules.values()), {"atlas"})
        plugin.terminate()

    def test_unregisters_executables_on_termination(self):
        plugin = atlastiHelper.GlobalPlugin()
        self.assertTrue(appModuleHandler.registeredExecutableAppModules)
        plugin.terminate()
        self.assertEqual(appModuleHandler.registeredExecutableAppModules, {})

    def test_dotted_executable_fallback_aliases_exist(self):
        for moduleName in (
            "atlas_ti", "atlas_ti9", "atlas_ti22", "atlas_ti23",
            "atlas_ti24", "atlas_ti25", "atlas_ti26",
        ):
            with self.subTest(moduleName=moduleName):
                self.assertIsNotNone(
                    importlib.util.find_spec("appModules." + moduleName))

    def test_safe_ui_capture_is_registered_as_opt_in(self):
        self.assertEqual(
            atlastiHelper.CONFIG_SPEC["enableSafeUICapture"],
            "boolean(default=False)")

    def test_translated_state_announcements_are_enabled_by_default(self):
        self.assertEqual(
            atlastiHelper.CONFIG_SPEC["announceControlStates"],
            "boolean(default=True)")


if __name__ == "__main__":
    unittest.main()
