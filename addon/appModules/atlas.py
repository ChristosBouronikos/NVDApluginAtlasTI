# -*- coding: utf-8 -*-
# =============================================================================
# Atlas.ti Accessibility App Module for NVDA
# Version: 1.1.0
# =============================================================================
# 
# Author: Christos Bouronikos
# Email: chrisbouronikos@gmail.com
# Donations: https://paypal.me/christosbouronikos
#
# Copyright (C) 2026 Christos Bouronikos
# This file is covered by the GNU General Public License v2.
# See the file LICENSE for more details.
#
# If you find this plugin helpful, please consider donating!
# =============================================================================

"""
Atlas.ti Accessibility App Module for NVDA v1.1.0

Provides accessibility enhancements for Atlas.ti qualitative data analysis:
- Quick panel navigation (Documents, Codes, Quotations, Memos, Navigator)
- Reading helpers for codes, quotations, and documents
- Improved control labeling for unlabeled buttons
"""

import appModuleHandler
import api
import ui
import controlTypes
import addonHandler
import re
import weakref
from scriptHandler import script, getLastScriptRepeatCount
from logHandler import log

# Initialize translation support
addonHandler.initTranslation()

# =============================================================================
# PANEL NAMES (Translatable)
# =============================================================================

PANEL_NAMES = {
    # Translators: Name of the Documents panel in Atlas.ti
    "DocumentManager": _("Documents Panel"),
    # Translators: Name of the Codes panel in Atlas.ti
    "CodeManager": _("Codes Panel"), 
    # Translators: Name of the Quotations panel in Atlas.ti
    "QuotationManager": _("Quotations Panel"),
    # Translators: Name of the Memos panel in Atlas.ti
    "MemoManager": _("Memos Panel"),
    # Translators: Name of the Project Navigator in Atlas.ti
    "ProjectNavigator": _("Project Navigator"),
}

PANEL_TOKENS = {
    "DocumentManager": ["DocumentManager", "Documents", "Document Manager"],
    "CodeManager": ["CodeManager", "Codes", "Code Manager"],
    "QuotationManager": ["QuotationManager", "Quotations", "Quotation Manager"],
    "MemoManager": ["MemoManager", "Memos", "Memo Manager"],
    "ProjectNavigator": ["ProjectNavigator", "Project Navigator", "Navigator"],
}

BUTTON_LABELS = {
    # Translators: Button to create a new project
    "NewProject": _("New Project"),
    # Translators: Button to open a project
    "OpenProject": _("Open Project"),
    # Translators: Button to save the project
    "SaveProject": _("Save Project"),
    # Translators: Button to import documents
    "Import": _("Import Documents"),
    # Translators: Button to export data
    "Export": _("Export"),
    # Translators: Button to create a new code
    "CreateCode": _("Create New Code"),
    # Translators: Button to create a new memo
    "CreateMemo": _("Create New Memo"),
    # Translators: Button to create a quotation
    "CreateQuotation": _("Create Quotation"),
    # Translators: Search button
    "Search": _("Search"),
    # Translators: Filter button
    "Filter": _("Filter"),
}

_BUTTON_LABELS_LOWER = {k.lower(): v for k, v in BUTTON_LABELS.items()}


# =============================================================================
# MAIN APP MODULE CLASS
# =============================================================================

