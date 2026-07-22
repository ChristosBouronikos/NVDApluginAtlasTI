# -*- coding: utf-8 -*-
# =============================================================================
# Atlas.ti Accessibility App Module for NVDA
# Version: 1.3.0
# =============================================================================
#
# Author: Christos Bouronikos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donations: https://paypal.me/christosbouronikos
#
# Copyright (C) 2026 Christos Bouronikos
# This file is covered by the GNU General Public License v2.
# See the file LICENSE for more details.
#
# If you find this plugin helpful, please consider donating!
# =============================================================================

"""ATLAS.ti Accessibility App Module for NVDA.

What this module does
---------------------
* Recognises ATLAS.ti controls -- ribbon tabs, managers, panes, buttons,
  columns and query operators -- from their automation ids and their
  accessible names, in every language ATLAS.ti's interface ships in.
* Speaks them in English or Greek. ATLAS.ti itself has no Greek interface,
  so for a Greek user the add-on is the translation layer: it recognises
  the English (or German, Spanish, Portuguese, Chinese) label and announces
  the Greek one.
* Moves focus to the major work areas and reports what is there: the
  current panel, the current table row with its column headers, the margin
  area, the comment pane, the status bar and the whole ribbon.

Design notes
------------
The UI table lives in :mod:`_atlastiUI`, which imports nothing from NVDA so
it can be tested on plain CPython. Everything that touches NVDA lives here.

Every announcement is meant to be honest: navigation reports success only
after focus has actually moved, and the reading commands say when the
focused object is not the kind of object the command is about, rather than
confidently describing an unrelated control.
"""

import json
import weakref

import addonHandler
import api
import appModuleHandler
import controlTypes
import ui
from logHandler import log
from scriptHandler import script

# The UI table is a sibling module. Relative import when NVDA loads this as
# part of the appModules package; plain import when the test suite loads it
# as a top-level module.
try:
    from . import _atlastiUI as uiData
except ImportError:  # pragma: no cover - exercised only outside NVDA
    import _atlastiUI as uiData

addonHandler.initTranslation()


# =============================================================================
# OPTIONAL NVDA MODULES
# =============================================================================
# None of these are required for the core features, and guarding them keeps
# the module importable under the test stubs and on older NVDA builds.

try:
    import config
except ImportError:  # pragma: no cover
    config = None

try:
    import languageHandler
except ImportError:  # pragma: no cover
    languageHandler = None

try:
    import core
except ImportError:  # pragma: no cover
    core = None


CONFIG_SECTION = "atlastiAccessibility"

CONFIG_DEFAULTS = {
    "outputLanguage": "auto",
    "bilingualLabels": True,
    "translateLabels": True,
    "labelUnlabeledButtons": True,
    "announcePanelChanges": True,
    "announceRibbonTabs": True,
    "announceControlStates": True,
    "speakHints": False,
    "enableSafeUICapture": False,
}


def getOption(name):
    """Read an add-on setting, falling back to its default.

    The settings panel lives in the global plugin; if it never ran (older
    NVDA, or a stripped test environment) every option keeps its default.
    """
    default = CONFIG_DEFAULTS.get(name)
    if config is None:
        return default
    try:
        return config.conf[CONFIG_SECTION][name]
    except Exception:
        return default


def setOption(name, value):
    """Persist an add-on setting; silently ignored when config is absent."""
    if config is None:
        return
    try:
        config.conf[CONFIG_SECTION][name] = value
    except Exception:
        log.debug("Could not store option %s" % name)


def outputLanguage():
    """Which language the add-on should speak in: "en" or "el"."""
    setting = getOption("outputLanguage")
    if setting in ("en", "el"):
        return setting
    nvdaLanguage = ""
    if languageHandler is not None:
        try:
            nvdaLanguage = languageHandler.getLanguage() or ""
        except Exception:
            nvdaLanguage = ""
    return "el" if nvdaLanguage.lower().startswith("el") else "en"


# =============================================================================
# NAVIGATION TARGETS
# =============================================================================
# Each target lists the UI element keys to look for, best candidate first.
# A manager and its underlying entity list can both satisfy a request, so
# the manager is tried before the generic entity name.

NAVIGATION_TARGETS = {
    "documents": ("managerDocuments", "documentBrowser", "documents"),
    "quotations": ("managerQuotations", "quotationBrowser", "quotations"),
    "codes": ("managerCodes", "codeBrowser", "codes"),
    "memos": ("managerMemos", "memoBrowser", "memos"),
    "networks": ("managerNetworks", "networkBrowser", "networks"),
    "links": ("managerLinks", "managerRelations", "links"),
    "navigator": ("projectNavigator",),
    "ribbon": ("ribbon",),
    "margin": ("marginArea",),
    "workArea": ("workArea",),
    "comment": ("commentPane", "previewPane"),
    "sidePanel": ("sidePanel",),
}

# Order used by the "cycle panels" commands.
PANEL_CYCLE = (
    "navigator",
    "workArea",
    "margin",
    "documents",
    "codes",
    "quotations",
    "memos",
    "comment",
)

# Containers that identify "which part of ATLAS.ti am I in".
CONTEXT_KINDS = ("manager", "panel", "window", "dialog")

# Reading commands only trust a context that actually is about the entity.
CODE_CONTEXTS = ("managerCodes", "codeBrowser", "codes", "managerCodeGroups")
QUOTATION_CONTEXTS = ("managerQuotations", "quotationBrowser", "quotations",
                      "quotationReader")
DOCUMENT_CONTEXTS = ("managerDocuments", "documentBrowser", "documents", "workArea")

DOCUMENT_EXTENSIONS = (
    ".pdf", ".txt", ".docx", ".doc", ".rtf", ".odt", ".xlsx", ".csv",
    ".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff",
    ".mp3", ".wav", ".m4a", ".mp4", ".avi", ".mov", ".mkv", ".srt", ".vtt",
)

# Tree walking limits. ATLAS.ti exposes a deep UIA tree and an unbounded
# walk can freeze speech for seconds, so every search is bounded.
MAX_SEARCH_NODES = 2500
MAX_SEARCH_DEPTH = 14
MAX_LIST_ITEMS = 300


# Dialog overlays are deliberately small marker mixins. ATLAS.ti renders
# these pop-ups through the same generic WPF/UIA classes; the marker lets the
# app module preserve the dialog family while resolving ambiguous controls
# such as Import, Search, Create, Continue, Yes and No.
class AtlasImportDialogOverlay:
    atlasDialogKey = "importDialog"


class AtlasSearchDialogOverlay:
    atlasDialogKey = "searchDialog"


class AtlasQueryDialogOverlay:
    atlasDialogKey = "queryDialog"


class AtlasReportDialogOverlay:
    atlasDialogKey = "reportDialog"


class AtlasConfirmationDialogOverlay:
    atlasDialogKey = "confirmationDialog"


class AtlasManagerOverlay:
    atlasSurfaceType = "manager"


class AtlasManagerContextMenuOverlay:
    atlasSurfaceType = "managerContextMenu"


class AtlasManagerFilterOverlay:
    atlasSurfaceType = "managerFilter"


class AtlasWelcomeScreenOverlay:
    atlasSurfaceType = "welcome"
    atlasContextKey = "welcomeScreen"


class AtlasQuotationReaderOverlay:
    atlasSurfaceType = "quotationReader"
    atlasContextKey = "quotationReader"


DIALOG_OVERLAYS = {
    "importDialog": AtlasImportDialogOverlay,
    "searchDialog": AtlasSearchDialogOverlay,
    "queryDialog": AtlasQueryDialogOverlay,
    "reportDialog": AtlasReportDialogOverlay,
    "confirmationDialog": AtlasConfirmationDialogOverlay,
}

MANAGER_KEYS = {
    "managerDocuments", "managerQuotations", "managerCodes", "managerMemos",
    "managerNetworks", "managerLinks", "managerRelations", "managerDocumentGroups",
    "managerCodeGroups", "managerMemoGroups", "managerNetworkGroups",
}

FILTER_KEYS = {
    "filterToday", "filterThisWeek", "filterOnlyMine", "filterCommented",
    "clearFilter", "globalFilterBar", "localFilter", "globalFilter",
    "clearGlobalFilter", "tabSearchFilter",
}


