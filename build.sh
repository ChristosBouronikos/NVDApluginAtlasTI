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

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ADDON_NAME="$(awk -F= '/^[[:space:]]*name[[:space:]]*=/ {print $2; exit}' addon/manifest.ini | xargs | sed 's/^\"//; s/\"$//')"
VERSION="$(awk -F= '/^[[:space:]]*version[[:space:]]*=/ {print $2; exit}' addon/manifest.ini | xargs | sed 's/^\"//; s/\"$//')"

if [[ -z "${ADDON_NAME}" || -z "${VERSION}" ]]; then
  echo "Error: name/version missing from addon/manifest.ini" >&2
  exit 1
fi

OUTPUT_FILE="${ADDON_NAME}-${VERSION}.nvda-addon"

echo "Building Atlas.ti Accessibility NVDA Add-on..."
echo "================================================"
echo "Author: Christos Bouronikos"
echo "Version: ${VERSION}"
echo ""

# Remove old build if exists
rm -f "$OUTPUT_FILE"

echo "Creating add-on package: $OUTPUT_FILE"

# Copy latest documentation to doc folders
echo "Updating documentation..."
mkdir -p addon/doc/en addon/doc/el
cp readme.md addon/doc/en/readme.md
cp readme.md addon/doc/el/readme.md
cp changelog.md addon/doc/en/changelog.md
cp changelog.md addon/doc/el/changelog.md

# Create the .nvda-addon file (it's just a zip with a different extension)
(cd addon && zip -r "../$OUTPUT_FILE" \
    . \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*.DS_Store" \
    -x "*.git*" \
    -x "*.po")

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