class AppModule(appModuleHandler.AppModule):
    """
    NVDA App Module for Atlas.ti v1.1.0
    
    Author: Christos Bouronikos <chrisbouronikos@gmail.com>
    Donations: https://paypal.me/christosbouronikos
    """
    
    # Translators: Category for Atlas.ti scripts in NVDA Input Gestures dialog
    scriptCategory = _("Atlas.ti")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lastPanel = None
        self._panelCache = {}
        log.info("Atlas.ti accessibility app module v1.1.0 loaded")
    
    def terminate(self):
        """Clean up when the app module is unloaded."""
        log.info("Atlas.ti accessibility app module unloaded")
        super().terminate()
    
    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================
    
    def event_NVDAObject_init(self, obj):
        """Modify NVDA objects during initialization for better labeling."""
        # Handle unlabeled buttons
        if obj.role == controlTypes.Role.BUTTON and not obj.name:
            automationId = getattr(obj, 'UIAAutomationId', None)
            if automationId:
                label = BUTTON_LABELS.get(automationId)
                if not label:
                    label = _BUTTON_LABELS_LOWER.get(str(automationId).lower())
                if label:
                    obj.name = label
        
        # Handle toolbar buttons with only icons
        if obj.role == controlTypes.Role.BUTTON:
            if not obj.name and hasattr(obj, 'description') and obj.description:
                obj.name = obj.description
    
    # =========================================================================
    # PANEL NAVIGATION SCRIPTS
    # =========================================================================
    
    @script(
        # Translators: Description for the go to documents script
        description=_("Jump to Documents panel"),
        gesture="kb:NVDA+control+alt+d"
    )
    def script_goToDocuments(self, gesture):
        """Navigate to the Documents panel."""
        self._navigateToPanel(_("Documents"), "DocumentManager")
    
    @script(
        # Translators: Description for the go to codes script
        description=_("Jump to Codes panel"), 
        gesture="kb:NVDA+control+alt+c"
    )
    def script_goToCodes(self, gesture):
        """Navigate to the Codes panel."""
        self._navigateToPanel(_("Codes"), "CodeManager")
    
    @script(
        # Translators: Description for the go to quotations script
        description=_("Jump to Quotations panel"),
        gesture="kb:NVDA+control+alt+q"
    )
    def script_goToQuotations(self, gesture):
        """Navigate to the Quotations panel."""
        self._navigateToPanel(_("Quotations"), "QuotationManager")
    
    @script(
        # Translators: Description for the go to memos script
        description=_("Jump to Memos panel"),
        gesture="kb:NVDA+control+alt+m"
    )
    def script_goToMemos(self, gesture):
        """Navigate to the Memos panel."""
        self._navigateToPanel(_("Memos"), "MemoManager")
    
    @script(
        # Translators: Description for the go to project navigator script
        description=_("Jump to Project Navigator"),
        gesture="kb:NVDA+control+alt+p"
    )
    def script_goToNavigator(self, gesture):
        """Navigate to the Project Navigator panel."""
        self._navigateToPanel(_("Project Navigator"), "ProjectNavigator")
    
    # =========================================================================
    # READING HELPER SCRIPTS
    # =========================================================================
    
    @script(
        # Translators: Description for the read code script
        description=_("Read current code details"),
        gesture="kb:NVDA+control+alt+shift+c"
    )
    def script_readCode(self, gesture):
        """Read details about the currently selected code."""
        obj = api.getFocusObject()
        codeInfo = self._getCodeInfo(obj)
        if codeInfo:
            ui.message(codeInfo)
        else:
            # Translators: Message when no code is selected
            ui.message(_("No code selected or code information unavailable"))
    
    @script(
        # Translators: Description for the read quotation script
        description=_("Read current quotation text"),
        gesture="kb:NVDA+control+alt+shift+q"
    )
    def script_readQuotation(self, gesture):
        """Read the currently selected quotation."""
        obj = api.getFocusObject()
        quotationText = self._getQuotationText(obj)
        if quotationText:
            ui.message(quotationText)
        else:
            # Translators: Message when no quotation is selected
            ui.message(_("No quotation selected or quotation text unavailable"))
    
    @script(
        # Translators: Description for the read document script
        description=_("Read document information"),
        gesture="kb:NVDA+control+alt+shift+d"
    )
    def script_readDocument(self, gesture):
        """Read information about the current document."""
        obj = api.getFocusObject()
        docInfo = self._getDocumentInfo(obj)
        if docInfo:
            ui.message(docInfo)
        else:
            # Translators: Message when no document info is available
            ui.message(_("No document information available"))
    
    @script(
        # Translators: Description for the announce panel script
        description=_("Announce current panel"),
        gesture="kb:NVDA+control+alt+shift+p"
    )
    def script_announcePanel(self, gesture):
        """Announce which panel currently has focus."""
        obj = api.getFocusObject()
        panelName = self._getPanelName(obj)
        if panelName:
            # Translators: Announced when reporting current panel
            ui.message(_("Current panel: {panel}").format(panel=panelName))
        else:
            # Translators: Message when panel cannot be determined
            ui.message(_("Unable to determine current panel"))
    
    @script(
        # Translators: Description for the list shortcuts script
        description=_("List available Atlas.ti shortcuts"),
        gesture="kb:NVDA+control+alt+shift+h"
    )
    def script_listShortcuts(self, gesture):
        """Announce available Atlas.ti accessibility shortcuts."""
        shortcuts = [
            # Translators: Shortcut help items
            _("Panel Navigation:"),
            _("NVDA+Ctrl+Alt+D: Documents"),
            _("NVDA+Ctrl+Alt+C: Codes"),
            _("NVDA+Ctrl+Alt+Q: Quotations"),
            _("NVDA+Ctrl+Alt+M: Memos"),
            _("NVDA+Ctrl+Alt+P: Project Navigator"),
            _("Reading:"),
            _("NVDA+Ctrl+Alt+Shift+C: Read code"),
            _("NVDA+Ctrl+Alt+Shift+Q: Read quotation"),
            _("NVDA+Ctrl+Alt+Shift+D: Read document"),
            _("NVDA+Ctrl+Alt+Shift+P: Current panel"),
            _("NVDA+Ctrl+Alt+Shift+H: This help"),
        ]
        ui.message(". ".join(shortcuts))
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _navigateToPanel(self, panelDisplayName, panelId):
        """Navigate to a specific panel in Atlas.ti."""
        try:
            cachedRef = self._panelCache.get(panelId)
            if cachedRef:
                cachedPanel = cachedRef() if isinstance(cachedRef, weakref.ReferenceType) else cachedRef
                if cachedPanel and getattr(cachedPanel, "isAlive", True):
                    cachedPanel.setFocus()
                    self._lastPanel = panelId
                    ui.message(_("{panel} panel").format(panel=panelDisplayName))
                    return

            focus = api.getFocusObject()
            mainWindow = self._getMainWindow(focus)
            
            if mainWindow:
                panelTokens = self._getPanelTokens(panelId, panelDisplayName)
                panel = self._findPanelByTokens(mainWindow, panelTokens)
                if panel:
                    panel.setFocus()
                    try:
                        self._panelCache[panelId] = weakref.ref(panel)
                    except TypeError:
                        self._panelCache[panelId] = panel
                    self._lastPanel = panelId
                    # Translators: Announced after navigating to a panel
                    ui.message(_("{panel} panel").format(panel=panelDisplayName))
                    return
            
            # Translators: Message when automatic navigation may not work
            ui.message(_("Trying to navigate to {panel}. Use Atlas.ti's View menu if this doesn't work.").format(panel=panelDisplayName))
            
        except Exception as e:
            log.error(f"Error navigating to panel {panelId}: {e}")
            # Translators: Error message when navigation fails
            ui.message(_("Could not navigate to {panel} panel").format(panel=panelDisplayName))
    
    def _getMainWindow(self, obj):
        """Get the main Atlas.ti window from any child object."""
        current = obj
        lastWindow = None
        while current:
            if current.role == controlTypes.Role.WINDOW:
                lastWindow = current
            current = current.parent
        if lastWindow:
            return lastWindow
        try:
            return api.getForegroundObject()
        except Exception:
            return None
    
    def _findPanelByTokens(self, container, tokens):
        """Find a panel by matching automation IDs, class names, or names."""
        try:
            normalizedTokens = [self._normalizeToken(t) for t in tokens if t]
            if not normalizedTokens:
                return None
            for child in container.recursiveDescendants:
                try:
                    values = []
                    automationId = getattr(child, 'UIAAutomationId', '')
                    className = getattr(child, 'windowClassName', '')
                    name = getattr(child, 'name', '')
                    if automationId:
                        values.append(self._normalizeToken(str(automationId)))
                    if className:
                        values.append(self._normalizeToken(str(className)))
                    if name:
                        values.append(self._normalizeToken(str(name)))

                    if not values:
                        continue

                    for token in normalizedTokens:
                        for value in values:
                            if token and token in value:
                                return child
                except Exception:
                    continue
        except Exception as e:
            log.debug(f"Error searching for panel: {e}")
        
        return None
    
    def _getPanelName(self, obj):
        """Determine which panel an object belongs to."""
        current = obj
        while current:
            values = []
            automationId = getattr(current, 'UIAAutomationId', '')
            className = getattr(current, 'windowClassName', '')
            name = getattr(current, 'name', '')
            if automationId:
                values.append(self._normalizeToken(str(automationId)))
            if className:
                values.append(self._normalizeToken(str(className)))
            if name:
                values.append(self._normalizeToken(str(name)))

            for panelId, panelName in PANEL_NAMES.items():
                tokens = self._getPanelTokens(panelId, panelName)
                if self._tokensMatch(tokens, values):
                    return panelName
            
            current = current.parent
        if self._lastPanel and self._lastPanel in PANEL_NAMES:
            return PANEL_NAMES[self._lastPanel]
        return None

    def _getPanelTokens(self, panelId, panelDisplayName=None):
        tokens = list(PANEL_TOKENS.get(panelId, []))
        tokens.append(panelId)
        if panelDisplayName:
            tokens.append(panelDisplayName)
        return tokens

    def _tokensMatch(self, tokens, values):
        normalizedTokens = [self._normalizeToken(t) for t in tokens if t]
        for token in normalizedTokens:
            for value in values:
                if token and token in value:
                    return True
        return False

    def _normalizeToken(self, value):
        return re.sub(r"[^a-z0-9]+", "", str(value).lower())
    
    def _getCodeInfo(self, obj):
        """Extract code information from the focused object."""
        try:
            name = obj.name if obj.name else _("Unnamed code")
            # Translators: Format for code information
            return _("Code: {name}").format(name=name)
        except Exception as e:
            log.debug(f"Error getting code info: {e}")
            return None
    
    def _getQuotationText(self, obj):
        """Extract quotation text from the focused object."""
        try:
            if hasattr(obj, 'value') and obj.value:
                # Translators: Format for quotation text
                return _("Quotation: {text}").format(text=obj.value)
            elif obj.name:
                return _("Quotation: {text}").format(text=obj.name)
            return None
        except Exception as e:
            log.debug(f"Error getting quotation text: {e}")
            return None
    
    def _getDocumentInfo(self, obj):
        """Extract document information from the focused object."""
        try:
            current = obj
            while current:
                name = getattr(current, 'name', '')
                
                if any(ext in name.lower() for ext in ['.pdf', '.txt', '.docx', '.doc', '.rtf']):
                    # Translators: Format for document info
                    return _("Document: {name}").format(name=name)
                
                current = current.parent
            
            mainWindow = self._getMainWindow(obj)
            if mainWindow and mainWindow.name:
                # Translators: Format for current context
                return _("Current context: {name}").format(name=mainWindow.name)
            
            return None
        except Exception as e:
            log.debug(f"Error getting document info: {e}")
            return None
