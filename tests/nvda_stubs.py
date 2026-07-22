# -*- coding: utf-8 -*-
# Author: Christos Bouronikos <chrisbouronikos@gmail.com>
# GitHub: https://github.com/ChristosBouronikos
# Donations: https://paypal.me/christosbouronikos
"""Minimal stand-ins for the NVDA modules addon code imports.

NVDA's Python API (appModuleHandler, api, ui, controlTypes, addonHandler,
scriptHandler, logHandler, globalPluginHandler) only exists inside a running
NVDA process. These stubs let the addon's pure logic be imported and tested
outside NVDA, on plain CPython.
"""

import builtins
import sys
import types


def install():
    """Register fake NVDA modules in sys.modules, if not already present."""
    if "appModuleHandler" in sys.modules:
        return

    appModuleHandler = types.ModuleType("appModuleHandler")

    class AppModule:
        def __init__(self, *args, **kwargs):
            pass

        def terminate(self):
            pass

    appModuleHandler.AppModule = AppModule
    appModuleHandler.registeredExecutableAppModules = {}

    def registerExecutableWithAppModule(executableName, appModuleName):
        appModuleHandler.registeredExecutableAppModules[executableName] = appModuleName

    def unregisterExecutable(executableName):
        appModuleHandler.registeredExecutableAppModules.pop(executableName, None)

    appModuleHandler.registerExecutableWithAppModule = registerExecutableWithAppModule
    appModuleHandler.unregisterExecutable = unregisterExecutable
    sys.modules["appModuleHandler"] = appModuleHandler

    globalPluginHandler = types.ModuleType("globalPluginHandler")

    class GlobalPlugin:
        def __init__(self, *args, **kwargs):
            pass

        def terminate(self):
            pass

    globalPluginHandler.GlobalPlugin = GlobalPlugin
    sys.modules["globalPluginHandler"] = globalPluginHandler

    api = types.ModuleType("api")
    api.getFocusObject = lambda: None
    api.getForegroundObject = lambda: None
    api.getStatusBar = lambda: None
    api.getStatusBarText = lambda obj: ""
    api.setNavigatorObject = lambda obj: None
    sys.modules["api"] = api

    ui = types.ModuleType("ui")
    ui.message = lambda *args, **kwargs: None
    ui.browseableMessage = lambda *args, **kwargs: None
    sys.modules["ui"] = ui

    controlTypes = types.ModuleType("controlTypes")

    class Role:
        BUTTON = "BUTTON"
        WINDOW = "WINDOW"
        TAB = "TAB"
        MENUITEM = "MENUITEM"
        CHECKBOX = "CHECKBOX"
        TOGGLEBUTTON = "TOGGLEBUTTON"
        SPLITBUTTON = "SPLITBUTTON"
        LISTITEM = "LISTITEM"
        TABLEROW = "TABLEROW"
        TREEVIEWITEM = "TREEVIEWITEM"
        DATAITEM = "DATAITEM"
        LIST = "LIST"
        TABLE = "TABLE"
        TREEVIEW = "TREEVIEW"
        DATAGRID = "DATAGRID"
        RADIOBUTTON = "RADIOBUTTON"
        GRAPHIC = "GRAPHIC"
        TEXT = "TEXT"
        STATICTEXT = "STATICTEXT"
        LINK = "LINK"
        TABLECELL = "TABLECELL"
        COLUMNHEADER = "COLUMNHEADER"
        DIALOG = "DIALOG"
        PANE = "PANE"
        GROUPING = "GROUPING"
        TOOLBAR = "TOOLBAR"
        STATUSBAR = "STATUSBAR"
        MENUBAR = "MENUBAR"
        MENU = "MENU"
        EDITABLETEXT = "EDITABLETEXT"
        DOCUMENT = "DOCUMENT"

        def displayString(self):  # pragma: no cover - not used as a value here
            return None

    class State:
        SELECTED = "SELECTED"
        CHECKED = "CHECKED"
        HALFCHECKED = "HALFCHECKED"
        EXPANDED = "EXPANDED"
        COLLAPSED = "COLLAPSED"
        UNAVAILABLE = "UNAVAILABLE"
        PRESSED = "PRESSED"

    controlTypes.Role = Role
    controlTypes.State = State
    controlTypes.roleLabels = {}
    sys.modules["controlTypes"] = controlTypes

    config = types.ModuleType("config")

    class _ConfSpec(dict):
        pass

    class _Conf(dict):
        def __init__(self):
            super().__init__()
            self.spec = _ConfSpec()

    config.conf = _Conf()
    sys.modules["config"] = config

    languageHandler = types.ModuleType("languageHandler")
    languageHandler.getLanguage = lambda: "en"
    sys.modules["languageHandler"] = languageHandler

    core = types.ModuleType("core")
    core.callLater = lambda delay, func: func()
    sys.modules["core"] = core

    addonHandler = types.ModuleType("addonHandler")

    def initTranslation():
        builtins.__dict__.setdefault("_", lambda s: s)

    addonHandler.initTranslation = initTranslation
    sys.modules["addonHandler"] = addonHandler

    scriptHandler = types.ModuleType("scriptHandler")

    def script(*args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    scriptHandler.script = script
    scriptHandler.getLastScriptRepeatCount = lambda: 0
    sys.modules["scriptHandler"] = scriptHandler

    logHandler = types.ModuleType("logHandler")

    class _Log:
        def info(self, *args, **kwargs):
            pass

        def debug(self, *args, **kwargs):
            pass

        def error(self, *args, **kwargs):
            pass

        def warning(self, *args, **kwargs):
            pass

    logHandler.log = _Log()
    sys.modules["logHandler"] = logHandler
