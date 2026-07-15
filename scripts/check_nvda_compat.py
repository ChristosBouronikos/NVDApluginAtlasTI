#!/usr/bin/env python3
"""Fail if manifest.ini's lastTestedNVDAVersion is behind the latest
non-experimental NVDA API version published by nvaccess/addon-datastore.

Run manually: python3 scripts/check_nvda_compat.py
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

MANIFEST_PATH = Path(__file__).resolve().parent.parent / "addon" / "manifest.ini"
NVDA_API_VERSIONS_URL = (
    "https://raw.githubusercontent.com/nvaccess/addon-datastore/master/transform/nvdaAPIVersions.json"
)


def readManifestVersion(fieldName):
    text = MANIFEST_PATH.read_text(encoding="utf-8")
    match = re.search(rf'^{fieldName}\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        raise SystemExit(f"Could not find {fieldName} in {MANIFEST_PATH}")
    parts = tuple(int(p) for p in match.group(1).split("."))
    return parts + (0,) * (3 - len(parts))


def fetchLatestStableApiVersion():
    with urllib.request.urlopen(NVDA_API_VERSIONS_URL, timeout=30) as response:
        versions = json.load(response)
    stable = [
        (v["apiVer"]["major"], v["apiVer"]["minor"], v["apiVer"]["patch"])
        for v in versions
        if not v.get("experimental")
    ]
    if not stable:
        raise SystemExit("No stable NVDA API versions found upstream; unexpected response shape")
    return max(stable)


def main():
    lastTested = readManifestVersion("lastTestedNVDAVersion")
    latestStable = fetchLatestStableApiVersion()

    print(f"manifest lastTestedNVDAVersion: {'.'.join(map(str, lastTested))}")
    print(f"latest stable NVDA API version: {'.'.join(map(str, latestStable))}")

    if lastTested < latestStable:
        print(
            "::warning::addon/manifest.ini's lastTestedNVDAVersion "
            f"({'.'.join(map(str, lastTested))}) is behind the latest stable "
            f"NVDA API version ({'.'.join(map(str, latestStable))}). "
            "If NVDA shipped a new API-breaking release, this addon may show "
            "as 'incompatible' in the Add-on Store until it's retested and "
            "the manifest is bumped."
        )
        return 1

    print("OK: lastTestedNVDAVersion is current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