# =============================================================================
# MAIN APP MODULE CLASS
# =============================================================================

class AppModule(appModuleHandler.AppModule):
    """NVDA App Module for ATLAS.ti.

    Author: Christos Bouronikos <chrisbouronikos@gmail.com>
    Donations: https://paypal.me/christosbouronikos
    """

    # Translators: Category for Atlas.ti scripts in NVDA Input Gestures dialog
    scriptCategory = _("Atlas.ti")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._panelCache = {}
        self._lastPanel = None
        self._lastContextKey = None
        self._lastRibbonTab = None
        self._languageSamples = []
        self._detectedLanguage = None
        log.info("Atlas.ti accessibility app module v1.3.0 loaded")

    def terminate(self):
        log.info("Atlas.ti accessibility app module unloaded")
        super().terminate()

    # =========================================================================
    # SPEECH HELPERS
    # =========================================================================

    def _label(self, element):
        """Spoken name of a UI element in the user's language."""
        return uiData.label(
            element,
            language=outputLanguage(),
            bilingual=bool(getOption("bilingualLabels")),
        )

    def _semanticControlType(self, obj):
        """Map an NVDA role to the bilingual role names in the UI table."""
        role = self._attr(obj, "role", None)
        if role in self._roles("BUTTON", "TOGGLEBUTTON", "SPLITBUTTON"):
            return "button"
        if role in self._roles("MENUITEM"):
            return "menuItem"
        if role in self._roles("CHECKBOX"):
            return "checkBox"
        if role in self._roles("RADIOBUTTON"):
            return "radioButton"
        if role in self._roles("COLUMNHEADER"):
            return "column"
        return None

    def _spokenLabel(self, element, obj=None, controlType=None):
        """Self-contained label for messages where NVDA will not add a role."""
        return uiData.spokenLabel(
            element,
            language=outputLanguage(),
            bilingual=bool(getOption("bilingualLabels")),
            controlTypeOverride=controlType or (
                self._semanticControlType(obj) if obj is not None else None),
        )

    def _nvdaLanguageMatchesOutput(self):
        """Whether NVDA itself will localise the native role correctly."""
        nvdaLanguage = ""
        if languageHandler is not None:
            try:
                nvdaLanguage = languageHandler.getLanguage() or ""
            except Exception:
                pass
        expected = "el" if nvdaLanguage.lower().startswith("el") else "en"
        return expected == outputLanguage()

    def _objectLabel(self, element, obj):
        """Name to assign to an NVDA object without duplicating its role.

        NVDA normally speaks the role itself.  If the user explicitly asks
        for Greek while NVDA's own interface is English (or the reverse),
        the role is embedded once in the requested language so an object is
        never announced as only a translated name with the wrong-language
        control type.
        """
        if self._nvdaLanguageMatchesOutput():
            return self._label(element)
        semanticType = self._semanticControlType(obj)
        if semanticType:
            return self._spokenLabel(element, obj=obj, controlType=semanticType)
        return self._label(element)

    def _describeElement(self, element, includeHint=None, obj=None):
        """Label plus optional hint and documented ATLAS.ti shortcut."""
        if not element:
            return None
        parts = [self._spokenLabel(element, obj=obj) if obj is not None else self._label(element)]
        if obj is not None:
            parts.extend(self._stateLabels(obj))
        if includeHint is None:
            includeHint = bool(getOption("speakHints"))
        if includeHint and uiData.hint(element):
            parts.append(uiData.hint(element))
        keyCombo = uiData.shortcut(element)
        if keyCombo:
            # Translators: Announces the ATLAS.ti keyboard shortcut of a control
            parts.append(_("shortcut {keys}").format(keys=keyCombo))
        return ", ".join(part for part in parts if part)

    def _stateLabels(self, obj):
        """Relevant control states translated into the selected language."""
        try:
            states = obj.states or set()
        except Exception:
            states = set()
        return uiData.stateLabels(states, language=outputLanguage())

    # =========================================================================
    # OBJECT INSPECTION HELPERS
    # =========================================================================

    @staticmethod
    def _roles(*names):
        """The Role members that exist on this NVDA version, as a tuple.

        Role membership has shifted between NVDA releases, so every role is
        looked up by name and missing ones are simply dropped.
        """
        roleEnum = getattr(controlTypes, "Role", None)
        found = []
        for name in names:
            role = getattr(roleEnum, name, None) if roleEnum is not None else None
            if role is not None:
                found.append(role)
        return tuple(found)

    @staticmethod
    def _attr(obj, name, default=""):
        """Read an NVDA object property without ever raising."""
        try:
            value = getattr(obj, name, default)
        except Exception:
            return default
        return default if value is None else value

    def _identifiers(self, obj):
        """The strings worth matching on, most reliable first.

        Automation ids and window class names come first because they do
        not change when the user switches ATLAS.ti's display language.
        """
        return (
            self._attr(obj, "UIAAutomationId"),
            self._attr(obj, "windowClassName"),
            self._attr(obj, "name"),
        )

    def _expectedKinds(self, obj):
        """Knowledge-base kinds compatible with an object's NVDA role."""
        role = self._attr(obj, "role", None)
        if role in self._roles("TAB"):
            return ("tab",)
        if role in self._roles("COLUMNHEADER"):
            return ("column",)
        if role in self._roles(
            "BUTTON", "MENUITEM", "CHECKBOX", "TOGGLEBUTTON", "SPLITBUTTON",
            "RADIOBUTTON"):
            return ("button", "operator", "view")
        if role in self._roles("DIALOG"):
            return ("dialog",)
        if role in self._roles("WINDOW", "PANE", "GROUPING", "TOOLBAR", "STATUSBAR"):
            return CONTEXT_KINDS
        return None

    def _rawResolve(self, obj):
        """Resolve without role/context filtering; used while finding context."""
        if obj is None:
            return None
        element = uiData.resolve(*self._identifiers(obj))
        if element is not None:
            return element
        marker = self._attr(obj, "atlasDialogKey")
        if marker in DIALOG_OVERLAYS:
            return uiData.ELEMENTS.get(marker)
        marker = self._attr(obj, "atlasContextKey")
        if marker in uiData.ELEMENTS:
            return uiData.ELEMENTS.get(marker)
        return None

    def _ancestorContextKeys(self, obj):
        keys = []
        current = self._attr(obj, "parent", None)
        steps = 0
        while current is not None and steps < 40:
            element = self._rawResolve(current)
            if element is not None and element["kind"] in CONTEXT_KINDS:
                if element["key"] not in keys:
                    keys.append(element["key"])
            current = self._attr(current, "parent", None)
            steps += 1
        return keys

    def _resolve(self, obj):
        """Resolve an object to a known ATLAS.ti UI element, or None."""
        if obj is None:
            return None
        kinds = self._expectedKinds(obj)
        context = self._ancestorContextKeys(obj)
        element = uiData.resolve(
            *self._identifiers(obj), kind=kinds, context=context)
        if element is not None:
            return element
        # Some UIA providers expose generic or inaccurate roles on their
        # containers. Preserve navigation by falling back to context-aware
        # matching without the role filter.
        return uiData.resolve(*self._identifiers(obj), context=context)

    def _rememberLanguageSample(self, obj):
        """Collect names so the ATLAS.ti display language can be guessed."""
        name = self._attr(obj, "name")
        if not name or len(self._languageSamples) >= 400:
            return
        self._languageSamples.append(name)
        self._detectedLanguage = None

    def detectedInterfaceLanguage(self):
        """Best guess at the language ATLAS.ti's own interface is using."""
        if self._detectedLanguage is None:
            self._detectedLanguage = uiData.guessInterfaceLanguage(
                self._languageSamples) or ""
        return self._detectedLanguage or None

    def _getMainWindow(self, obj=None):
        """The top-level ATLAS.ti window."""
        try:
            foreground = api.getForegroundObject()
        except Exception:
            foreground = None
        if foreground is not None:
            return foreground
        current = obj
        lastWindow = None
        while current is not None:
            if self._attr(current, "role", None) in self._roles("WINDOW"):
                lastWindow = current
            current = self._attr(current, "parent", None)
        return lastWindow

    def _walk(self, container, maxNodes=MAX_SEARCH_NODES, maxDepth=MAX_SEARCH_DEPTH):
        """Breadth-first walk of the accessible tree under ``container``.

        Bounded deliberately: an unbounded walk of ATLAS.ti's UIA tree can
        block speech for several seconds on a large project.
        """
        if container is None:
            return
        queue = [(container, 0)]
        visited = 0
        while queue and visited < maxNodes:
            obj, depth = queue.pop(0)
            visited += 1
            yield obj
            if depth >= maxDepth:
                continue
            try:
                children = obj.children or []
            except Exception:
                continue
            for child in children:
                queue.append((child, depth + 1))

    def _findElement(self, container, elementKeys):
        """Find the first descendant matching one of ``elementKeys``.

        Two passes on purpose. The first accepts only automation id or
        window class matches, which are language independent and precise;
        the second falls back to display names. Without the split, a button
        labelled "Open Code Manager" would win over the Code Manager pane
        itself simply by appearing earlier in the tree.
        """
        wanted = set(elementKeys)
        nameMatch = None
        for obj in self._walk(container):
            automationId = self._attr(obj, "UIAAutomationId")
            className = self._attr(obj, "windowClassName")
            element = uiData.resolve(automationId, className)
            if element is not None and element["key"] in wanted:
                return obj
            if nameMatch is None:
                element = uiData.resolve(self._attr(obj, "name"))
                if element is not None and element["key"] in wanted:
                    nameMatch = obj
        return nameMatch

    def _contextElement(self, obj):
        """Walk up from ``obj`` to the container it lives in."""
        current = obj
        steps = 0
        while current is not None and steps < 40:
            element = self._resolve(current)
            if element is not None and element["kind"] in CONTEXT_KINDS:
                return element
            current = self._attr(current, "parent", None)
            steps += 1
        return None

    def _contextPath(self, obj, maxParts=4):
        """Readable chain of the containers an object sits in."""
        parts = []
        current = self._attr(obj, "parent", None)
        steps = 0
        while current is not None and steps < 40 and len(parts) < maxParts:
            element = self._resolve(current)
            if element is not None and element["kind"] in CONTEXT_KINDS:
                spoken = self._label(element)
                if spoken and spoken not in parts:
                    parts.append(spoken)
            current = self._attr(current, "parent", None)
            steps += 1
        return list(reversed(parts))

    def _inContext(self, obj, contextKeys):
        """Is ``obj`` inside one of the given containers?"""
        current = obj
        steps = 0
        while current is not None and steps < 40:
            element = self._resolve(current)
            if element is not None and element["key"] in contextKeys:
                return True
            current = self._attr(current, "parent", None)
            steps += 1
        return False

    def _roleName(self, obj):
        """Localised role name, e.g. "button"."""
        role = self._attr(obj, "role", None)
        if role is None:
            return None
        try:
            return role.displayString
        except Exception:
            pass
        try:
            return controlTypes.roleLabels[role]
        except Exception:
            return None

    def _objectText(self, obj):
        """Best available text of an object: its value, else its content."""
        value = self._attr(obj, "value")
        if value:
            return value
        try:
            info = obj.makeTextInfo(obj.TextInfo.POSITION_ALL)
            text = info.text
            if text and text.strip():
                return text.strip()
        except Exception:
            pass
        return self._attr(obj, "name")

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def event_foreground(self, obj, nextHandler):
        """Drop cached panel references when the foreground window changes.

        A cached panel can stay "alive" (per weakref/isAlive) even after
        ATLAS.ti swaps projects or reopens a window, so it is no longer the
        right target. Foreground change is the cheapest reliable signal we
        have to invalidate it.
        """
        self._panelCache.clear()
        self._lastPanel = None
        self._lastContextKey = None
        self._lastRibbonTab = None
        nextHandler()

    def event_NVDAObject_init(self, obj):
        """Give ATLAS.ti controls better names before NVDA speaks them.

        Two jobs: name the buttons ATLAS.ti leaves unlabelled, and -- when
        the user listens in Greek -- replace recognised English labels with
        their Greek equivalents.
        """
        try:
            role = self._attr(obj, "role", None)
            name = self._attr(obj, "name")
            self._rememberLanguageSample(obj)

            controlRoles = self._roles(
                "BUTTON", "MENUITEM", "TAB", "CHECKBOX", "TOGGLEBUTTON",
                "SPLITBUTTON", "RADIOBUTTON")
            isButton = role is not None and role in controlRoles

            if not name and isButton and getOption("labelUnlabeledButtons"):
                element = uiData.resolve(
                    self._attr(obj, "UIAAutomationId"),
                    self._attr(obj, "windowClassName"),
                    kind=self._expectedKinds(obj),
                    context=self._ancestorContextKeys(obj),
                )
                if element is not None:
                    obj.name = self._objectLabel(element, obj)
                    return
                description = self._attr(obj, "description")
                if description:
                    obj.name = description
                return

            if (
                name
                and isButton
                and outputLanguage() == "el"
                and getOption("translateLabels")
            ):
                # Renaming must use exact matches only.  The broader resolver
                # deliberately supports substring matches for navigation, but
                # using it here can destroy research content: a list item named
                # "Interview about codes" would otherwise become simply
                # "Codes" in Greek.
                element = uiData.resolveExact(
                    self._attr(obj, "UIAAutomationId"),
                    self._attr(obj, "windowClassName"),
                    name,
                    kind=self._expectedKinds(obj),
                    context=self._ancestorContextKeys(obj),
                )
                if element is None:
                    # A ribbon button can be named after the window it opens
                    # (for example "Code Manager"). In that case the label is
                    # still exact and safe even though its semantic table kind
                    # is "manager" rather than "button".
                    element = uiData.resolveExact(
                        self._attr(obj, "UIAAutomationId"),
                        self._attr(obj, "windowClassName"),
                        name,
                        context=self._ancestorContextKeys(obj),
                    )
                if element is not None:
                    translated = self._objectLabel(element, obj)
                    if translated:
                        obj.name = translated
        except Exception as error:
            log.debug("Atlas.ti labelling error: %s" % error)

    def event_gainFocus(self, obj, nextHandler):
        """Announce when focus crosses into a different part of ATLAS.ti."""
        try:
            self._rememberLanguageSample(obj)
            if getOption("announceRibbonTabs"):
                self._announceRibbonTab(obj)
            if getOption("announcePanelChanges"):
                self._announceContextChange(obj)
        except Exception as error:
            log.debug("Atlas.ti focus handling error: %s" % error)
        nextHandler()

    def event_stateChange(self, obj, nextHandler):
        """Provide translated checked/selected/expanded state feedback.

        NVDA already speaks states in its own language. A separate translated
        message is needed only when the add-on is explicitly configured for
        the other language, which avoids duplicate speech in automatic mode.
        """
        nextHandler()
        if not getOption("announceControlStates") or self._nvdaLanguageMatchesOutput():
            return
        if self._resolve(obj) is None:
            return
        labels = self._stateLabels(obj)
        if labels:
            ui.message(", ".join(labels))

    def chooseNVDAObjectOverlayClasses(self, obj, clsList):
        """Attach the most specific structural ATLAS.ti marker overlay.

        ATLAS.ti exposes many WPF surfaces through generic UIA classes. These
        markers preserve dialog, Welcome, Quotation Reader, manager-filter and
        manager-context-menu identity for context-aware resolution.
        """
        current = obj
        steps = 0
        elements = []
        while current is not None and steps < 40:
            element = self._rawResolve(current)
            if element is not None:
                elements.append(element)
                overlay = DIALOG_OVERLAYS.get(element["key"])
                if overlay is not None:
                    clsList.insert(0, overlay)
                    return
            current = self._attr(current, "parent", None)
            steps += 1

        keys = {element["key"] for element in elements}
        if "welcomeScreen" in keys:
            clsList.insert(0, AtlasWelcomeScreenOverlay)
            return
        if "quotationReader" in keys:
            clsList.insert(0, AtlasQuotationReaderOverlay)
            return
        managerPresent = bool(keys.intersection(MANAGER_KEYS))
        if managerPresent and keys.intersection(FILTER_KEYS):
            clsList.insert(0, AtlasManagerFilterOverlay)
            return
        role = self._attr(obj, "role", None)
        if managerPresent and role in self._roles("MENU", "MENUITEM"):
            clsList.insert(0, AtlasManagerContextMenuOverlay)
            return
        if managerPresent:
            clsList.insert(0, AtlasManagerOverlay)

    def _announceRibbonTab(self, obj):
        role = self._attr(obj, "role", None)
        if role not in self._roles("TAB"):
            return
        element = self._resolve(obj)
        if element is None or element["kind"] != "tab":
            return
        if element["key"] == self._lastRibbonTab:
            return
        self._lastRibbonTab = element["key"]
        message = self._describeElement(element)
        if message:
            ui.message(message)

    def _announceContextChange(self, obj):
        element = self._contextElement(obj)
        if element is None:
            return
        if element["key"] == self._lastContextKey:
            return
        self._lastContextKey = element["key"]
        spoken = self._label(element)
        if spoken:
            ui.message(spoken)

    # =========================================================================
    # PANEL NAVIGATION SCRIPTS
    # =========================================================================

    @script(
        # Translators: Description for the go to documents script
        description=_("Go to the Document Manager"),
        gesture="kb:NVDA+control+alt+d",
    )
    def script_goToDocuments(self, gesture):
        self._navigateTo("documents")

    @script(
        # Translators: Description for the go to codes script
        description=_("Go to the Code Manager"),
        gesture="kb:NVDA+control+alt+c",
    )
    def script_goToCodes(self, gesture):
        self._navigateTo("codes")

    @script(
        # Translators: Description for the go to quotations script
        description=_("Go to the Quotation Manager"),
        gesture="kb:NVDA+control+alt+q",
    )
    def script_goToQuotations(self, gesture):
        self._navigateTo("quotations")

    @script(
        # Translators: Description for the go to memos script
        description=_("Go to the Memo Manager"),
        gesture="kb:NVDA+control+alt+m",
    )
    def script_goToMemos(self, gesture):
        self._navigateTo("memos")

    @script(
        # Translators: Description for the go to networks script
        description=_("Go to the Network Manager"),
        gesture="kb:NVDA+control+alt+n",
    )
    def script_goToNetworks(self, gesture):
        self._navigateTo("networks")

    @script(
        # Translators: Description for the go to links script
        description=_("Go to the Link Manager"),
        gesture="kb:NVDA+control+alt+l",
    )
    def script_goToLinks(self, gesture):
        self._navigateTo("links")

    @script(
        # Translators: Description for the go to project navigator script
        description=_("Go to the Project Navigator"),
        gesture="kb:NVDA+control+alt+p",
    )
    def script_goToNavigator(self, gesture):
        self._navigateTo("navigator")

    @script(
        # Translators: Description for the go to ribbon script
        description=_("Go to the ribbon"),
        gesture="kb:NVDA+control+alt+r",
    )
    def script_goToRibbon(self, gesture):
        self._navigateTo("ribbon")

    @script(
        # Translators: Description for the go to margin area script
        description=_("Go to the margin area"),
        gesture="kb:NVDA+control+alt+a",
    )
    def script_goToMargin(self, gesture):
        self._navigateTo("margin")

    @script(
        # Translators: Description for the go to working area script
        description=_("Go to the working area"),
        gesture="kb:NVDA+control+alt+w",
    )
    def script_goToWorkArea(self, gesture):
        self._navigateTo("workArea")

    @script(
        # Translators: Description for the go to comment pane script
        description=_("Go to the comment pane"),
        gesture="kb:NVDA+control+alt+e",
    )
    def script_goToComment(self, gesture):
        self._navigateTo("comment")

    @script(
        # Translators: Description for the go to side panel script
        description=_("Go to the side panel with groups and filters"),
        gesture="kb:NVDA+control+alt+s",
    )
    def script_goToSidePanel(self, gesture):
        self._navigateTo("sidePanel")

    @script(
        # Translators: Description for the next panel script
        description=_("Move to the next Atlas.ti panel"),
        gesture="kb:NVDA+control+alt+pageDown",
    )
    def script_nextPanel(self, gesture):
        self._cyclePanel(1)

    @script(
        # Translators: Description for the previous panel script
        description=_("Move to the previous Atlas.ti panel"),
        gesture="kb:NVDA+control+alt+pageUp",
    )
    def script_previousPanel(self, gesture):
        self._cyclePanel(-1)

    # =========================================================================
    # READING SCRIPTS
    # =========================================================================

    @script(
        # Translators: Description for the describe element script
        description=_("Describe the focused Atlas.ti control in detail"),
        gesture="kb:NVDA+control+alt+shift+e",
    )
    def script_describeFocus(self, gesture):
        obj = api.getFocusObject()
        if obj is None:
            # Translators: Message when nothing has focus
            ui.message(_("Nothing is focused"))
            return

        parts = []
        element = self._resolve(obj)
        if element is not None:
            parts.append(self._describeElement(element, includeHint=True, obj=obj))
        else:
            name = self._attr(obj, "name")
            if name:
                parts.append(name)
            roleName = self._roleName(obj)
            if roleName:
                parts.append(roleName)
            parts.extend(self._stateLabels(obj))

        value = self._attr(obj, "value")
        if value:
            parts.append(str(value))

        path = self._contextPath(obj)
        if path:
            # Translators: Announces where a control sits, e.g. "in Code Manager"
            parts.append(_("in {path}").format(path=" - ".join(path)))

        if not parts:
            # Translators: Message when a control exposes no usable information
            ui.message(_("This control provides no information to the screen reader"))
            return
        ui.message(", ".join(part for part in parts if part))

    @script(
        # Translators: Description for the announce panel script
        description=_("Announce the current Atlas.ti panel"),
        gesture="kb:NVDA+control+alt+shift+p",
    )
    def script_announcePanel(self, gesture):
        obj = api.getFocusObject()
        element = self._contextElement(obj)
        if element is not None:
            # Translators: Announced when reporting current panel
            ui.message(_("Current panel: {panel}").format(panel=self._label(element)))
            return
        if self._lastPanel:
            lastElement = uiData.ELEMENTS.get(self._lastPanel)
            if lastElement is not None:
                # Translators: Reported when only the last used panel is known
                ui.message(_("Panel unknown. Last panel reached with a command: {panel}")
                           .format(panel=self._label(lastElement)))
                return
        # Translators: Message when panel cannot be determined
        ui.message(_("Unable to determine the current panel"))

    @script(
        # Translators: Description for the read row script
        description=_("Read every column of the current row"),
        gesture="kb:NVDA+control+alt+shift+r",
    )
    def script_readRow(self, gesture):
        obj = api.getFocusObject()
        cells = self._rowCells(obj)
        if not cells:
            # Translators: Message when focus is not on a list or table row
            ui.message(_("Focus is not on a list row"))
            return
        parts = []
        for header, text in cells:
            if not text:
                continue
            if header:
                parts.append("{header}: {text}".format(header=header, text=text))
            else:
                parts.append(text)
        if not parts:
            # Translators: Message when a row exposes no readable cells
            ui.message(_("This row has no readable content"))
            return
        ui.message(". ".join(parts))

    @script(
        # Translators: Description for the item count script
        description=_("Report the item count and status bar of the current list"),
        gesture="kb:NVDA+control+alt+shift+s",
    )
    def script_readStatus(self, gesture):
        parts = []
        obj = api.getFocusObject()

        element = self._contextElement(obj)
        if element is not None:
            parts.append(self._label(element))

        count = self._listItemCount(obj)
        if count is not None:
            # Translators: Reports how many items a list holds
            parts.append(_("{count} items").format(count=count))

        statusText = self._statusBarText()
        if statusText:
            parts.append(statusText)

        if not parts:
            # Translators: Message when no status information is available
            ui.message(_("No status information available"))
            return
        ui.message(", ".join(parts))

    @script(
        # Translators: Description for the read ribbon script
        description=_("List the controls on the current ribbon tab"),
        gesture="kb:NVDA+control+alt+shift+t",
    )
    def script_readRibbon(self, gesture):
        mainWindow = self._getMainWindow(api.getFocusObject())
        ribbon = self._findElement(mainWindow, ("ribbon",)) or mainWindow
        if ribbon is None:
            # Translators: Message when the ribbon cannot be found
            ui.message(_("The ribbon could not be found"))
            return

        selectedTab = None
        buttons = []
        tabRoles = self._roles("TAB")
        buttonRoles = self._roles("BUTTON", "TOGGLEBUTTON", "SPLITBUTTON", "MENUITEM")
        for obj in self._walk(ribbon, maxNodes=1200, maxDepth=10):
            role = self._attr(obj, "role", None)
            if role in tabRoles:
                if self._isSelected(obj) and selectedTab is None:
                    selectedTab = self._resolve(obj) or self._attr(obj, "name")
                continue
            if role not in buttonRoles:
                continue
            element = self._resolve(obj)
            spoken = self._label(element) if element else self._attr(obj, "name")
            if spoken and spoken not in buttons:
                buttons.append(spoken)
            if len(buttons) >= MAX_LIST_ITEMS:
                break

        if isinstance(selectedTab, dict):
            selectedTab = self._label(selectedTab)
        if not buttons:
            # Translators: Message when the ribbon exposes no buttons
            ui.message(_("No ribbon controls are exposed to the screen reader"))
            return

        # Translators: Title of the ribbon contents window
        title = _("Atlas.ti ribbon")
        if selectedTab:
            # Translators: Title of the ribbon contents window for a named tab
            title = _("Atlas.ti ribbon: {tab}").format(tab=selectedTab)
        self._showList(title, buttons)

    @script(
        # Translators: Description for the read margin script
        description=_("Read the codes and memos in the margin area"),
        gesture="kb:NVDA+control+alt+shift+a",
    )
    def script_readMargin(self, gesture):
        mainWindow = self._getMainWindow(api.getFocusObject())
        margin = self._findElement(mainWindow, ("marginArea",))
        if margin is None:
            # Translators: Message when the margin area is not available
            ui.message(_("The margin area could not be found. Open a document first."))
            return
        entries = []
        for obj in self._walk(margin, maxNodes=800, maxDepth=8):
            name = self._attr(obj, "name")
            if name and name not in entries:
                entries.append(name)
            if len(entries) >= MAX_LIST_ITEMS:
                break
        if not entries:
            # Translators: Message when the margin area holds nothing readable
            ui.message(_("The margin area is empty or not readable"))
            return
        # Translators: Title of the margin area contents window
        self._showList(_("Atlas.ti margin area"), entries)

    @script(
        # Translators: Description for the read comment script
        description=_("Read the comment or preview pane"),
        gesture="kb:NVDA+control+alt+shift+n",
    )
    def script_readComment(self, gesture):
        mainWindow = self._getMainWindow(api.getFocusObject())
        pane = self._findElement(mainWindow, ("commentPane", "previewPane"))
        if pane is None:
            # Translators: Message when no comment or preview pane is present
            ui.message(_("No comment or preview pane was found"))
            return
        text = self._objectText(pane)
        if not text:
            for child in self._walk(pane, maxNodes=200, maxDepth=5):
                text = self._objectText(child)
                if text:
                    break
        if not text:
            # Translators: Message when the comment pane is empty
            ui.message(_("The comment pane is empty"))
            return
        ui.message(text)

    @script(
        # Translators: Description for the describe visual script
        description=_("Describe the current chart or diagram, and try to read its contents"),
        gesture="kb:NVDA+control+alt+shift+v",
    )
    def script_describeVisual(self, gesture):
        """Read a chart/diagram's real content if Atlas.ti exposes any;
        otherwise say plainly what it normally shows and where to find the
        same data as text, instead of leaving the researcher with silence
        or a bare, unexplained control name."""
        obj = api.getFocusObject()
        visualObj, element = self._findVisualAncestor(obj)
        if element is None:
            # Translators: Message when focus is not on a chart, diagram or visual-only view
            ui.message(_("The focused control is not a chart, diagram, or visual-only view."))
            return

        label = self._label(element)
        found = self._visualContent(visualObj)
        if found:
            # Translators: Title of the window listing a chart's actual accessible content
            title = _("{chart}: accessible content found").format(chart=label)
            self._showList(title, found)
            return

        parts = [label]
        conceptText = uiData.concept(element, language=outputLanguage())
        if conceptText:
            parts.append(conceptText)
        # Translators: Stated when Atlas.ti exposes no readable content for a chart/diagram
        parts.append(_("Atlas.ti does not expose the individual contents of this element to "
                       "the screen reader."))
        companionElement = uiData.companion(element)
        if companionElement is not None:
            # Translators: Points to the accessible alternative for a chart/diagram
            parts.append(_("For the same data as readable text, use {alternative}. Press "
                           "NVDA+Ctrl+Alt+Shift+J to jump there now.")
                         .format(alternative=self._label(companionElement)))
        ui.message(" ".join(part for part in parts if part))

    @script(
        # Translators: Description for the go to data view script
        description=_("Jump to the accessible data view of the current chart or diagram"),
        gesture="kb:NVDA+control+alt+shift+j",
    )
    def script_goToDataView(self, gesture):
        obj = api.getFocusObject()
        _unused, element = self._findVisualAncestor(obj)
        if element is None:
            # Translators: Message when focus is not on a chart, diagram or visual-only view
            ui.message(_("The focused control is not a chart, diagram, or visual-only view."))
            return
        companionElement = uiData.companion(element)
        if companionElement is None:
            # Translators: Reported when no accessible alternative is known for a chart
            ui.message(_("No accessible alternative is known for {chart}.")
                       .format(chart=self._label(element)))
            return
        self._navigateToKeys(
            (companionElement["key"],), cacheKey="companion:" + companionElement["key"])

    @script(
        # Translators: Description for the read code script
        description=_("Read the focused code"),
        gesture="kb:NVDA+control+alt+shift+c",
    )
    def script_readCode(self, gesture):
        self._readEntity(
            CODE_CONTEXTS,
            # Translators: Format for code information
            _("Code: {name}"),
            # Translators: Message when focus is not on a code
            _("Focus is not on a code. Open the Code Manager or the code list first."),
        )

    @script(
        # Translators: Description for the read quotation script
        description=_("Read the focused quotation"),
        gesture="kb:NVDA+control+alt+shift+q",
    )
    def script_readQuotation(self, gesture):
        self._readEntity(
            QUOTATION_CONTEXTS,
            # Translators: Format for quotation text
            _("Quotation: {name}"),
            # Translators: Message when focus is not on a quotation
            _("Focus is not on a quotation. Open the Quotation Manager or the "
              "Quotation Reader first."),
        )

    @script(
        # Translators: Description for the read document script
        description=_("Read the current document"),
        gesture="kb:NVDA+control+alt+shift+d",
    )
    def script_readDocument(self, gesture):
        obj = api.getFocusObject()
        name = self._findDocumentName(obj)
        if name:
            # Translators: Format for document info
            ui.message(_("Document: {name}").format(name=name))
            return
        if self._inContext(obj, DOCUMENT_CONTEXTS):
            focusName = self._attr(obj, "name")
            if focusName:
                ui.message(_("Document: {name}").format(name=focusName))
                return
        mainWindow = self._getMainWindow(obj)
        windowName = self._attr(mainWindow, "name")
        if windowName:
            # Translators: Format for current context, used as a last resort
            ui.message(_("No document identified. Window title: {name}")
                       .format(name=windowName))
            return
        # Translators: Message when no document info is available
        ui.message(_("No document information available"))

    # =========================================================================
    # GLOSSARY, HELP AND SETTINGS SCRIPTS
    # =========================================================================

    @script(
        # Translators: Description for the glossary script
        description=_("Show the Atlas.ti term glossary in English and Greek"),
        gesture="kb:NVDA+control+alt+shift+g",
    )
    def script_showGlossary(self, gesture):
        language = outputLanguage()
        lines = []
        kindOrder = ("tab", "manager", "window", "panel", "entity", "button",
                     "column", "view", "operator", "dialog", "field")
        kindTitles = {
            # Translators: Glossary section for ribbon tabs
            "tab": _("Ribbon tabs"),
            # Translators: Glossary section for entity managers
            "manager": _("Managers"),
            # Translators: Glossary section for windows
            "window": _("Windows and tools"),
            # Translators: Glossary section for panels and areas
            "panel": _("Panels and areas"),
            # Translators: Glossary section for entity types
            "entity": _("Entity types"),
            # Translators: Glossary section for buttons
            "button": _("Buttons and commands"),
            # Translators: Glossary section for list columns
            "column": _("List columns"),
            # Translators: Glossary section for view options
            "view": _("View options"),
            # Translators: Glossary section for query operators
            "operator": _("Query operators"),
            # Translators: Glossary section for dialogs
            "dialog": _("Dialogs"),
            # Translators: Glossary section for input fields
            "field": _("Fields"),
        }
        for kind in kindOrder:
            elements = uiData.elementsOfKind(kind)
            if not elements:
                continue
            lines.append("")
            lines.append(kindTitles.get(kind, kind).upper())
            for element in elements:
                if language == "el":
                    entry = "{el} - {en}".format(el=element["el"], en=element["en"])
                else:
                    entry = "{en} - {el}".format(en=element["en"], el=element["el"])
                keyCombo = uiData.shortcut(element)
                if keyCombo:
                    entry += " [{keys}]".format(keys=keyCombo)
                lines.append(entry)
        # Translators: Title of the glossary window
        self._showList(_("Atlas.ti glossary"), lines)

    @script(
        # Translators: Description for the list shortcuts script
        description=_("Show all Atlas.ti add-on commands"),
        gesture="kb:NVDA+control+alt+shift+h",
    )
    def script_listShortcuts(self, gesture):
        lines = [
            # Translators: Help heading for panel navigation commands
            _("PANEL NAVIGATION"),
            # Translators: Help entry
            _("NVDA+Control+Alt+D: Document Manager"),
            _("NVDA+Control+Alt+C: Code Manager"),
            _("NVDA+Control+Alt+Q: Quotation Manager"),
            _("NVDA+Control+Alt+M: Memo Manager"),
            _("NVDA+Control+Alt+N: Network Manager"),
            _("NVDA+Control+Alt+L: Link Manager"),
            _("NVDA+Control+Alt+P: Project Navigator"),
            _("NVDA+Control+Alt+R: Ribbon"),
            _("NVDA+Control+Alt+A: Margin area"),
            _("NVDA+Control+Alt+W: Working area"),
            _("NVDA+Control+Alt+E: Comment pane"),
            _("NVDA+Control+Alt+S: Side panel"),
            _("NVDA+Control+Alt+Page down: Next panel"),
            _("NVDA+Control+Alt+Page up: Previous panel"),
            "",
            # Translators: Help heading for reading commands
            _("READING"),
            _("NVDA+Control+Alt+Shift+E: Describe the focused control"),
            _("NVDA+Control+Alt+Shift+P: Current panel"),
            _("NVDA+Control+Alt+Shift+R: All columns of the current row"),
            _("NVDA+Control+Alt+Shift+S: Item count and status bar"),
            _("NVDA+Control+Alt+Shift+T: Controls on the current ribbon tab"),
            _("NVDA+Control+Alt+Shift+A: Margin area contents"),
            _("NVDA+Control+Alt+Shift+N: Comment or preview pane"),
            _("NVDA+Control+Alt+Shift+V: Describe the current chart or diagram"),
            _("NVDA+Control+Alt+Shift+J: Jump to the accessible data view of a chart"),
            _("NVDA+Control+Alt+Shift+C: Focused code"),
            _("NVDA+Control+Alt+Shift+Q: Focused quotation"),
            _("NVDA+Control+Alt+Shift+D: Current document"),
            "",
            # Translators: Help heading for language and help commands
            _("LANGUAGE AND HELP"),
            _("NVDA+Control+Alt+Shift+G: Glossary of Atlas.ti terms"),
            _("NVDA+Control+Alt+Shift+L: Switch between English and Greek"),
            _("NVDA+Control+Alt+Shift+H: This command list"),
            _("NVDA+Control+Alt+Shift+I: Log diagnostic information"),
            _("NVDA+Control+Alt+Shift+U: Privacy-filtered UI tree capture"),
            "",
            # Translators: Help heading for Atlas.ti's own shortcuts
            _("ATLAS.TI SHORTCUTS"),
            _("Control+J: Apply codes to the selected segment"),
            _("Control+K: Create new codes"),
            _("Control+S: Save the project"),
        ]
        # Translators: Title of the command list window
        self._showList(_("Atlas.ti accessibility commands"), lines)

    @script(
        # Translators: Description for the language toggle script
        description=_("Switch the add-on speech language between English and Greek"),
        gesture="kb:NVDA+control+alt+shift+l",
    )
    def script_toggleLanguage(self, gesture):
        order = ("auto", "en", "el")
        current = getOption("outputLanguage")
        try:
            nextSetting = order[(order.index(current) + 1) % len(order)]
        except ValueError:
            nextSetting = "auto"
        setOption("outputLanguage", nextSetting)

        if nextSetting == "auto":
            # Translators: Announced when the add-on follows NVDA's language
            message = _("Speech language: automatic")
        elif nextSetting == "el":
            # Translators: Announced when the add-on speaks Greek
            message = _("Speech language: Greek")
        else:
            # Translators: Announced when the add-on speaks English
            message = _("Speech language: English")

        detected = self.detectedInterfaceLanguage()
        if detected:
            # Translators: Reports which language Atlas.ti's own interface uses
            message += ", " + _("Atlas.ti interface language: {language}").format(
                language=self._languageName(detected))
        ui.message(message)

    @script(
        # Translators: Description for the diagnostics script
        description=_("Write diagnostic information about the focused control to the NVDA log"),
        gesture="kb:NVDA+control+alt+shift+i",
    )
    def script_logDiagnostics(self, gesture):
        obj = api.getFocusObject()
        element = self._resolve(obj)
        details = {
            "automationId": self._attr(obj, "UIAAutomationId"),
            "className": self._attr(obj, "windowClassName"),
            "role": str(self._attr(obj, "role", None)),
            "hasName": bool(self._attr(obj, "name")),
            "recognisedAs": element["key"] if element else None,
            "context": self._contextPath(obj),
            "interfaceLanguage": self.detectedInterfaceLanguage(),
        }
        # Names and values can hold research data, so only structural facts
        # are logged; the log is meant to be safe to attach to a bug report.
        log.info("Atlas.ti diagnostics: %r" % details)
        # Translators: Announced after diagnostic information has been logged
        ui.message(_("Diagnostic information written to the NVDA log"))

    def _safeUICaptureRecords(self, root):
        """Return privacy-filtered structural records from an ATLAS.ti tree.

        Lists, tables, trees, data grids and all their descendants are
        pruned. Text, editable text, cells and list rows are never recorded.
        Values and descriptions are never read. This leaves the controls
        needed to improve accessibility--names, roles, automation ids and
        window classes--without quotation text, documents, codes, memos or
        other research content.
        """
        dataContainers = self._roles(
            "LIST", "TABLE", "TREEVIEW", "DATAGRID", "LISTITEM", "TABLEROW",
            "TREEVIEWITEM", "DATAITEM", "TABLECELL", "EDITABLETEXT", "TEXT",
            "STATICTEXT", "DOCUMENT")
        safeControls = self._roles(
            "WINDOW", "DIALOG", "PANE", "GROUPING", "TOOLBAR", "STATUSBAR",
            "MENUBAR", "MENU", "TAB", "BUTTON", "MENUITEM", "CHECKBOX",
            "TOGGLEBUTTON", "SPLITBUTTON", "RADIOBUTTON", "COLUMNHEADER")
        structuralContainers = self._roles(
            "WINDOW", "DIALOG", "PANE", "GROUPING", "TOOLBAR", "STATUSBAR",
            "MENUBAR", "MENU")
        queue = [(root, 0)] if root is not None else []
        visited = 0
        records = []
        while queue and visited < MAX_SEARCH_NODES:
            obj, depth = queue.pop(0)
            visited += 1
            role = self._attr(obj, "role", None)
            if role in dataContainers:
                continue
            if role in safeControls:
                element = self._resolve(obj)
                name = self._attr(obj, "name")
                if name:
                    name = " ".join(str(name).split())[:160]
                # Unknown window and pane titles can contain a project name.
                # Keep the structural identifiers but redact that title. A
                # known structural element is safe because it resolved to a
                # fixed label in the bilingual control table.
                if role in structuralContainers and element is None:
                    name = ""
                records.append({
                    "depth": depth,
                    "name": name or "",
                    "role": str(role),
                    "automationId": str(self._attr(obj, "UIAAutomationId"))[:160],
                    "className": str(self._attr(obj, "windowClassName"))[:160],
                    "recognisedAs": element["key"] if element else None,
                    "contextKeys": self._ancestorContextKeys(obj),
                })
            if depth >= MAX_SEARCH_DEPTH:
                continue
            try:
                children = obj.children or []
            except Exception:
                children = []
            for child in children:
                queue.append((child, depth + 1))
        return records

    @script(
        # Translators: Description for the opt-in privacy-filtered UI capture command
        description=_("Capture the privacy-filtered ATLAS.ti control tree in the NVDA log"),
        gesture="kb:NVDA+control+alt+shift+u",
    )
    def script_captureSafeUITree(self, gesture):
        if not getOption("enableSafeUICapture"):
            # Translators: The UI capture command is disabled until explicitly enabled
            ui.message(_(
                "UI tree capture is disabled. Enable privacy-filtered UI tree capture "
                "in NVDA Settings, Atlas.ti."))
            return
        root = self._getMainWindow(api.getFocusObject())
        records = self._safeUICaptureRecords(root)
        log.info("Atlas.ti safe UI tree capture begin schema=1 controls=%d" % len(records))
        for record in records:
            log.info("Atlas.ti UI control: %s" % json.dumps(
                record, ensure_ascii=False, sort_keys=True))
        log.info("Atlas.ti safe UI tree capture end")
        # Translators: Confirms the number of structural controls safely logged
        ui.message(_("Captured {count} controls in the NVDA log").format(
            count=len(records)))

    # =========================================================================
    # NAVIGATION IMPLEMENTATION
    # =========================================================================

    def _navigateTo(self, targetName):
        """Move focus to a named area of ATLAS.ti."""
        elementKeys = NAVIGATION_TARGETS.get(targetName, ())
        self._navigateToKeys(elementKeys, cacheKey=targetName)

    def _navigateToKeys(self, elementKeys, cacheKey=None):
        """Move focus to the first ATLAS.ti element matching ``elementKeys``.

        Shared by the fixed panel-navigation commands (via ``_navigateTo``,
        keyed by target name) and by the dynamic "go to accessible data
        view" command, which resolves its target at run time from an
        element's ``companion`` rather than from a fixed name.
        """
        primary = uiData.ELEMENTS.get(elementKeys[0]) if elementKeys else None
        displayName = self._label(primary) if primary else (elementKeys[0] if elementKeys else "?")
        cacheKey = cacheKey or (elementKeys[0] if elementKeys else None)

        try:
            panel = self._cachedPanel(cacheKey) if cacheKey else None
            if panel is None:
                mainWindow = self._getMainWindow(api.getFocusObject())
                panel = self._findElement(mainWindow, elementKeys)
                if panel is not None and cacheKey:
                    self._cachePanel(cacheKey, panel)

            if panel is None:
                # Translators: Reported when a panel is not present in the window
                ui.message(_("{panel} was not found. It may be closed; open it from "
                             "the Home tab.").format(panel=displayName))
                return

            self._lastPanel = elementKeys[0] if elementKeys else None
            warning = self._visualViewModeWarning(panel)
            self._focusPanel(panel, displayName, extra=warning)
        except Exception as error:
            log.error("Error navigating to %s: %s" % (elementKeys, error))
            # Translators: Error message when navigation fails
            ui.message(_("Could not move to {panel}").format(panel=displayName))

    def _visualViewModeWarning(self, panel):
        """Warn when ``panel`` currently shows a visual-only view mode.

        Atlas.ti's Code Manager and Document Manager can be switched, via
        the ribbon's View button, from their normal accessible List view
        into a Cloud, Bar chart or Treemap view. Those turn what would
        otherwise be a readable list into a single rendered graphic --
        worth surfacing the moment the researcher arrives, rather than
        leaving them to discover an apparently empty manager on their own.
        """
        viewModeKeys = ("viewCloud", "viewCodeBarChart", "viewTreemapMode")
        toggleRoles = self._roles("RADIOBUTTON", "TOGGLEBUTTON", "TAB")
        if not toggleRoles:
            return None
        try:
            for obj in self._walk(panel, maxNodes=300, maxDepth=5):
                role = self._attr(obj, "role", None)
                if role not in toggleRoles or not self._isSelected(obj):
                    continue
                element = self._resolve(obj)
                if element is not None and element["key"] in viewModeKeys:
                    conceptText = uiData.concept(element, language=outputLanguage())
                    # Translators: Warning spoken when a manager is showing a
                    # visual-only view instead of its accessible list
                    return _("Warning: {view} is active. {concept}").format(
                        view=self._label(element), concept=conceptText or "")
        except Exception as error:
            log.debug("View mode check failed: %s" % error)
        return None

    def _findVisualAncestor(self, obj):
        """Nearest visual-only Atlas.ti control at or above ``obj``.

        Returns ``(nvdaObject, element)``, or ``(None, None)`` when neither
        ``obj`` nor any of its ancestors is a recognised chart, diagram, or
        visual-only view mode. Unlike ``_contextElement`` this checks every
        ancestor's own resolved element directly regardless of "kind" -- a
        chart can be tagged as a button, a panel or a window in the table,
        and focus can land either on the chart's own container or on the
        ribbon button that opened it.
        """
        current = obj
        steps = 0
        while current is not None and steps < 40:
            element = self._resolve(current)
            if uiData.isVisualOnly(element):
                return current, element
            current = self._attr(current, "parent", None)
            steps += 1
        return None, None

    def _visualContent(self, container):
        """Try to read whatever accessible content a visual container has.

        Most charts and diagrams in Atlas.ti are rendered as one opaque
        graphic with no accessible children -- but some diagramming
        controls (particularly WPF-based ones like the Network Editor) do
        register a UI Automation element per shape. Rather than assume the
        worst, this always looks first: it walks the container bounded and
        collects the names of children whose role suggests real content
        (a shape, a label, a list item) rather than layout chrome like
        scrollbars. Only if nothing turns up does the caller fall back to
        the honest "not readable" explanation.
        """
        if container is None:
            return []
        contentRoles = self._roles(
            "GRAPHIC", "TEXT", "STATICTEXT", "LISTITEM", "TREEVIEWITEM", "LINK", "TABLECELL")
        if not contentRoles:
            return []
        ownName = self._attr(container, "name")
        found = []
        for child in self._walk(container, maxNodes=1500, maxDepth=8):
            if child is container:
                continue
            role = self._attr(child, "role", None)
            if role not in contentRoles:
                continue
            name = self._attr(child, "name")
            if not name or name == ownName or name in found:
                continue
            found.append(name)
            if len(found) >= MAX_LIST_ITEMS:
                break
        return found

    def _focusPanel(self, panel, displayName, extra=None):
        """Focus a panel and report only what actually happened.

        ``setFocus`` is queued rather than immediate, so success is verified
        on a short delay. When the panel refuses focus -- common for pure
        container objects -- the navigator object is moved there instead and
        the announcement says so. ``extra``, when given, is appended to
        whichever announcement ends up being spoken -- used to warn that a
        manager just reached is showing a visual-only view (Cloud, Bar
        chart, Treemap) instead of its normal accessible list.
        """
        def schedule(callback):
            if core is not None and hasattr(core, "callLater"):
                core.callLater(250, callback)
            else:  # pragma: no cover - only outside NVDA
                callback()

        def verify(allowRecovery=True):
            try:
                if self._focusIsWithin(panel):
                    message = displayName if not extra else "{0}. {1}".format(displayName, extra)
                    ui.message(message)
                    return
                if allowRecovery and self._focusFirstUsableDescendant(panel):
                    schedule(lambda: verify(False))
                    return
                self._fallbackToNavigator(panel, displayName, extra=extra)
            except Exception as error:
                log.debug("Focus verification failed: %s" % error)

        try:
            panel.setFocus()
        except Exception:
            if self._focusFirstUsableDescendant(panel):
                schedule(lambda: verify(False))
            else:
                self._fallbackToNavigator(panel, displayName, extra=extra)
            return
        schedule(verify)

    def _focusFirstUsableDescendant(self, panel):
        """Try the first enabled interactive child of a non-focusable panel."""
        dataRoles = self._roles("LIST", "TABLE", "TREEVIEW", "DATAGRID", "EDITABLETEXT")
        tabRoles = self._roles("TAB",)
        actionRoles = self._roles(
            "BUTTON", "MENUITEM", "CHECKBOX", "RADIOBUTTON", "TOGGLEBUTTON",
            "SPLITBUTTON")
        priorities = {}
        for priority, roles in enumerate((dataRoles, tabRoles, actionRoles)):
            for role in roles:
                priorities[role] = priority
        unavailable = getattr(getattr(controlTypes, "State", None), "UNAVAILABLE", None)
        candidates = []
        for order, candidate in enumerate(self._walk(panel, maxNodes=500, maxDepth=7)):
            role = self._attr(candidate, "role", None)
            if candidate is panel or role not in priorities:
                continue
            candidates.append((priorities[role], order, candidate))
        for _priority, _order, candidate in sorted(candidates, key=lambda item: item[:2]):
            try:
                states = candidate.states or set()
            except Exception:
                states = set()
            if unavailable is not None and unavailable in states:
                continue
            try:
                candidate.setFocus()
                return True
            except Exception:
                continue
        return False

    def _fallbackToNavigator(self, panel, displayName, extra=None):
        """Point NVDA's navigator object at a panel that cannot take focus."""
        try:
            api.setNavigatorObject(panel)
        except Exception:
            # Translators: Reported when focus could not be moved to a panel
            ui.message(_("{panel} could not take focus").format(panel=displayName))
            return
        # Translators: Reported when the navigator object was moved instead of focus
        message = _("{panel}, navigator object moved. Focus did not change.").format(
            panel=displayName)
        if extra:
            message = "{0}. {1}".format(message, extra)
        ui.message(message)

    def _focusIsWithin(self, panel):
        """Is the focus now on this panel or inside it?"""
        try:
            focus = api.getFocusObject()
        except Exception:
            return False
        current = focus
        steps = 0
        while current is not None and steps < 40:
            if current == panel:
                return True
            current = self._attr(current, "parent", None)
            steps += 1
        return False

    def _cachedPanel(self, targetName):
        reference = self._panelCache.get(targetName)
        if reference is None:
            return None
        panel = reference() if isinstance(reference, weakref.ReferenceType) else reference
        if panel is None:
            return None
        if not self._attr(panel, "isAlive", True):
            self._panelCache.pop(targetName, None)
            return None
        return panel

    def _cachePanel(self, targetName, panel):
        try:
            self._panelCache[targetName] = weakref.ref(panel)
        except TypeError:
            self._panelCache[targetName] = panel

    def _cyclePanel(self, step):
        """Move to the next or previous panel that actually exists."""
        try:
            currentIndex = PANEL_CYCLE.index(self._currentCycleTarget())
        except ValueError:
            currentIndex = -1 if step > 0 else 0
        for offset in range(1, len(PANEL_CYCLE) + 1):
            candidate = PANEL_CYCLE[(currentIndex + step * offset) % len(PANEL_CYCLE)]
            mainWindow = self._getMainWindow(api.getFocusObject())
            panel = self._findElement(mainWindow, NAVIGATION_TARGETS.get(candidate, ()))
            if panel is not None:
                self._cachePanel(candidate, panel)
                self._navigateTo(candidate)
                return
        # Translators: Reported when no other panel could be reached
        ui.message(_("No other Atlas.ti panel was found"))

    def _currentCycleTarget(self):
        """Which cycle entry the focus currently sits in, if any."""
        element = self._contextElement(api.getFocusObject())
        if element is None:
            return None
        for targetName, keys in NAVIGATION_TARGETS.items():
            if element["key"] in keys and targetName in PANEL_CYCLE:
                return targetName
        return None

    # =========================================================================
    # READING IMPLEMENTATION
    # =========================================================================

    def _readEntity(self, contexts, template, wrongContextMessage):
        """Announce the focused item, but only inside a matching container.

        Version 1.1.0 announced whatever had focus as a "code" or a
        "quotation" without checking, which produced confident but wrong
        feedback. Now a mismatch is reported honestly.
        """
        obj = api.getFocusObject()
        if obj is None or not self._inContext(obj, contexts):
            ui.message(wrongContextMessage)
            return
        name = self._attr(obj, "name") or self._attr(obj, "value")
        if not name:
            # Translators: Message when the focused item has no readable name
            ui.message(_("The focused item has no name"))
            return
        ui.message(template.format(name=name))

    def _rowCells(self, obj):
        """Return [(columnHeader, text)] for the focused row.

        Handles both shapes ATLAS.ti uses: a row object holding cell
        children, and a flat list item whose columns are exposed only as
        one concatenated name.
        """
        role = self._attr(obj, "role", None)
        if role not in self._roles("LISTITEM", "TABLEROW", "TREEVIEWITEM", "DATAITEM"):
            return []

        cells = []
        try:
            children = obj.children or []
        except Exception:
            children = []

        for child in children:
            text = self._attr(child, "value") or self._attr(child, "name")
            if not text:
                continue
            header = self._attr(child, "columnHeaderText")
            if header:
                # A number of ATLAS.ti labels collide across roles. "Start"
                # is both a real manager column and the German Home-tab
                # label. Column context must win here.
                element = uiData.resolveExact(
                    header,
                    kind="column",
                    context=self._ancestorContextKeys(obj),
                )
                if element is not None:
                    header = self._spokenLabel(element, controlType="column")
            cells.append((header, str(text)))

        if not cells:
            name = self._attr(obj, "name")
            if name:
                cells.append((None, str(name)))
        return cells

    def _listItemCount(self, obj):
        """How many items the list around ``obj`` holds."""
        listRoles = self._roles("LIST", "TABLE", "TREEVIEW", "DATAGRID")
        current = obj
        steps = 0
        while current is not None and steps < 10:
            if self._attr(current, "role", None) in listRoles:
                try:
                    return current.childCount
                except Exception:
                    return None
            current = self._attr(current, "parent", None)
            steps += 1
        return None

    def _statusBarText(self):
        """Text of the ATLAS.ti status bar, which reports item counts."""
        try:
            statusBar = api.getStatusBar()
        except Exception:
            statusBar = None
        if statusBar is not None:
            try:
                return api.getStatusBarText(statusBar)
            except Exception:
                return self._attr(statusBar, "name")
        mainWindow = self._getMainWindow(api.getFocusObject())
        bar = self._findElement(mainWindow, ("statusBar",))
        if bar is None:
            return None
        return self._objectText(bar)

    def _findDocumentName(self, obj):
        """Look for a document file name on the object or its ancestors."""
        current = obj
        steps = 0
        while current is not None and steps < 20:
            name = str(self._attr(current, "name"))
            lowered = name.lower()
            if any(lowered.endswith(ext) or (ext + " ") in lowered
                   for ext in DOCUMENT_EXTENSIONS):
                return name
            current = self._attr(current, "parent", None)
            steps += 1
        return None

    def _isSelected(self, obj):
        try:
            states = obj.states or set()
        except Exception:
            return False
        stateEnum = getattr(controlTypes, "State", None)
        selected = getattr(stateEnum, "SELECTED", None) if stateEnum else None
        return selected is not None and selected in states

    def _languageName(self, code):
        names = {
            # Translators: Name of a language Atlas.ti's interface can use
            "en": _("English"),
            # Translators: Name of a language Atlas.ti's interface can use
            "de": _("German"),
            # Translators: Name of a language Atlas.ti's interface can use
            "es": _("Spanish"),
            # Translators: Name of a language Atlas.ti's interface can use
            "pt": _("Portuguese"),
            # Translators: Name of a language Atlas.ti's interface can use
            "zh": _("Simplified Chinese"),
            # Translators: Name of a language Atlas.ti controls can expose
            "el": _("Greek"),
        }
        return names.get(code, code)

    def _showList(self, title, lines):
        """Show lines in a browsable window, or speak them if that fails.

        A browsable message can be reviewed line by line and copied, which
        a single long spoken sentence cannot.
        """
        text = "\n".join(str(line) for line in lines)
        try:
            ui.browseableMessage(text, title)
        except Exception:
            ui.message(". ".join(str(line) for line in lines if line))
