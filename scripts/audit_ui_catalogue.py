#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit the ATLAS.ti bilingual control catalogue and documented tree."""

import argparse
import json
import os
import re
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_MODULES = os.path.join(ROOT, "addon", "appModules")
if APP_MODULES not in sys.path:
    sys.path.insert(0, APP_MODULES)

import _atlastiUI as uiData  # noqa: E402


GREEK = re.compile(r"[Α-Ωα-ωΆ-Ώά-ώ]")


def audit():
    issues = []
    for key, element in uiData.ELEMENTS.items():
        if not str(element.get("en", "")).strip():
            issues.append({"type": "missingEnglish", "key": key})
        greek = str(element.get("el", "")).strip()
        if not greek:
            issues.append({"type": "missingGreek", "key": key})
        elif not GREEK.search(greek):
            issues.append({"type": "noGreekCharacters", "key": key, "value": greek})
        for context in element.get("contexts") or ():
            if context not in uiData.ELEMENTS:
                issues.append({"type": "unknownContext", "key": key, "context": context})

    issues.extend({"type": "unresolvedCollision", **item}
                  for item in uiData.unresolvedCollisions())

    for surfaceKey, surface in uiData.DOCUMENTED_SURFACES.items():
        if not str(surface.get("source", "")).startswith(uiData.MANUAL_ROOT):
            issues.append({"type": "invalidSource", "surface": surfaceKey})
        for elementKey in ((surface.get("root"),) + tuple(surface.get("children", ()))):
            if elementKey and elementKey not in uiData.ELEMENTS:
                issues.append({
                    "type": "unknownDocumentedElement",
                    "surface": surfaceKey,
                    "key": elementKey,
                })
    return issues


def summary():
    kinds = {}
    for element in uiData.ELEMENTS.values():
        kinds[element["kind"]] = kinds.get(element["kind"], 0) + 1
    return {
        "manualVersion": uiData.MANUAL_VERSION,
        "controls": len(uiData.ELEMENTS),
        "documentedSurfaces": len(uiData.DOCUMENTED_SURFACES),
        "exactCollisions": len(uiData.exactCollisions()),
        "unresolvedCollisions": len(uiData.unresolvedCollisions()),
        "kinds": dict(sorted(kinds.items())),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args(argv)
    issues = audit()
    payload = {"summary": summary(), "issues": issues}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("ATLAS.ti UI catalogue audit")
        for key, value in payload["summary"].items():
            print("%s: %s" % (key, value))
        if issues:
            print("Issues:")
            for issue in issues:
                print("- " + json.dumps(issue, ensure_ascii=False, sort_keys=True))
        else:
            print("Issues: none")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
