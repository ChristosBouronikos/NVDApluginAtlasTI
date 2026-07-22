# -*- coding: utf-8 -*-
# Author: Christos Bouronikos <chrisbouronikos@gmail.com>
# GitHub: https://github.com/ChristosBouronikos
# Donations: https://paypal.me/christosbouronikos
"""Tests for the pure ATLAS.ti UI knowledge base (_atlastiUI.py)."""
import os
import sys
import unittest

_APPMODULES_DIR = os.path.join(os.path.dirname(__file__), "..", "addon", "appModules")
if _APPMODULES_DIR not in sys.path:
    sys.path.insert(0, _APPMODULES_DIR)

import _atlastiUI as uiData  # noqa: E402


class NormalizeTests(unittest.TestCase):
    def test_lowercases_and_strips_punctuation(self):
        self.assertEqual(uiData.normalize("Document Manager!"), "documentmanager")

    def test_strips_periods_digits_kept(self):
        self.assertEqual(uiData.normalize("Atlas.ti25"), "atlasti25")

    def test_handles_non_string_input(self):
        self.assertEqual(uiData.normalize(123), "123")

    def test_greek_text_is_preserved_not_stripped(self):
        # v1.1.0 regression: the old normaliser kept only [a-z0-9] and
        # reduced every Greek string to "". Greek must survive here.
        result = uiData.normalize("Πίνακας Κωδικών")
        self.assertNotEqual(result, "")
        self.assertIn("κωδικων", result)

    def test_case_and_accent_and_final_sigma_insensitive(self):
        a = uiData.normalize("Κωδικός")
        b = uiData.normalize("ΚΩΔΙΚΟΣ")
        c = uiData.normalize("κωδικος")
        self.assertEqual(a, b)
        self.assertEqual(b, c)


class ResolveTests(unittest.TestCase):
    def test_resolves_by_automation_id_exact(self):
        element = uiData.resolve("CodeManager")
        self.assertIsNotNone(element)
        self.assertEqual(element["key"], "managerCodes")

    def test_resolves_by_english_display_name(self):
        element = uiData.resolve("Code Manager")
        self.assertEqual(element["key"], "managerCodes")

    def test_resolves_by_german_alias(self):
        element = uiData.resolve("Kode-Manager")
        self.assertEqual(element["key"], "managerCodes")

    def test_resolves_by_spanish_alias(self):
        element = uiData.resolve("Administrador de Códigos")
        self.assertEqual(element["key"], "managerCodes")

    def test_prefers_earlier_candidate_when_both_match_exactly(self):
        # automationId "Documents" is an exact match for the entity; passing
        # it before a generic name should not be overridden.
        element = uiData.resolve("DocumentManager", "SomeRandomName")
        self.assertEqual(element["key"], "managerDocuments")

    def test_returns_none_for_unrecognised_string(self):
        self.assertIsNone(uiData.resolve("TotallyUnknownWidgetXyz"))

    def test_ignores_falsy_values(self):
        self.assertIsNone(uiData.resolve("", None, "   "))

    def test_short_tokens_do_not_loosely_match(self):
        # "ID" is a real column key but must not swallow unrelated names
        # like "Hidden" or "Guide" via substring matching.
        element = uiData.resolve("HiddenWidget")
        self.assertIsNone(element)

    def test_exact_resolver_rejects_content_containing_ui_term(self):
        self.assertIsNone(uiData.resolveExact("Interview about codes"))

    def test_exact_resolver_accepts_exact_localised_label(self):
        element = uiData.resolveExact("Administrador de Códigos")
        self.assertEqual(element["key"], "managerCodes")

    def test_start_collision_is_resolved_by_control_kind(self):
        column = uiData.resolveExact("Start", kind="column")
        tab = uiData.resolveExact("Start", kind="tab")
        self.assertEqual(column["key"], "colStart")
        self.assertEqual(tab["key"], "tabHome")

    def test_manager_context_resolves_segmented_comment_control(self):
        element = uiData.resolveExact(
            "Comment", kind="button", context=("managerCodes",))
        self.assertEqual(element["key"], "managerCommentView")


