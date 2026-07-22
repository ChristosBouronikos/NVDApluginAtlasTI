# -*- coding: utf-8 -*-
# Author: Christos Bouronikos <chrisbouronikos@gmail.com>
# GitHub: https://github.com/ChristosBouronikos
# Donations: https://paypal.me/christosbouronikos
import json
import os
import sys
import unittest

import nvda_stubs

nvda_stubs.install()

_APPMODULES_DIR = os.path.join(os.path.dirname(__file__), "..", "addon", "appModules")
if _APPMODULES_DIR not in sys.path:
    sys.path.insert(0, _APPMODULES_DIR)

import atlas  # noqa: E402  (must follow stub install)
import _atlastiUI as uiData  # noqa: E402
import config  # noqa: E402  (the stub installed by nvda_stubs)
import ui  # noqa: E402


def _newAppModule():
    """Build an AppModule instance without running NVDA's real __init__."""
    mod = atlas.AppModule.__new__(atlas.AppModule)
    mod._panelCache = {}
    mod._lastPanel = None
    mod._lastContextKey = None
    mod._lastRibbonTab = None
    mod._languageSamples = []
    mod._detectedLanguage = None
    return mod


def _resetConfig():
    config.conf.clear()
    config.conf[atlas.CONFIG_SECTION] = dict(atlas.CONFIG_DEFAULTS)
    # languageHandler is a shared stub module; tests that redirect
    # getLanguage() must not leak that into unrelated tests.
    sys.modules["languageHandler"].getLanguage = lambda: "en"


class FakeObj:
    """Minimal stand-in for an NVDA object."""

    def __init__(self, role=None, name="", automationId="", className="",
                 value="", parent=None, children=None, isAlive=True,
                 columnHeaderText="", description=""):
        self.role = role
        self.name = name
        self.UIAAutomationId = automationId
        self.windowClassName = className
        self.value = value
        self.parent = parent
        self.children = children or []
        self.isAlive = isAlive
        self.columnHeaderText = columnHeaderText
        self.description = description
        self.childCount = len(self.children)
        self.states = set()
        for child in self.children:
            child.parent = self

    @property
    def recursiveDescendants(self):
        for child in self.children:
            yield child
            for grandchild in child.recursiveDescendants:
                yield grandchild

    def setFocus(self):
        atlas.api._focus = self


# =============================================================================
# CONFIG / LANGUAGE HELPERS
# =============================================================================

class ConfigOptionTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()

    def test_getOption_reads_stored_value(self):
        config.conf[atlas.CONFIG_SECTION]["speakHints"] = True
        self.assertTrue(atlas.getOption("speakHints"))

    def test_getOption_falls_back_to_default_on_error(self):
        del config.conf[atlas.CONFIG_SECTION]
        self.assertEqual(atlas.getOption("outputLanguage"), "auto")

    def test_setOption_persists_value(self):
        atlas.setOption("bilingualLabels", False)
        self.assertFalse(config.conf[atlas.CONFIG_SECTION]["bilingualLabels"])

    def test_outputLanguage_explicit_setting_wins(self):
        atlas.setOption("outputLanguage", "el")
        self.assertEqual(atlas.outputLanguage(), "el")

    def test_outputLanguage_auto_follows_nvda_greek(self):
        atlas.setOption("outputLanguage", "auto")
        nvda_stubs_lang = sys.modules["languageHandler"]
        nvda_stubs_lang.getLanguage = lambda: "el_GR"
        self.assertEqual(atlas.outputLanguage(), "el")

    def test_outputLanguage_auto_defaults_to_english(self):
        atlas.setOption("outputLanguage", "auto")
        nvda_stubs_lang = sys.modules["languageHandler"]
        nvda_stubs_lang.getLanguage = lambda: "fr_FR"
        self.assertEqual(atlas.outputLanguage(), "en")


# =============================================================================
# OBJECT RESOLUTION
# =============================================================================

class ResolveTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_resolves_by_automation_id(self):
        obj = FakeObj(automationId="CodeManager")
        element = self.mod._resolve(obj)
        self.assertEqual(element["key"], "managerCodes")

    def test_resolves_by_name_when_no_id(self):
        obj = FakeObj(name="Quotation Manager")
        element = self.mod._resolve(obj)
        self.assertEqual(element["key"], "managerQuotations")

    def test_none_object_resolves_to_none(self):
        self.assertIsNone(self.mod._resolve(None))

    def test_comment_segment_uses_manager_context(self):
        manager = FakeObj(automationId="CodeManager")
        control = FakeObj(role="RADIOBUTTON", name="Comment", parent=manager)
        self.assertEqual(self.mod._resolve(control)["key"], "managerCommentView")


class ContextTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_contextElement_walks_up_to_manager(self):
        manager = FakeObj(automationId="CodeManager", role="LIST")
        row = FakeObj(name="Some code", role="LISTITEM", parent=manager)
        element = self.mod._contextElement(row)
        self.assertEqual(element["key"], "managerCodes")

    def test_contextElement_returns_none_when_nothing_matches(self):
        obj = FakeObj(name="Unrelated")
        self.assertIsNone(self.mod._contextElement(obj))

    def test_inContext_true_when_ancestor_matches(self):
        manager = FakeObj(automationId="QuotationManager")
        child = FakeObj(name="child", parent=manager)
        self.assertTrue(self.mod._inContext(child, atlas.QUOTATION_CONTEXTS))

    def test_inContext_false_when_no_ancestor_matches(self):
        manager = FakeObj(automationId="MemoManager")
        child = FakeObj(name="child", parent=manager)
        self.assertFalse(self.mod._inContext(child, atlas.QUOTATION_CONTEXTS))


class FindElementTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_finds_by_automation_id_over_name_collision(self):
        # A button whose *name* mentions "Codes" should not beat the real
        # Code Manager pane matched by automation id.
        decoyButton = FakeObj(name="Open Codes Manager", automationId="SomeButton")
        target = FakeObj(automationId="CodeManager")
        container = FakeObj(children=[decoyButton, target])
        found = self.mod._findElement(container, ("managerCodes",))
        self.assertIs(found, target)

    def test_returns_none_when_absent(self):
        container = FakeObj(children=[FakeObj(automationId="Other")])
        self.assertIsNone(self.mod._findElement(container, ("managerCodes",)))

    def test_falls_back_to_name_match(self):
        target = FakeObj(name="Memo Manager")
        container = FakeObj(children=[target])
        found = self.mod._findElement(container, ("managerMemos",))
        self.assertIs(found, target)


# =============================================================================
# EVENT HANDLERS
# =============================================================================

class EventForegroundTests(unittest.TestCase):
    """Covers the stale-panel-cache fix: a foreground change must drop
    cached panel references rather than let a wrong-but-alive one survive."""

    def test_clears_panel_cache_and_last_state(self):
        mod = _newAppModule()
        mod._panelCache = {"documents": object()}
        mod._lastPanel = "documents"
        mod._lastContextKey = "managerDocuments"
        mod._lastRibbonTab = "tabHome"

        called = []
        mod.event_foreground(obj=None, nextHandler=lambda: called.append(True))

        self.assertEqual(mod._panelCache, {})
        self.assertIsNone(mod._lastPanel)
        self.assertIsNone(mod._lastContextKey)
        self.assertIsNone(mod._lastRibbonTab)
        self.assertEqual(called, [True])


class NVDAObjectInitTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_labels_unlabeled_known_button_in_english(self):
        atlas.setOption("outputLanguage", "en")
        obj = FakeObj(role="BUTTON", name="", automationId="SaveProject")
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "Save Project")

    def test_labels_unlabeled_known_button_in_greek(self):
        atlas.setOption("outputLanguage", "el")
        atlas.setOption("bilingualLabels", False)
        obj = FakeObj(role="BUTTON", name="", automationId="SaveProject")
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "Κουμπί Αποθήκευση Έργου")

    def test_falls_back_to_description_when_unknown(self):
        obj = FakeObj(role="BUTTON", name="", automationId="TotallyUnknown",
                       description="Some tooltip text")
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "Some tooltip text")

    def test_does_not_touch_already_named_button_in_english_mode(self):
        atlas.setOption("outputLanguage", "en")
        obj = FakeObj(role="BUTTON", name="Custom Existing Name")
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "Custom Existing Name")

    def test_translates_recognised_english_label_to_greek(self):
        atlas.setOption("outputLanguage", "el")
        atlas.setOption("bilingualLabels", False)
        obj = FakeObj(role="BUTTON", name="Code Manager")
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "Κουμπί Διαχειριστής Κωδικών")

    def test_translation_disabled_leaves_name_untouched(self):
        atlas.setOption("outputLanguage", "el")
        atlas.setOption("translateLabels", False)
        obj = FakeObj(role="BUTTON", name="Code Manager")
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "Code Manager")

    def test_does_not_translate_project_content_containing_ui_term(self):
        atlas.setOption("outputLanguage", "el")
        atlas.setOption("bilingualLabels", False)
        obj = FakeObj(role="LISTITEM", name="Interview about codes")
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "Interview about codes")

    def test_does_not_translate_non_exact_control_name(self):
        atlas.setOption("outputLanguage", "el")
        atlas.setOption("bilingualLabels", False)
        obj = FakeObj(role="BUTTON", name="Open Code Manager")
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "Open Code Manager")

    def test_labeling_disabled_leaves_unlabeled_button_alone(self):
        atlas.setOption("labelUnlabeledButtons", False)
        obj = FakeObj(role="BUTTON", name="", automationId="SaveProject")
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "")

    def test_never_raises_on_broken_object(self):
        class Broken:
            @property
            def role(self):
                raise RuntimeError("boom")

        # Must not propagate.
        self.mod.event_NVDAObject_init(Broken())

    def test_greek_menu_item_includes_greek_role_when_nvda_is_english(self):
        atlas.setOption("outputLanguage", "el")
        atlas.setOption("bilingualLabels", False)
        manager = FakeObj(automationId="CodeManager")
        obj = FakeObj(role="MENUITEM", name="Change Color", parent=manager)
        self.mod.event_NVDAObject_init(obj)
        self.assertEqual(obj.name, "Στοιχείο μενού Αλλαγή χρώματος")


# =============================================================================
# READING: honesty of context-checked commands
# =============================================================================

class ReadEntityTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()
        self.messages = []
        self._origMessage = ui.message
        ui.message = lambda msg: self.messages.append(msg)

    def tearDown(self):
        ui.message = self._origMessage

    def test_reads_code_when_in_code_context(self):
        manager = FakeObj(automationId="CodeManager")
        row = FakeObj(name="Sustainability", parent=manager)
        atlas.api.getFocusObject = lambda: row
        self.mod.script_readCode(None)
        self.assertEqual(self.messages, ["Code: Sustainability"])

    def test_refuses_to_read_code_when_not_in_code_context(self):
        manager = FakeObj(automationId="MemoManager")
        row = FakeObj(name="Some memo", parent=manager)
        atlas.api.getFocusObject = lambda: row
        self.mod.script_readCode(None)
        self.assertEqual(len(self.messages), 1)
        self.assertIn("not on a code", self.messages[0])

    def test_reads_quotation_when_in_quotation_context(self):
        manager = FakeObj(automationId="QuotationManager")
        row = FakeObj(value="Some excerpt text", parent=manager)
        atlas.api.getFocusObject = lambda: row
        self.mod.script_readQuotation(None)
        self.assertEqual(self.messages, ["Quotation: Some excerpt text"])


# =============================================================================
# ROW READING
# =============================================================================

class RowCellsTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_extracts_header_and_text_pairs(self):
        cellA = FakeObj(value="3", columnHeaderText="ID")
        cellB = FakeObj(value="Interview 1", columnHeaderText="Name")
        row = FakeObj(role="LISTITEM", children=[cellA, cellB])
        cells = self.mod._rowCells(row)
        self.assertEqual(cells[0][1], "3")
        self.assertEqual(cells[1][1], "Interview 1")
        # Column header text should be translated via the UI table.
        self.assertEqual(cells[0][0], "Column ID")
        self.assertEqual(cells[1][0], "Column Name")

    def test_non_row_returns_empty_list(self):
        obj = FakeObj(role="BUTTON")
        self.assertEqual(self.mod._rowCells(obj), [])

    def test_falls_back_to_row_name_when_no_cell_children(self):
        row = FakeObj(role="LISTITEM", name="Whole row text", children=[])
        cells = self.mod._rowCells(row)
        self.assertEqual(cells, [(None, "Whole row text")])

    def test_start_header_is_column_not_german_home_tab(self):
        atlas.setOption("outputLanguage", "el")
        atlas.setOption("bilingualLabels", False)
        cell = FakeObj(value="00:15", columnHeaderText="Start")
        row = FakeObj(role="LISTITEM", children=[cell])
        self.assertEqual(self.mod._rowCells(row), [("Στήλη Έναρξη", "00:15")])


class DialogOverlayTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_import_dialog_descendant_gets_import_overlay(self):
        dialog = FakeObj(role="DIALOG", automationId="ImportDialog")
        child = FakeObj(role="BUTTON", name="Import", parent=dialog)
        classes = []
        self.mod.chooseNVDAObjectOverlayClasses(child, classes)
        self.assertEqual(classes, [atlas.AtlasImportDialogOverlay])

    def test_all_five_dialog_families_have_distinct_overlays(self):
        expected = {
            "ImportDialog": atlas.AtlasImportDialogOverlay,
            "SearchDialog": atlas.AtlasSearchDialogOverlay,
            "QueryDialog": atlas.AtlasQueryDialogOverlay,
            "ReportDialog": atlas.AtlasReportDialogOverlay,
            "ConfirmationDialog": atlas.AtlasConfirmationDialogOverlay,
        }
        for automationId, overlay in expected.items():
            classes = []
            self.mod.chooseNVDAObjectOverlayClasses(
                FakeObj(role="DIALOG", automationId=automationId), classes)
            self.assertEqual(classes, [overlay], msg=automationId)

    def test_welcome_screen_descendant_gets_welcome_overlay(self):
        welcome = FakeObj(role="WINDOW", automationId="WelcomeScreen")
        child = FakeObj(role="BUTTON", automationId="WelcomeNews", parent=welcome)
        classes = []
        self.mod.chooseNVDAObjectOverlayClasses(child, classes)
        self.assertEqual(classes, [atlas.AtlasWelcomeScreenOverlay])

    def test_quotation_reader_descendant_gets_reader_overlay(self):
        reader = FakeObj(role="WINDOW", automationId="QuotationReader")
        child = FakeObj(role="RADIOBUTTON", automationId="QuotationReaderSingleLine",
                        parent=reader)
        classes = []
        self.mod.chooseNVDAObjectOverlayClasses(child, classes)
        self.assertEqual(classes, [atlas.AtlasQuotationReaderOverlay])

    def test_manager_filter_gets_specific_filter_overlay(self):
        manager = FakeObj(role="WINDOW", automationId="CodeManager")
        child = FakeObj(role="CHECKBOX", automationId="FilterToday", parent=manager)
        classes = []
        self.mod.chooseNVDAObjectOverlayClasses(child, classes)
        self.assertEqual(classes, [atlas.AtlasManagerFilterOverlay])

    def test_manager_context_item_gets_context_menu_overlay(self):
        manager = FakeObj(role="WINDOW", automationId="CodeManager")
        child = FakeObj(role="MENUITEM", name="Unknown future command", parent=manager)
        classes = []
        self.mod.chooseNVDAObjectOverlayClasses(child, classes)
        self.assertEqual(classes, [atlas.AtlasManagerContextMenuOverlay])

    def test_ordinary_manager_child_gets_manager_overlay(self):
        manager = FakeObj(role="WINDOW", automationId="CodeManager")
        child = FakeObj(role="BUTTON", automationId="NewCode", parent=manager)
        classes = []
        self.mod.chooseNVDAObjectOverlayClasses(child, classes)
        self.assertEqual(classes, [atlas.AtlasManagerOverlay])

    def test_overlay_marker_does_not_hide_the_controls_own_identity(self):
        class WelcomeControl(atlas.AtlasWelcomeScreenOverlay, FakeObj):
            pass

        control = WelcomeControl(role="BUTTON", automationId="WelcomeNews")
        self.assertEqual(self.mod._rawResolve(control)["key"], "welcomeNews")

    def test_dialog_overlay_marker_is_only_a_context_fallback(self):
        class ImportControl(atlas.AtlasImportDialogOverlay, FakeObj):
            pass

        control = ImportControl(role="BUTTON", automationId="DialogImport")
        self.assertEqual(self.mod._rawResolve(control)["key"], "dialogImport")


class StateAnnouncementTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()
        self.messages = []
        self.originalMessage = ui.message
        ui.message = self.messages.append

    def tearDown(self):
        ui.message = self.originalMessage

    def test_state_change_is_translated_when_output_differs_from_nvda(self):
        atlas.setOption("outputLanguage", "el")
        manager = FakeObj(role="WINDOW", automationId="CodeManager")
        control = FakeObj(role="CHECKBOX", automationId="FilterToday", parent=manager)
        control.states = {"CHECKED", "EXPANDED"}
        called = []
        self.mod.event_stateChange(control, lambda: called.append(True))
        self.assertEqual(called, [True])
        self.assertEqual(self.messages, ["Τσεκαρισμένο, Αναπτυγμένο"])

    def test_state_change_does_not_duplicate_native_language(self):
        atlas.setOption("outputLanguage", "en")
        control = FakeObj(role="BUTTON", automationId="SaveProject")
        control.states = {"PRESSED"}
        self.mod.event_stateChange(control, lambda: None)
        self.assertEqual(self.messages, [])


class SafeUICaptureTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_capture_records_controls_but_prunes_research_lists(self):
        hiddenResearchButton = FakeObj(
            role="BUTTON", name="Interview participant private name")
        researchList = FakeObj(
            role="LIST", name="Documents", children=[hiddenResearchButton])
        safeButton = FakeObj(
            role="BUTTON", name="Save Project", automationId="SaveProject")
        window = FakeObj(role="WINDOW", name="ATLAS.ti", children=[
            researchList, safeButton])
        records = self.mod._safeUICaptureRecords(window)
        names = [record["name"] for record in records]
        self.assertIn("Save Project", names)
        self.assertNotIn("Documents", names)
        self.assertNotIn("Interview participant private name", names)
        self.assertTrue(all("value" not in record for record in records))
        saveRecord = next(record for record in records if record["name"] == "Save Project")
        self.assertEqual(saveRecord["contextKeys"], [])

    def test_capture_redacts_unknown_window_title_that_may_hold_project_name(self):
        window = FakeObj(role="WINDOW", name="ATLAS.ti - Confidential Study")
        records = self.mod._safeUICaptureRecords(window)
        self.assertEqual(records[0]["name"], "")

    def test_capture_command_is_disabled_until_user_opts_in(self):
        messages = []
        original = ui.message
        ui.message = messages.append
        try:
            self.mod.script_captureSafeUITree(None)
        finally:
            ui.message = original
        self.assertEqual(len(messages), 1)
        self.assertIn("disabled", messages[0])

    def test_privacy_corpus_is_completely_pruned(self):
        path = os.path.join(os.path.dirname(__file__), "privacy_capture_cases.json")
        with open(path, "r", encoding="utf-8") as stream:
            cases = json.load(stream)
        for case in cases:
            sensitiveChildren = [
                FakeObj(role="BUTTON", name=name, automationId="DynamicResearchItem")
                for name in case["sensitiveNames"]
            ]
            container = FakeObj(
                role=case["containerRole"], name=case["containerName"],
                children=sensitiveChildren)
            safe = FakeObj(role="BUTTON", name="Save Project", automationId="SaveProject")
            window = FakeObj(role="WINDOW", name="ATLAS.ti", children=[container, safe])
            records = self.mod._safeUICaptureRecords(window)
            capturedNames = {record["name"] for record in records}
            for sensitiveName in case["sensitiveNames"]:
                self.assertNotIn(sensitiveName, capturedNames, msg=case["containerRole"])
            self.assertNotIn(case["containerName"], capturedNames)
            self.assertIn("Save Project", capturedNames)


# =============================================================================
# NAVIGATION
# =============================================================================

class NavigateToTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()
        self.messages = []
        self._origMessage = ui.message
        ui.message = lambda msg: self.messages.append(msg)
        self._origFocus = atlas.api.getFocusObject
        self._origForeground = atlas.api.getForegroundObject

    def tearDown(self):
        ui.message = self._origMessage
        atlas.api.getFocusObject = self._origFocus
        atlas.api.getForegroundObject = self._origForeground

    def test_reports_not_found_when_panel_absent(self):
        window = FakeObj(role="WINDOW", children=[])
        atlas.api.getForegroundObject = lambda: window
        atlas.api.getFocusObject = lambda: window
        self.mod._navigateTo("codes")
        self.assertEqual(len(self.messages), 1)
        self.assertIn("not found", self.messages[0])

    def test_focuses_panel_and_announces_success(self):
        panel = FakeObj(automationId="CodeManager")
        window = FakeObj(role="WINDOW", children=[panel])
        atlas.api.getForegroundObject = lambda: window
        atlas.api.getFocusObject = lambda: panel  # focus verification sees panel
        self.mod._navigateTo("codes")
        self.assertEqual(self.messages, ["Code Manager"])
        self.assertEqual(self.mod._lastPanel, "managerCodes")

    def test_caches_panel_and_reuses_it(self):
        panel = FakeObj(automationId="CodeManager")
        window = FakeObj(role="WINDOW", children=[panel])
        atlas.api.getForegroundObject = lambda: window
        atlas.api.getFocusObject = lambda: panel
        self.mod._navigateTo("codes")
        self.assertIn("codes", self.mod._panelCache)
        cached = self.mod._cachedPanel("codes")
        self.assertIs(cached, panel)

    def test_falls_back_to_navigator_when_focus_does_not_move(self):
        panel = FakeObj(automationId="CodeManager")
        window = FakeObj(role="WINDOW", children=[panel])
        atlas.api.getForegroundObject = lambda: window
        # Focus never actually reaches the panel.
        unrelated = FakeObj(name="somewhere else")
        atlas.api.getFocusObject = lambda: unrelated
        navSet = []
        atlas.api.setNavigatorObject = lambda obj: navSet.append(obj)
        self.mod._navigateTo("codes")
        self.assertEqual(navSet, [panel])
        self.assertIn("navigator object moved", self.messages[0])

    def test_recovers_focus_to_first_usable_descendant(self):
        class NonFocusingPanel(FakeObj):
            def setFocus(self):
                pass

        child = FakeObj(role="LIST", name="Code list")
        panel = NonFocusingPanel(automationId="CodeManager", children=[child])
        window = FakeObj(role="WINDOW", children=[panel])
        unrelated = FakeObj(name="somewhere else")
        atlas.api._focus = unrelated
        atlas.api.getForegroundObject = lambda: window
        atlas.api.getFocusObject = lambda: atlas.api._focus
        navSet = []
        atlas.api.setNavigatorObject = navSet.append
        self.mod._navigateTo("codes")
        self.assertIs(atlas.api._focus, child)
        self.assertEqual(navSet, [])
        self.assertEqual(self.messages, ["Code Manager"])

    def test_skips_unavailable_descendant_during_focus_recovery(self):
        blocked = FakeObj(role="BUTTON", name="Unavailable")
        blocked.states = {"UNAVAILABLE"}
        usable = FakeObj(role="BUTTON", automationId="NewCode")
        panel = FakeObj(automationId="CodeManager", children=[blocked, usable])
        self.assertTrue(self.mod._focusFirstUsableDescendant(panel))
        self.assertIs(atlas.api._focus, usable)

    def test_focus_recovery_prefers_data_view_over_toolbar_button(self):
        toolbarButton = FakeObj(role="BUTTON", automationId="NewCode")
        dataList = FakeObj(role="LIST", name="Code list")
        panel = FakeObj(automationId="CodeManager", children=[toolbarButton, dataList])
        self.assertTrue(self.mod._focusFirstUsableDescendant(panel))
        self.assertIs(atlas.api._focus, dataList)


# =============================================================================
# CHARTS AND DIAGRAMS: honest reading, real content when it exists
# =============================================================================

class FindVisualAncestorTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_finds_self_when_focus_is_on_the_visual_control_itself(self):
        obj = FakeObj(automationId="NetworkEditor")
        found, element = self.mod._findVisualAncestor(obj)
        self.assertIs(found, obj)
        self.assertEqual(element["key"], "networkEditor")

    def test_finds_ancestor_when_focus_is_on_a_child(self):
        container = FakeObj(automationId="WordCloud")
        child = FakeObj(name="some fragment", parent=container)
        found, element = self.mod._findVisualAncestor(child)
        self.assertIs(found, container)
        self.assertEqual(element["key"], "wordCloud")

    def test_ordinary_control_yields_none(self):
        obj = FakeObj(automationId="CodeManager")
        found, element = self.mod._findVisualAncestor(obj)
        self.assertIsNone(found)
        self.assertIsNone(element)


class VisualContentTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_finds_real_named_content_when_exposed(self):
        node1 = FakeObj(role="GRAPHIC", name="Code: Sustainability")
        node2 = FakeObj(role="STATICTEXT", name="Code: Barriers")
        container = FakeObj(automationId="NetworkEditor", children=[node1, node2])
        found = self.mod._visualContent(container)
        self.assertEqual(found, ["Code: Sustainability", "Code: Barriers"])

    def test_returns_empty_when_no_content_bearing_roles_present(self):
        chrome = FakeObj(role="BUTTON", name="Zoom in")
        container = FakeObj(automationId="NetworkEditor", children=[chrome])
        # A zoom button is UI chrome, not chart content -- BUTTON is not in
        # the content-role set, so it must not be reported as content.
        found = self.mod._visualContent(container)
        self.assertEqual(found, [])

    def test_ignores_the_containers_own_name_and_duplicates(self):
        dupe = FakeObj(role="GRAPHIC", name="Same label")
        dupeAgain = FakeObj(role="GRAPHIC", name="Same label")
        echo = FakeObj(role="GRAPHIC", name="Network Editor")
        container = FakeObj(automationId="NetworkEditor", name="Network Editor",
                             children=[dupe, dupeAgain, echo])
        found = self.mod._visualContent(container)
        self.assertEqual(found, ["Same label"])


class DescribeVisualScriptTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        atlas.setOption("outputLanguage", "en")
        self.mod = _newAppModule()
        self.messages = []
        self.shown = []
        self._origMessage = ui.message
        self._origBrowse = ui.browseableMessage
        ui.message = lambda msg: self.messages.append(msg)
        ui.browseableMessage = lambda text, title: self.shown.append((title, text))

    def tearDown(self):
        ui.message = self._origMessage
        ui.browseableMessage = self._origBrowse

    def test_non_visual_focus_reports_plainly(self):
        atlas.api.getFocusObject = lambda: FakeObj(automationId="CodeManager")
        self.mod.script_describeVisual(None)
        self.assertEqual(len(self.messages), 1)
        self.assertIn("not a chart", self.messages[0])

    def test_visual_with_no_content_explains_concept_and_points_to_companion(self):
        emptyChart = FakeObj(automationId="NetworkEditor", children=[])
        atlas.api.getFocusObject = lambda: emptyChart
        self.mod.script_describeVisual(None)
        self.assertEqual(len(self.messages), 1)
        message = self.messages[0]
        self.assertIn("Network Editor", message)
        self.assertIn("does not expose", message)
        self.assertIn("Link Manager", message)  # the companion

    def test_visual_with_real_content_is_shown_as_a_browsable_list(self):
        node = FakeObj(role="GRAPHIC", name="Code: Sustainability")
        chart = FakeObj(automationId="NetworkEditor", children=[node])
        atlas.api.getFocusObject = lambda: chart
        self.mod.script_describeVisual(None)
        self.assertEqual(self.messages, [])  # spoken via browseableMessage, not ui.message
        self.assertEqual(len(self.shown), 1)
        title, text = self.shown[0]
        self.assertIn("Network Editor", title)
        self.assertIn("Code: Sustainability", text)


class GoToDataViewScriptTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()
        self.messages = []
        self._origMessage = ui.message
        ui.message = lambda msg: self.messages.append(msg)
        self._origFocus = atlas.api.getFocusObject
        self._origForeground = atlas.api.getForegroundObject

    def tearDown(self):
        ui.message = self._origMessage
        atlas.api.getFocusObject = self._origFocus
        atlas.api.getForegroundObject = self._origForeground

    def test_non_visual_focus_reports_plainly(self):
        atlas.api.getFocusObject = lambda: FakeObj(automationId="CodeManager")
        self.mod.script_goToDataView(None)
        self.assertEqual(len(self.messages), 1)
        self.assertIn("not a chart", self.messages[0])

    def test_no_known_companion_is_reported_honestly(self):
        atlas.api.getFocusObject = lambda: FakeObj(automationId="NetworkEditor")
        original = uiData.companion
        uiData.companion = lambda element: None
        try:
            self.mod.script_goToDataView(None)
        finally:
            uiData.companion = original
        self.assertEqual(len(self.messages), 1)
        self.assertIn("No accessible alternative", self.messages[0])

    def test_jumps_to_the_companion_element(self):
        # Focus resolution (found the panel) is what this test checks, not
        # whether the synchronous focus-verification round-trip succeeds --
        # that path is already covered by NavigateToTests.
        linkManagerPanel = FakeObj(automationId="LinkManager")
        window = FakeObj(role="WINDOW", children=[linkManagerPanel])
        chart = FakeObj(automationId="NetworkEditor")
        atlas.api.getForegroundObject = lambda: window
        atlas.api.getFocusObject = lambda: chart
        self.mod.script_goToDataView(None)
        self.assertIn("companion:managerLinks", self.mod._panelCache)
        self.assertIs(self.mod._panelCache["companion:managerLinks"](), linkManagerPanel)


class VisualViewModeWarningTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()

    def test_warns_when_a_visual_view_mode_is_selected(self):
        cloudToggle = FakeObj(automationId="ViewCloud", role="RADIOBUTTON")
        cloudToggle.states.add("SELECTED")
        manager = FakeObj(automationId="CodeManager", children=[cloudToggle])
        warning = self.mod._visualViewModeWarning(manager)
        self.assertIsNotNone(warning)
        self.assertIn("Cloud view", warning)

    def test_no_warning_when_list_view_is_selected(self):
        listToggle = FakeObj(automationId="ListView", role="RADIOBUTTON")
        listToggle.states.add("SELECTED")
        manager = FakeObj(automationId="CodeManager", children=[listToggle])
        warning = self.mod._visualViewModeWarning(manager)
        self.assertIsNone(warning)

    def test_no_warning_when_toggle_is_not_selected(self):
        cloudToggle = FakeObj(automationId="ViewCloud", role="RADIOBUTTON")
        manager = FakeObj(automationId="CodeManager", children=[cloudToggle])
        warning = self.mod._visualViewModeWarning(manager)
        self.assertIsNone(warning)

    def test_navigate_to_codes_includes_view_mode_warning(self):
        cloudToggle = FakeObj(automationId="ViewCloud", role="RADIOBUTTON")
        cloudToggle.states.add("SELECTED")
        codePanel = FakeObj(automationId="CodeManager", children=[cloudToggle])
        window = FakeObj(role="WINDOW", children=[codePanel])
        atlas.api.getForegroundObject = lambda: window
        atlas.api.getFocusObject = lambda: codePanel
        messages = []
        origMessage = ui.message
        ui.message = lambda msg: messages.append(msg)
        try:
            self.mod._navigateTo("codes")
        finally:
            ui.message = origMessage
        self.assertEqual(len(messages), 1)
        self.assertIn("Code Manager", messages[0])
        self.assertIn("Cloud view", messages[0])


# =============================================================================
# GLOSSARY / HELP DO NOT CRASH
# =============================================================================

class GlossaryAndHelpTests(unittest.TestCase):
    def setUp(self):
        _resetConfig()
        self.mod = _newAppModule()
        self.shown = []
        self._orig = ui.browseableMessage
        ui.browseableMessage = lambda text, title: self.shown.append((title, text))

    def tearDown(self):
        ui.browseableMessage = self._orig

    def test_glossary_lists_every_element(self):
        self.mod.script_showGlossary(None)
        self.assertEqual(len(self.shown), 1)
        _, text = self.shown[0]
        for key, element in uiData.ELEMENTS.items():
            self.assertIn(element["en"], text, msg=key)

    def test_shortcut_list_does_not_raise(self):
        self.mod.script_listShortcuts(None)
        self.assertEqual(len(self.shown), 1)


if __name__ == "__main__":
    unittest.main()
