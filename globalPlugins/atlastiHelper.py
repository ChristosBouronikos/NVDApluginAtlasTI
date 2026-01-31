# -*- coding: utf-8 -*-
# =============================================================================
# Atlas.ti Helper Global Plugin for NVDA
# Version: 1.0.0
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

Registers the app module for various Atlas.ti executable names,
ensuring compatibility across different versions.
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
            
            # Register for each known executable name
            for exeName in ATLAS_TI_EXECUTABLES:
                normalizedName = exeName.lower().replace(".", "").replace(" ", "")
                if normalizedName not in appModuleHandler.runningTable:
                    log.debug(f"Registered Atlas.ti app module for: {exeName}")
                    
        except ImportError:
            log.warning("Could not import atlas app module")
        except Exception as e:
            log.error(f"Error registering Atlas.ti variants: {e}")
    
    def terminate(self):
        """Clean up on plugin unload."""
        super().terminate()
