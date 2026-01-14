# Assessment B Results: Hygiene, Security & Quality

## Executive Summary

*   **Exceptional Linting Status**: The repository strictly enforces `ruff`, `black`, and `mypy` via CI/CD, resulting in a very clean codebase.
*   **AGENTS.md Violation**: The `AGENTS.md` explicitly forbids `print()` in favor of logging, yet `tools/*.py` scripts use `print()` extensively for CLI output.
*   **Security Posture**: No secrets were found in a scan. Dependencies are managed via `requirements.txt` but lack a lockfile.
*   **Code Quality**: Python code is well-typed (Mypy strict). JavaScript lacks a linter in the CI pipeline (only `node -c` syntax check).
*   **HTML/CSS Validation**: `stylelint` and `html-validate` are configured, which is excellent for a static site.

## Top 10 Hygiene Risks

1.  **Logging Violation (Severity: MEDIUM)**: `tools/` scripts use `print()` which violates `AGENTS.md`. This reduces observability in CI logs.
2.  **Missing Lockfile (Severity: MEDIUM)**: `requirements.txt` uses range pins (e.g. `>=`), allowing transitive dependency drift.
3.  **Missing JS Linting (Severity: LOW)**: `script.js` is verified only for syntax, not style/best practices (e.g. `eslint`).
4.  **Complex Regex (Severity: LOW)**: `clean_latex_comments.py` and others use complex regex without abundant comments.
5.  **Hardcoded Paths (Severity: LOW)**: Verification scripts often assume execution from repo root (documented, but fragile).
6.  **Orphaned Scripts (Severity: LOW)**: Some scripts in `tools/` (like `latex_to_quarto.py`) seem to be one-off migration scripts that should be archived.
7.  **Docstring Coverage (Severity: LOW)**: While typed, not all tool functions have descriptive docstrings.
8.  **TODOs (Severity: NIT)**: A few `TODO` comments exist, but policy usually discourages them.
9.  **File Permissions (Severity: NIT)**: Scripts in `tools/` are not executable (`chmod +x`) requiring `python tools/...`.
10. **Magic Numbers (Severity: NIT)**: Timeout values in verification scripts are hardcoded.

## Scorecard

| Category                | Score | Evidence                                    | Remediation                     |
| ----------------------- | ----- | ------------------------------------------- | ------------------------------- |
| Python Linting          | 10/10 | Ruff/Black/Mypy enforced and passing.       | N/A                             |
| JS/CSS Linting          | 7/10  | Stylelint/HTML-validate yes, ESLint no.     | Add ESLint.                     |
| Security                | 9/10  | No secrets, static site.                    | Add `requirements.lock`.        |
| Standard Adherence      | 8/10  | Fails `AGENTS.md` print rule.               | Switch to `logging`.            |
| Code Organization       | 8/10  | Flat `tools/` folder is messy.              | Group scripts.                  |
| Dependency Management   | 7/10  | `requirements.txt` without lock.            | Use `pip-tools` or `uv`.        |

**Weighted Score: 8.2/10**

## Refactoring Plan

**Quick Wins**
1.  **Enforce Logging**: Convert `print()` to `logging.info()` in `tools/check_links.py` and `tools/check_site_health.py` as they are frequently used.
2.  **Archive Migration Scripts**: Move `convert_*.py` and `latex_to_*.py` to `tools/archive/` or `legacy/` if they are no longer actively used for new content.

**Strategic Fixes**
1.  **Add ESLint**: Configure `eslint` for `docs/script.js` to catch potential browser compatibility issues or logic errors.
2.  **Generate Lockfile**: Adopt `pip-tools` to generate `requirements.lock` for reproducible CI builds.
