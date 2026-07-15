# -*- coding: utf-8 -*-
# =============================================================================
# Atlas.ti Helper Global Plugin for NVDA
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
Atlas.ti Helper Global Plugin

Attempts to register the app module for various Atlas.ti executable names.
If NVDA doesn't expose a public registration API, alias appModules provide
compatibility for common executable variants.

Both mechanisms are kept deliberately:
- appModuleHandler.registerAppModule (used here) is the primary path and
  covers any executable name at runtime, but it's not guaranteed to exist
  on every NVDA version this add-on supports.
- The alias files in appModules/ (atlasti.py, atlasti9.py, atlasti22.py,
  etc.) are NVDA's own executable-name-to-module convention, so they work
  even when registerAppModule is unavailable or fails silently.
Do not remove the alias files as a "duplication cleanup" without also
verifying registerAppModule is universally available on all supported
NVDA versions.
"""

import globalPluginHandler
import appModuleHandler
from logHandler import log

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
    "ATLAS.ti",      # Mixed case
    "ATLASti",       # All caps no period
]


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    """
    Global plugin to ensure Atlas.ti app module loads for all executable variants.
    
    Author: Christos Bouronikos <chrisbouronikos@gmail.com>
    Donations: https://paypal.me/christosbouronikos
    """
    
    def __init__(self):
        super().__init__()
        self._registerAtlasTiVariants()
    
    def _registerAtlasTiVariants(self):
        """Register app module for known Atlas.ti executable names."""
        try:
            # Import the atlas app module
            from appModules import atlas
            register = getattr(appModuleHandler, "registerAppModule", None)
            if callable(register):
                for exeName in ATLAS_TI_EXECUTABLES:
                    try:
                        register(exeName, atlas.AppModule)
                    except Exception as e:
                        log.debug(f"Could not register {exeName}: {e}")
                log.debug("Registered Atlas.ti app module variants via registerAppModule")
            else:
                # Fallback relies on alias appModules (e.g. atlasti.py, atlasti25.py)
                log.debug("No app module registration API; relying on alias appModules")
        except ImportError:
            log.warning("Could not import atlas app module")
        except Exception as e:
            log.error(f"Error registering Atlas.ti variants: {e}")
    
    def terminate(self):
        """Clean up on plugin unload."""
        super().terminate()
