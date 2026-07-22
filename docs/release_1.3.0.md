# ATLAS.ti Accessibility 1.3.0 release handoff

## Included

- Complete English/Greek catalogue exceeding 116 buttons, 22 columns and 18
  panes, with all 11 managers and 11 tabs.
- Documentation-derived ATLAS.ti 26 semantic tree tied to official manual
  version 26.1.1+34607.
- Context-aware collision resolution and explicit control-role speech.
- Manager, filter, context-menu, Welcome, Quotation Reader and five dialog
  overlay families.
- Translated checked, selected, expanded, collapsed, unavailable and pressed states.
- Focus recovery through the first enabled interactive descendant.
- Disabled-by-default privacy-filtered Windows UI-tree capture.
- Capture comparison, catalogue export and release-audit tools.
- Privacy corpus, collision tests and Windows validation checklist.

## Release commands

```text
python -m unittest discover -s tests
python scripts/audit_ui_catalogue.py
python scripts/check_nvda_compat.py
msgfmt --check --statistics -o addon/locale/el/LC_MESSAGES/nvda.mo addon/locale/el/LC_MESSAGES/nvda.po
./build.sh
unzip -t atlastiAccessibility-1.3.0.nvda-addon
shasum -a 256 atlastiAccessibility-1.3.0.nvda-addon
```

## Windows evidence still required

The manual does not publish AutomationIds, UIA roles, class names or actual
accessibility child order. Before a stable release, run the Windows checklist
and reconcile its safe capture. That is the source of truth for ATLAS.ti 26 UIA.

## Prepared commit

Suggested subject:

```text
feat: harden ATLAS.ti 26 accessibility and UI capture tooling
```

Include the add-on, tests, scripts, generated catalogue, documentation, locale,
build and workflow changes. Exclude the untracked `output/` analysis artifact
unless it is intentionally part of the release. The repository already
contained a broad dirty worktree before this pass, so review the staged diff
before creating a single release commit.
