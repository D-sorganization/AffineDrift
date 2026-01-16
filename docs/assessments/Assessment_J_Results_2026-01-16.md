# Assessment J Results: Extensibility & Plugin Architecture

## Executive Summary

- **Extensibility**: The system is modular (`tools/`, `articles/`). Adding new articles is easy (add file, update list).
- **Plugins**: Quarto has a plugin system (extensions), but this repo uses a custom `build-html.py` which might not support them fully if they require complex processing.
- **Customization**: `custom.scss` allows styling changes.

## Top Extensibility Risks

1.  **Hardcoded Build Script (Severity: HIGH)**: As noted in Assessment A, `build-html.py` requires manual updates for new root files, hampering extensibility.

## Scorecard

| Category              | Score | Evidence                                                                 | Remediation                               |
| --------------------- | ----- | ------------------------------------------------------------------------ | ----------------------------------------- |
| Extension Points      | 7/10  | Quarto is extensible, but custom build limits it.                        | Fix `build-html.py`.                      |
| API Stability         | N/A   | Not an API.                                                              | N/A                                       |
| Plugin System         | 6/10  | Limited by custom build.                                                 | Restore full Quarto build if possible.    |
| Contribution Docs     | 8/10  | `CONTRIBUTING.md` (implied or in README) exists.                         | N/A                                       |

**Weighted Score: 7.0/10**

## Refactoring Plan

**Quick Wins**
1.  **Globbing**: Update `build-html.py` to use `glob` for file discovery.

**Strategic Fixes**
1.  **Quarto CLI**: Prioritize using standard Quarto CLI in CI/Dev to leverage its full ecosystem.
