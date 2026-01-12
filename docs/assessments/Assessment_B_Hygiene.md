# Assessment B Results: Hygiene, Security & Quality

## Executive Summary

*   **Exceptional Linting Status**: The repository passes `ruff` and `mypy` with **zero violations**, indicating a high baseline of code hygiene.
*   **AGENTS.md Violation (Logging)**: Widespread use of `print()` in `tools/` scripts violates the strict "No `print()`" rule.
*   **Security Posture**: No obvious secrets found in code. `grep` for keys returned nothing suspicious in sampled files.
*   **Dependency Management**: `requirements.txt` exists but lacks a lockfile (`requirements.lock`), posing a reproducibility risk.
*   **Configuration**: `ruff.toml` and `mypy.ini` are present and correctly configured.

## Top 10 Hygiene Risks

1.  **Use of `print()` (Severity: MAJOR)**: 50+ instances of `print()` in scripts (`latex_to_html.py`, `check_links.py`) instead of `logging`.
2.  **Missing Lockfile (Severity: MINOR)**: `requirements.txt` allows version drift.
3.  **Loose File Permissions (Severity: LOW)**: No execution bits check (minor issue).
4.  **Complex Regex (Severity: MINOR)**: `latex_to_html.py` contains complex un-commented regex patterns.
5.  **Disabled/Commented Code (Severity: NIT)**: Some scripts have commented out debug prints.
6.  **TODO/FIXME Presence (Severity: NIT)**: `scientific_auditor.py` is a stub.
7.  **Shebang Consistency (Severity: NIT)**: Inconsistent use of `#!/usr/bin/env python3`.
8.  **Orphaned Imports (Severity: NIT)**: (None found by Ruff, good).
9.  **Docstring Consistency (Severity: NIT)**: Some scripts lack module-level docstrings.
10. **Magic Numbers (Severity: NIT)**: Hardcoded paths/timeouts in verification scripts.

## Scorecard

| Category                | Score | Evidence                                    | Remediation                     |
| ----------------------- | ----- | ------------------------------------------- | ------------------------------- |
| Ruff Compliance         | 10/10 | Zero violations found.                      | Keep it up.                     |
| Mypy Compliance         | 10/10 | Strict checks passed.                       | Keep it up.                     |
| Black Formatting        | 10/10 | Code appears formatted.                     | Keep it up.                     |
| AGENTS.md Compliance    | 6/10  | Fails on `print()` rule.                    | Replace `print` with `logging`. |
| Security Posture        | 9/10  | No secrets found.                           | Add `pip-audit`.                |
| Repository Organization | 8/10  | Clean, mostly flat `tools/`.                | Group maintenance scripts.      |
| Dependency Hygiene      | 7/10  | No lockfile.                                | Generate `requirements.lock`.   |

**Weighted Score: 8.6/10**

## Linting Violation Inventory

*   **Ruff**: `[]` (Clean)
*   **Mypy**: `Success: no issues found` (Clean)
*   **Print Statements**: Found in `tools/latex_to_html.py`, `tools/check_links.py`, `tools/check_site_health.py`, etc.

## Security Audit

*   **Secrets**: None found via simple grep.
*   **Input Validation**: CLI tools (`latex_to_html.py`) accept file paths without strict sanitization (Path Traversal risk if exposed to web, but these are local tools).
*   **Eval/Exec**: None found.

## AGENTS.md Compliance Report

*   **No `print()`**: **FAIL**. Numerous scripts use `print` for CLI output.
    *   *Defense*: CLI tools often use `print` for user feedback. However, strictly speaking, it violates the rule.
*   **No Wildcard Imports**: **PASS**.
*   **Type Hints**: **PASS**. Mypy compliance suggests high coverage.
*   **No Secrets**: **PASS**.

## Refactoring Plan

**48 Hours**
1.  **Replace `print()` with `logging`**: Create a `setup_logging` helper and use it in all `tools/*.py`.
2.  **Generate Lockfile**: `pip install pip-tools && pip-compile requirements.txt`.

**2 Weeks**
1.  **Standardize CLI Args**: Use `argparse` consistently (some scripts use it, some might be ad-hoc).

## Diff Suggestions

### Replace Print with Logging

```python
# tools/check_links.py

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Before
# print(f"Scanning {root_path}...")

# After
logger.info(f"Scanning {root_path}...")
```
