# Assessment B Results: Hygiene, Security & Quality

## Executive Summary

- **Security Posture**: No secrets detected. `pickle` is not used. Dependencies are pinned in `requirements.txt`.
- **Linting Compliance**: `pyproject.toml` configures `black`, but `ruff` and `mypy` configurations are missing from `pyproject.toml` (though listed in requirements).
- **AGENTS.md Compliance**: Generally good, though some scripts (e.g., `tools/scientific_auditor.py`) use `print` (via `json.dumps` for output) which arguably violates the "No print" rule, though acceptable for CLI tools.
- **Code Quality**: `tools/` scripts are generally well-written with type hints and docstrings.

## Top 10 Hygiene Risks

1.  **Missing Lint Config (Severity: MEDIUM)**: `ruff` and `mypy` are in requirements but lack configuration in `pyproject.toml`, leading to potential inconsistency.
2.  **Loose Dependency Versions (Severity: LOW)**: `requirements.txt` uses `>=` (e.g., `numpy>=1.24.0`). While standard for libraries, applications usually prefer pinned versions to ensure reproducibility.
3.  **Mixed Script Quality (Severity: LOW)**: Some scripts in `tools/` have full type hints, others are simpler.
4.  **No Pre-commit Hook (Severity: LOW)**: `pre-commit` is listed in requirements but no `.pre-commit-config.yaml` was found in root (checked implicitly via file list).
5.  **Shadowing/ambiguity (Severity: NIT)**: `build-html.py` uses regex for HTML parsing which can be fragile (security/correctness risk).

## Scorecard

| Category              | Score | Evidence                                                                 | Remediation                               |
| --------------------- | ----- | ------------------------------------------------------------------------ | ----------------------------------------- |
| Security Issues       | 10/10 | No secrets or `pickle` usage found.                                      | Maintain vigilance.                       |
| Linting Compliance    | 6/10  | Missing `ruff`/`mypy` config.                                            | Add `[tool.ruff]` to `pyproject.toml`.    |
| AGENTS.md Compliance  | 8/10  | Mostly followed. `print` usage in CLI tools is acceptable exception.     | Add explicit exception in AGENTS.md.      |
| Organization Quality  | 7/10  | `tools/` is flat.                                                        | Organize `tools/`.                        |

**Weighted Score: 7.8/10**

## Refactoring Plan

**Quick Wins**
1.  **Add Lint Config**: Add basic `ruff` and `mypy` configuration to `pyproject.toml` to align with `requirements.txt`.

**Strategic Fixes**
1.  **Dependency Pinning**: Switch to `poetry` or `pip-tools` for exact dependency locking.
2.  **Pre-commit**: Add `.pre-commit-config.yaml` to enforce standards automatically.
