#!/bin/bash
# =============================================================================
# Build script for Atlas.ti NVDA Add-on
# Version: 1.0.0
# =============================================================================
# 
# Author: Christos Bouronikos
# Email: chrisbouronikos@gmail.com
# Donations: https://paypal.me/christosbouronikos
#
# Copyright (C) 2026 Christos Bouronikos
# =============================================================================

set -e

ADDON_NAME="atlastiAccessibility"
VERSION="1.0.0"
OUTPUT_FILE="${ADDON_NAME}-${VERSION}.nvda-addon"

echo "Building Atlas.ti Accessibility NVDA Add-on..."
echo "================================================"
echo "Author: Christos Bouronikos"
echo "Version: ${VERSION}"
echo ""

# Remove old build if exists
rm -f "$OUTPUT_FILE"

echo "Creating add-on package: $OUTPUT_FILE"

# Create the .nvda-addon file (it's just a zip with a different extension)
zip -r "$OUTPUT_FILE" \
    manifest.ini \
    appModules/ \
    globalPlugins/ \
    locale/ \
    doc/ \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*.DS_Store" \
    -x "*.git*" \
    -x "*.po"

echo ""
echo "Build complete!"
echo "================================================"
echo "Output: $(pwd)/$OUTPUT_FILE"
echo ""
echo "To install:"
echo "1. Copy $OUTPUT_FILE to your Windows machine"
echo "2. Double-click the file to install with NVDA"
echo "   OR use NVDA Menu -> Tools -> Add-on Store -> Install from external source"
echo ""
echo "If this addon helped you, please donate: https://paypal.me/christosbouronikos"
