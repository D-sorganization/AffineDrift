# Issue: CI Version Mismatch

**Status:** Open
**Severity:** Medium
**Date:** 2026-01-23
**Labels:** jules:code-quality, ci

## Description
The workflow `.github/workflows/ci-standard.yml` contains inconsistencies between installed tool versions and the versions checked against `pre-commit-config.yaml`.
*   Installs: `black==25.12.0`, `ruff==0.14.10`, `mypy==1.13.0`
*   Checks: `rev: 24.4.2` (Black), `rev: v0.5.0` (Ruff), `rev: v1.13.0` (MyPy)

## Impact
*   **Confusion:** CI might pass/fail inconsistently with local pre-commit runs.
*   **Maintenance:** "Future" versions like `black==25.12.0` are suspicious and may not be stable or real.

## Remediation
1.  **Sync:** Update `ci-standard.yml` to install versions that match `pre-commit-config.yaml`.
2.  **Verify:** Ensure `black==25.12.0` is a valid/intended version or correct it to the actual latest stable version.
