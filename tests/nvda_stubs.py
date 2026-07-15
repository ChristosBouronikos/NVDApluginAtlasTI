# -*- coding: utf-8 -*-
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
    appModuleHandler.registerAppModule = None
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
    sys.modules["api"] = api

    ui = types.ModuleType("ui")
    ui.message = lambda *args, **kwargs: None
    sys.modules["ui"] = ui

    controlTypes = types.ModuleType("controlTypes")

    class Role:
        BUTTON = "BUTTON"
        WINDOW = "WINDOW"

    controlTypes.Role = Role
    sys.modules["controlTypes"] = controlTypes

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
