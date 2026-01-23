# Issue: Critical Automation Disabled

**Status:** Open
**Severity:** Critical
**Date:** 2026-01-23
**Labels:** jules:code-quality, critical, automation

## Description
Two critical maintenance workflows are disabled (`if: false`) due to API changes in the Jules CLI (v0.1.x migration):
1.  `.github/workflows/Jules-Tech-Custodian.yml`
2.  `.github/workflows/Jules-Conflict-Fix.yml`

## Impact
*   **Tech Debt:** Code quality issues are not being automatically fixed.
*   **Maintenance:** Merge conflicts are not being resolved automatically, increasing developer load.

## Remediation
1.  **Migrate:** Update the workflow files to use the new Jules CLI syntax (`jules new` / `jules remote pull`).
2.  **Enable:** Remove `if: false` and test the workflows.