class LabelTests(unittest.TestCase):
    def test_english_label(self):
        element = uiData.resolve("CodeManager")
        self.assertEqual(uiData.label(element, language="en"), "Code Manager")

    def test_greek_label(self):
        element = uiData.resolve("CodeManager")
        self.assertEqual(uiData.label(element, language="el"), "Διαχειριστής Κωδικών")

    def test_bilingual_label_appends_english_original(self):
        element = uiData.resolve("CodeManager")
        spoken = uiData.label(element, language="el", bilingual=True)
        self.assertIn("Διαχειριστής Κωδικών", spoken)
        self.assertIn("Code Manager", spoken)

    def test_bilingual_has_no_effect_in_english(self):
        element = uiData.resolve("CodeManager")
        spoken = uiData.label(element, language="en", bilingual=True)
        self.assertEqual(spoken, "Code Manager")

    def test_label_of_none_is_none(self):
        self.assertIsNone(uiData.label(None))

    def test_self_contained_greek_button_label_includes_role(self):
        element = uiData.resolve("SaveProject")
        self.assertEqual(
            uiData.spokenLabel(element, language="el"),
            "Κουμπί Αποθήκευση Έργου")

    def test_self_contained_greek_column_label_includes_role(self):
        element = uiData.resolveExact("Start", kind="column")
        self.assertEqual(
            uiData.spokenLabel(element, language="el"), "Στήλη Έναρξη")

    def test_tabs_already_include_their_role_in_greek(self):
        element = uiData.resolve("HomeTab")
        self.assertEqual(
            uiData.spokenLabel(element, language="el"), "Καρτέλα Αρχική")

    def test_control_states_are_translated_in_stable_order(self):
        states = {"COLLAPSED", "UNAVAILABLE", "CHECKED"}
        self.assertEqual(
            uiData.stateLabels(states, language="el"),
            ["Μη διαθέσιμο", "Τσεκαρισμένο", "Συμπτυγμένο"],
        )

    def test_half_checked_is_not_misread_as_checked(self):
        self.assertEqual(
            uiData.stateLabels({"HALFCHECKED"}, language="en"),
            ["Partially checked"],
        )


class GuessInterfaceLanguageTests(unittest.TestCase):
    def test_detects_german_from_distinguishing_names(self):
        names = ["Kode-Manager", "Zitat-Manager", "Speichern"]
        self.assertEqual(uiData.guessInterfaceLanguage(names), "de")

    def test_detects_spanish(self):
        names = ["Administrador de Códigos", "Administrador de Citas"]
        self.assertEqual(uiData.guessInterfaceLanguage(names), "es")

    def test_detects_greek_interface_labels(self):
        names = ["Καρτέλα Αρχική", "Διαχειριστής Κωδικών", "Αποθήκευση Έργου"]
        self.assertEqual(uiData.guessInterfaceLanguage(names), "el")

    def test_ambiguous_or_english_names_yield_none(self):
        # "Memos" and generic English UI strings carry no distinguishing
        # foreign-language evidence.
        self.assertIsNone(uiData.guessInterfaceLanguage(["Memos", "Filter", ""]))

    def test_empty_input_yields_none(self):
        self.assertIsNone(uiData.guessInterfaceLanguage([]))


class VisualOnlyTests(unittest.TestCase):
    """Charts/diagrams: honesty about what is and isn't readable."""

    def test_network_editor_is_visual_only_with_a_companion(self):
        element = uiData.resolve("NetworkEditor")
        self.assertTrue(uiData.isVisualOnly(element))
        companion = uiData.companion(element)
        self.assertIsNotNone(companion)
        self.assertEqual(companion["key"], "managerLinks")

    def test_word_cloud_companion_is_word_list(self):
        element = uiData.resolve("WordCloud")
        companion = uiData.companion(element)
        self.assertEqual(companion["key"], "wordList")

    def test_ordinary_manager_is_not_visual_only(self):
        element = uiData.resolve("CodeManager")
        self.assertFalse(uiData.isVisualOnly(element))
        self.assertIsNone(uiData.companion(element))

    def test_concept_available_in_both_languages(self):
        element = uiData.resolve("NetworkEditor")
        english = uiData.concept(element, language="en")
        greek = uiData.concept(element, language="el")
        self.assertTrue(english)
        self.assertTrue(greek)
        self.assertNotEqual(english, greek)

    def test_concept_of_none_is_none(self):
        self.assertIsNone(uiData.concept(None))

    def test_concept_of_non_visual_element_is_none(self):
        element = uiData.resolve("CodeManager")
        self.assertIsNone(uiData.concept(element))

    def test_view_mode_toggles_point_back_to_list_view(self):
        for key in ("viewCloud", "viewCodeBarChart", "viewTreemapMode"):
            element = uiData.ELEMENTS[key]
            self.assertTrue(uiData.isVisualOnly(element), msg=key)
            companion = uiData.companion(element)
            self.assertEqual(companion["key"], "viewList", msg=key)

    def test_sankey_and_treemap_and_barchart_are_visual_only(self):
        for key in ("sankeyDiagram", "treemap", "barChart", "diagramPane",
                    "codeCooccurrenceExplorer"):
            self.assertTrue(uiData.isVisualOnly(uiData.ELEMENTS[key]), msg=key)


