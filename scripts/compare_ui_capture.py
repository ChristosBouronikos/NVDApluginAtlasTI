#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare a privacy-filtered NVDA ATLAS.ti capture with the UI catalogue.

The add-on writes one structural control per log line. This tool accepts a
complete NVDA log, a JSON list of records, or newline-delimited JSON/Python
dictionaries. It never needs or expects document, quotation, code or memo
content.
"""

import argparse
import ast
import json
import os
import sys
from collections import Counter


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_MODULES = os.path.join(ROOT, "addon", "appModules")
if APP_MODULES not in sys.path:
    sys.path.insert(0, APP_MODULES)

import _atlastiUI as uiData  # noqa: E402


LOG_PREFIX = "Atlas.ti UI control:"


def _record(value):
    """Return a normalised structural capture record or None."""
    if not isinstance(value, dict):
        return None
    return {
        "depth": int(value.get("depth", 0) or 0),
        "name": str(value.get("name", "") or ""),
        "role": str(value.get("role", "") or ""),
        "automationId": str(value.get("automationId", "") or ""),
        "className": str(value.get("className", "") or ""),
        "recognisedAs": value.get("recognisedAs"),
        "contextKeys": [str(item) for item in (value.get("contextKeys") or [])],
    }


def parseCaptureText(text):
    """Parse capture records from an NVDA log or JSON text."""
    stripped = text.strip()
    if not stripped:
        return []
    try:
        parsed = json.loads(stripped)
    except (TypeError, ValueError):
        parsed = None
    if isinstance(parsed, dict):
        parsed = parsed.get("controls", [parsed])
    if isinstance(parsed, list):
        return [record for item in parsed if (record := _record(item)) is not None]

    records = []
    for line in text.splitlines():
        payload = line.split(LOG_PREFIX, 1)[1].strip() if LOG_PREFIX in line else line.strip()
        if not payload or not payload.startswith("{"):
            continue
        try:
            item = json.loads(payload)
        except ValueError:
            try:
                item = ast.literal_eval(payload)
            except (SyntaxError, ValueError):
                continue
        record = _record(item)
        if record is not None:
            records.append(record)
    return records


def loadCapture(path):
    with open(path, "r", encoding="utf-8", errors="replace") as stream:
        return parseCaptureText(stream.read())


def _roleToken(role):
    text = str(role).upper()
    for token in (
        "MENUITEM", "CHECKBOX", "RADIOBUTTON", "TOGGLEBUTTON", "SPLITBUTTON",
        "COLUMNHEADER", "TAB", "BUTTON", "DIALOG", "WINDOW", "PANE", "GROUPING",
        "TOOLBAR", "STATUSBAR", "MENUBAR", "MENU",
    ):
        if token in text:
            return token
    return text


EXPECTED_ROLES = {
    "button": {"BUTTON", "TOGGLEBUTTON", "SPLITBUTTON"},
    "menuItem": {"MENUITEM"},
    "checkBox": {"CHECKBOX"},
    "radioButton": {"RADIOBUTTON", "TOGGLEBUTTON"},
    "column": {"COLUMNHEADER"},
}


def _kindsForRole(role):
    token = _roleToken(role)
    if token == "TAB":
        return ("tab",)
    if token == "COLUMNHEADER":
        return ("column",)
    if token in {
        "BUTTON", "MENUITEM", "CHECKBOX", "RADIOBUTTON", "TOGGLEBUTTON",
        "SPLITBUTTON",
    }:
        return ("button", "operator", "view")
    if token == "DIALOG":
        return ("dialog",)
    if token in {"WINDOW", "PANE", "GROUPING", "TOOLBAR", "STATUSBAR"}:
        return ("manager", "panel", "window", "dialog")
    return None


def _match(record):
    recognised = record.get("recognisedAs")
    if recognised in uiData.ELEMENTS:
        return uiData.ELEMENTS[recognised], "capture"
    for field in ("automationId", "className", "name"):
        value = record.get(field)
        if value:
            element = uiData.resolveExact(
                value,
                kind=_kindsForRole(record.get("role")),
                context=record.get("contextKeys"),
            )
            if element is None and field != "name":
                element = uiData.resolveExact(value, context=record.get("contextKeys"))
            if element is not None:
                return element, field
    return None, None


def compareRecords(records):
    """Return a JSON-serializable reconciliation report."""
    unknown = []
    wrongRoles = []
    changedIds = []
    missingTranslations = []
    matched = []
    seenKeys = Counter()

    for index, record in enumerate(records):
        element, matchedBy = _match(record)
        if element is None:
            unknown.append({"index": index, **record})
            continue
        key = element["key"]
        seenKeys[key] += 1
        matched.append({"index": index, "key": key, "matchedBy": matchedBy})
        if not element.get("en") or not element.get("el"):
            missingTranslations.append({"index": index, "key": key})

        semanticType = uiData.controlType(element)
        expected = EXPECTED_ROLES.get(semanticType)
        actual = _roleToken(record.get("role"))
        if expected and actual and actual not in expected:
            wrongRoles.append({
                "index": index,
                "key": key,
                "actualRole": actual,
                "expectedRoles": sorted(expected),
            })

        automationId = record.get("automationId")
        knownIds = {uiData.normalize(value) for value in element.get("ids", ())}
        if (
            matchedBy in ("name", "className")
            and automationId
            and uiData.normalize(automationId) not in knownIds
        ):
            changedIds.append({
                "index": index,
                "key": key,
                "capturedAutomationId": automationId,
                "catalogueAutomationIds": list(element.get("ids", ())),
            })

    duplicateCaptureKeys = [
        {"key": key, "count": count}
        for key, count in sorted(seenKeys.items()) if count > 1
    ]
    ambiguousLabels = []
    for token, keys in sorted(uiData._EXACT.items()):
        if len(keys) > 1:
            ambiguousLabels.append({"normalisedLabel": token, "keys": list(keys)})

    documentedKeys = {
        key
        for surface in uiData.DOCUMENTED_SURFACES.values()
        for key in ((surface.get("root"),) + tuple(surface.get("children", ())))
        if key
    }
    capturedKeys = set(seenKeys)
    return {
        "schemaVersion": 1,
        "manualVersion": uiData.MANUAL_VERSION,
        "summary": {
            "capturedControls": len(records),
            "matchedControls": len(matched),
            "unknownControls": len(unknown),
            "wrongRoles": len(wrongRoles),
            "changedAutomationIds": len(changedIds),
            "missingTranslations": len(missingTranslations),
            "documentedKeysObserved": len(documentedKeys.intersection(capturedKeys)),
            "documentedKeysExpected": len(documentedKeys),
        },
        "unknownControls": unknown,
        "wrongRoles": wrongRoles,
        "changedAutomationIds": changedIds,
        "missingTranslations": missingTranslations,
        "duplicateCapturedElements": duplicateCaptureKeys,
        "ambiguousCatalogueLabels": ambiguousLabels,
        "documentedKeysNotObserved": sorted(documentedKeys - capturedKeys),
        "matched": matched,
    }


def markdownReport(report):
    summary = report["summary"]
    lines = [
        "# ATLAS.ti UI capture comparison",
        "",
        "Manual version: `%s`" % report["manualVersion"],
        "",
        "| Check | Count |",
        "|---|---:|",
    ]
    for key in (
        "capturedControls", "matchedControls", "unknownControls", "wrongRoles",
        "changedAutomationIds", "missingTranslations", "documentedKeysObserved",
        "documentedKeysExpected",
    ):
        lines.append("| %s | %s |" % (key, summary[key]))

    sections = (
        ("Unknown controls", "unknownControls"),
        ("Role mismatches", "wrongRoles"),
        ("Changed automation IDs", "changedAutomationIds"),
        ("Missing translations", "missingTranslations"),
        ("Duplicate captured elements", "duplicateCapturedElements"),
    )
    for title, key in sections:
        lines.extend(("", "## " + title, ""))
        items = report[key]
        if not items:
            lines.append("None.")
        else:
            for item in items:
                lines.append("- `%s`" % json.dumps(item, ensure_ascii=False, sort_keys=True))
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", nargs="?", help="NVDA log or JSON capture")
    parser.add_argument("--json-output", help="write the comparison report as JSON")
    parser.add_argument("--markdown-output", help="write a human-readable Markdown report")
    parser.add_argument("--export-catalogue", help="write the bilingual catalogue as JSON")
    args = parser.parse_args(argv)

    if args.export_catalogue:
        payload = {
            "schemaVersion": 1,
            "manualVersion": uiData.MANUAL_VERSION,
            "manualRoot": uiData.MANUAL_ROOT,
            "surfaces": uiData.DOCUMENTED_SURFACES,
            "controls": uiData.catalogueRecords(),
        }
        with open(args.export_catalogue, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")

    if not args.capture:
        if args.export_catalogue:
            return 0
        parser.error("capture is required unless --export-catalogue is used")

    report = compareRecords(loadCapture(args.capture))
    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
    if args.markdown_output:
        with open(args.markdown_output, "w", encoding="utf-8") as stream:
            stream.write(markdownReport(report))
    if not args.json_output and not args.markdown_output:
        print(markdownReport(report), end="")
    return 1 if report["summary"]["unknownControls"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
