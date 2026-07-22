# -*- coding: utf-8 -*-
# =============================================================================
# Atlas.ti Helper Global Plugin for NVDA
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

"""Atlas.ti Helper Global Plugin.

Three jobs:

1. Registers the ATLAS.ti app module for every executable name ATLAS.ti has
   shipped under, so the add-on loads regardless of ATLAS.ti version.
   Both mechanisms below are kept deliberately:
   - appModuleHandler.registerExecutableWithAppModule is the primary path
     and covers every known executable name at runtime.
   - The alias files in appModules/ (atlasti.py, atlas_ti.py,
     atlas_ti26.py, etc.) follow NVDA's executable-name-to-module
     convention, so they work even if runtime registration is unavailable.
   Do not remove the alias files as a "duplication cleanup" without also
   verifying runtime registration on every supported NVDA version.

2. Registers the add-on's configuration spec, so the settings the app
   module reads through ``config.conf`` always have a valid default even
   before the settings panel has ever been opened.

3. Adds an NVDA Settings panel ("Atlas.ti") so the user can pick the speech
   language (English, Greek, or follow NVDA), and toggle bilingual labels,
   automatic translation of recognised controls, and unlabelled-button
   naming, without editing any file by hand.
"""

import globalPluginHandler
import appModuleHandler
from logHandler import log

try:
    import config
except ImportError:  # pragma: no cover - config always exists inside NVDA
    config = None

try:
    import gui
    import wx
except ImportError:  # pragma: no cover - headless/test environments
    gui = None
    wx = None

import addonHandler

addonHandler.initTranslation()

# Known Atlas.ti executable names across versions
ATLAS_TI_EXECUTABLES = [
    "atlas",         # Generic
    "atlas.ti",      # With period
    "atlasti",       # Without period
    "atlas.ti9",     # Version 9
    "atlas.ti22",    # Version 22
    "atlas.ti23",    # Version 23
    "atlas.ti24",    # Version 24
    "atlas.ti25",    # Version 25
    "atlas.ti26",    # Version 26
    "ATLAS.ti",      # Mixed case
    "ATLASti",       # All caps no period
]

CONFIG_SECTION = "atlastiAccessibility"

CONFIG_SPEC = {
    "outputLanguage": "string(default=auto)",
    "bilingualLabels": "boolean(default=True)",
    "translateLabels": "boolean(default=True)",
    "labelUnlabeledButtons": "boolean(default=True)",
    "announcePanelChanges": "boolean(default=True)",
    "announceRibbonTabs": "boolean(default=True)",
    "announceControlStates": "boolean(default=True)",
    "speakHints": "boolean(default=False)",
    "enableSafeUICapture": "boolean(default=False)",
}


def _registerConfigSpec():
    """Register the add-on's config section, if it isn't already there."""
    if config is None:
        return
    try:
        if CONFIG_SECTION not in config.conf.spec:
            config.conf.spec[CONFIG_SECTION] = CONFIG_SPEC
    except Exception as error:
        log.debug("Could not register Atlas.ti config spec: %s" % error)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    """
    Global plugin to ensure Atlas.ti app module loads for all executable
    variants, and to expose the add-on's settings in NVDA's Settings dialog.

    Author: Christos Bouronikos <chrisbouronikos@gmail.com>
    Donations: https://paypal.me/christosbouronikos
    """

    def __init__(self):
        super().__init__()
        self._registeredExecutables = []
        _registerConfigSpec()
        self._registerAtlasTiVariants()
        self._registerSettingsPanel()

    def _registerAtlasTiVariants(self):
        """Register app module for known Atlas.ti executable names."""
        try:
            # Import first so a broken app module is reported now rather than
            # only when ATLAS.ti starts.  NVDA's registration API expects the
            # module name ("atlas"), not the AppModule class itself.
            from appModules import atlas
            moduleName = atlas.__name__.rsplit(".", 1)[-1]
            register = getattr(
                appModuleHandler, "registerExecutableWithAppModule", None)
            if callable(register):
                # NVDA obtains executable names in lowercase.  Normalising
                # here also removes duplicate mixed-case spellings.
                for exeName in dict.fromkeys(
                    name.lower() for name in ATLAS_TI_EXECUTABLES):
                    try:
                        register(exeName, moduleName)
                        self._registeredExecutables.append(exeName)
                    except Exception as e:
                        log.debug(f"Could not register {exeName}: {e}")
                log.debug(
                    "Registered Atlas.ti app module variants via "
                    "registerExecutableWithAppModule")
            else:
                # NVDA replaces dots in executable names with underscores,
                # hence both atlasti.py and atlas_ti*.py aliases are shipped.
                log.debug("No app module registration API; relying on alias appModules")
        except ImportError:
            log.warning("Could not import atlas app module")
        except Exception as e:
            log.error(f"Error registering Atlas.ti variants: {e}")

    def _registerSettingsPanel(self):
        """Add the "Atlas.ti" category to NVDA's Settings dialog."""
        if gui is None or not hasattr(gui, "settingsDialogs"):
            log.debug("GUI not available; skipping Atlas.ti settings panel")
            return
        try:
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(
                AtlasTiSettingsPanel)
        except Exception as error:
            log.debug("Could not add Atlas.ti settings panel: %s" % error)

    def terminate(self):
        """Clean up on plugin unload."""
        unregister = getattr(appModuleHandler, "unregisterExecutable", None)
        if callable(unregister):
            for exeName in self._registeredExecutables:
                try:
                    unregister(exeName)
                except Exception as error:
                    log.debug(f"Could not unregister {exeName}: {error}")
        self._registeredExecutables = []
        if gui is not None and hasattr(gui, "settingsDialogs"):
            try:
                gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(
                    AtlasTiSettingsPanel)
            except Exception:
                pass
        super().terminate()