class ElementsOfKindTests(unittest.TestCase):
    def test_returns_only_requested_kind(self):
        tabs = uiData.elementsOfKind("tab")
        self.assertTrue(tabs)
        self.assertTrue(all(e["kind"] == "tab" for e in tabs))

    def test_sorted_by_english_name(self):
        tabs = uiData.elementsOfKind("tab")
        names = [e["en"] for e in tabs]
        self.assertEqual(names, sorted(names))

    def test_unknown_kind_returns_empty(self):
        self.assertEqual(uiData.elementsOfKind("notAKind"), [])


class DataIntegrityTests(unittest.TestCase):
    """Guards against the table quietly rotting as it grows."""

    def test_every_element_has_english_and_greek_labels(self):
        for key, element in uiData.ELEMENTS.items():
            self.assertTrue(element["en"], msg=key)
            self.assertTrue(element["el"], msg=key)

    def test_every_key_resolves_to_itself(self):
        for key in uiData.ELEMENTS:
            element = uiData.resolve(key)
            self.assertIsNotNone(element, msg=key)
            self.assertEqual(element["key"], key)

    def test_every_companion_reference_points_at_a_real_element(self):
        for key, element in uiData.ELEMENTS.items():
            companionKey = element.get("companion")
            if companionKey is not None:
                self.assertIn(companionKey, uiData.ELEMENTS,
                              msg="%s companion %r does not exist" % (key, companionKey))

    def test_every_visual_only_element_has_a_concept_description(self):
        for key, element in uiData.ELEMENTS.items():
            if element.get("visualOnly"):
                self.assertIsNotNone(element.get("concept"), msg=key)

    def test_no_duplicate_automation_ids_across_different_elements(self):
        # An element listing two casing variants of its own id (e.g. both
        # would normalise the same) is fine; only a *different* element
        # reusing the same normalised id is a real ambiguity bug.
        seen = {}
        for key, element in uiData.ELEMENTS.items():
            for identifier in element["ids"]:
                normalized = uiData.normalize(identifier)
                owner = seen.get(normalized)
                if owner is not None and owner != key:
                    self.fail("id %r resolves ambiguously to both %r and %r"
                              % (identifier, owner, key))
                seen[normalized] = key

    def test_requested_atlasti_26_inventory_is_fully_covered(self):
        counts = {}
        for element in uiData.ELEMENTS.values():
            counts[element["kind"]] = counts.get(element["kind"], 0) + 1
        self.assertGreaterEqual(counts.get("button", 0), 116)
        self.assertGreaterEqual(counts.get("column", 0), 22)
        self.assertGreaterEqual(counts.get("panel", 0), 18)
        self.assertGreaterEqual(counts.get("manager", 0), 11)
        self.assertGreaterEqual(counts.get("tab", 0), 11)

    def test_priority_atlasti_26_surfaces_have_greek_labels(self):
        keys = (
            "managerDiagramView", "managerPreviewView", "managerCommentView",
            "filterToday", "filterThisWeek", "filterOnlyMine", "filterCommented",
            "welcomeProjectListPane", "sampleProjects", "quotationSingleLine",
            "quotationSmallPreview", "quotationLargePreview", "importDialog",
            "searchDialog", "queryDialog", "reportDialog", "confirmationDialog",
        )
        for key in keys:
            self.assertTrue(uiData.ELEMENTS[key]["el"], msg=key)

    def test_documentation_tree_references_real_elements(self):
        for surfaceKey, surface in uiData.DOCUMENTED_SURFACES.items():
            root = surface.get("root")
            if root:
                self.assertIn(root, uiData.ELEMENTS, msg=surfaceKey)
            for child in surface.get("children", ()):
                self.assertIn(child, uiData.ELEMENTS, msg=surfaceKey)
            self.assertTrue(surface.get("source", "").startswith(uiData.MANUAL_ROOT))

    def test_machine_readable_catalogue_covers_every_element(self):
        records = uiData.catalogueRecords()
        self.assertEqual(len(records), len(uiData.ELEMENTS))
        self.assertEqual({record["key"] for record in records}, set(uiData.ELEMENTS))
        for record in records:
            self.assertTrue(record["en"], msg=record["key"])
            self.assertTrue(record["el"], msg=record["key"])

    def test_every_exact_collision_is_resolvable_by_kind_and_context(self):
        self.assertTrue(uiData.exactCollisions())
        self.assertEqual(uiData.unresolvedCollisions(), [])


if __name__ == "__main__":
    unittest.main()
