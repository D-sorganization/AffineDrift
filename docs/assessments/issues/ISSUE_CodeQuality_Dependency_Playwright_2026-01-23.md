# Issue: Missing Dependency - Playwright

**Status:** Open
**Severity:** High
**Date:** 2026-01-23
**Labels:** jules:code-quality, dependencies

## Description
The script `tests/verification/verify_console.py` imports `playwright`, but this package is not listed in `requirements.txt`. This causes "Incomplete Dependency Declaration" errors in strict environments and may cause CI failures if the environment is not pre-seeded.

## Impact
*   **Reproducibility:** Fresh installs cannot run verification tests.
*   **CI Stability:** Relies on implicit environment state rather than explicit declarations.

## Remediation
1.  **Add:** Add `playwright` (and potentially `pytest-playwright`) to `requirements.txt`.