if gui is not None:

    class AtlasTiSettingsPanel(gui.settingsDialogs.SettingsPanel):
        """NVDA Settings panel for the Atlas.ti accessibility add-on."""

        # Translators: Title of the Atlas.ti settings category in NVDA Settings
        title = _("Atlas.ti")

        _LANGUAGE_CHOICES = ("auto", "en", "el")

        def makeSettings(self, settingsSizer):
            helper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

            # Translators: Label for the speech language choice in Atlas.ti settings
            languageLabel = _("&Speech language:")
            self._languageLabels = [
                # Translators: Speech language option that follows NVDA's own language
                _("Follow NVDA's language"),
                # Translators: Speech language option for English
                _("English"),
                # Translators: Speech language option for Greek
                _("Greek"),
            ]
            self.languageChoice = helper.addLabeledControl(
                languageLabel, wx.Choice, choices=self._languageLabels)
            currentLanguage = self._getOption("outputLanguage", "auto")
            try:
                self.languageChoice.SetSelection(
                    self._LANGUAGE_CHOICES.index(currentLanguage))
            except ValueError:
                self.languageChoice.SetSelection(0)

            self.bilingualCheckbox = helper.addItem(wx.CheckBox(
                self,
                # Translators: Checkbox in Atlas.ti settings
                label=_("Speak the &original label after a translated one")))
            self.bilingualCheckbox.SetValue(self._getOption("bilingualLabels", True))

            self.translateCheckbox = helper.addItem(wx.CheckBox(
                self,
                # Translators: Checkbox in Atlas.ti settings
                label=_("&Translate recognised Atlas.ti controls into the "
                        "speech language")))
            self.translateCheckbox.SetValue(self._getOption("translateLabels", True))

            self.labelButtonsCheckbox = helper.addItem(wx.CheckBox(
                self,
                # Translators: Checkbox in Atlas.ti settings
                label=_("&Name buttons that Atlas.ti leaves unlabelled")))
            self.labelButtonsCheckbox.SetValue(
                self._getOption("labelUnlabeledButtons", True))

            self.announcePanelsCheckbox = helper.addItem(wx.CheckBox(
                self,
                # Translators: Checkbox in Atlas.ti settings
                label=_("Announce the panel when it &changes")))
            self.announcePanelsCheckbox.SetValue(
                self._getOption("announcePanelChanges", True))

            self.announceRibbonCheckbox = helper.addItem(wx.CheckBox(
                self,
                # Translators: Checkbox in Atlas.ti settings
                label=_("Announce the ribbon &tab when it changes")))
            self.announceRibbonCheckbox.SetValue(
                self._getOption("announceRibbonTabs", True))

            self.announceStatesCheckbox = helper.addItem(wx.CheckBox(
                self,
                # Translators: Checkbox for translated state changes
                label=_("Announce translated control &states")))
            self.announceStatesCheckbox.SetValue(
                self._getOption("announceControlStates", True))

            self.speakHintsCheckbox = helper.addItem(wx.CheckBox(
                self,
                # Translators: Checkbox in Atlas.ti settings
                label=_("Speak a short &hint when describing a control")))
            self.speakHintsCheckbox.SetValue(self._getOption("speakHints", False))

            self.safeCaptureCheckbox = helper.addItem(wx.CheckBox(
                self,
                # Translators: Opt-in setting for privacy-filtered UI tree logging
                label=_("Enable privacy-filtered ATLAS.ti &UI tree capture")))
            self.safeCaptureCheckbox.SetValue(
                self._getOption("enableSafeUICapture", False))

        def onSave(self):
            self._setOption(
                "outputLanguage",
                self._LANGUAGE_CHOICES[self.languageChoice.GetSelection()])
            self._setOption("bilingualLabels", self.bilingualCheckbox.GetValue())
            self._setOption("translateLabels", self.translateCheckbox.GetValue())
            self._setOption(
                "labelUnlabeledButtons", self.labelButtonsCheckbox.GetValue())
            self._setOption(
                "announcePanelChanges", self.announcePanelsCheckbox.GetValue())
            self._setOption(
                "announceRibbonTabs", self.announceRibbonCheckbox.GetValue())
            self._setOption(
                "announceControlStates", self.announceStatesCheckbox.GetValue())
            self._setOption("speakHints", self.speakHintsCheckbox.GetValue())
            self._setOption(
                "enableSafeUICapture", self.safeCaptureCheckbox.GetValue())

        @staticmethod
        def _getOption(name, default):
            if config is None:
                return default
            try:
                return config.conf[CONFIG_SECTION][name]
            except Exception:
                return default

        @staticmethod
        def _setOption(name, value):
            if config is None:
                return
            try:
                config.conf[CONFIG_SECTION][name] = value
            except Exception as error:
                log.debug("Could not save Atlas.ti option %s: %s" % (name, error))
