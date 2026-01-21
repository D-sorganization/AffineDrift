---
title: "Critical: Jules Automation Workflows Disabled"
date: 2026-01-21
status: Open
severity: Critical
labels: [jules:code-quality, critical, automation-gap]
---

## Description
Two critical automation workflows are explicitly disabled in `.github/workflows/` due to API changes in the Jules CLI.

## Details
*   **Workflow:** `.github/workflows/Jules-Tech-Custodian.yml`
    *   **Status:** `if: false`
    *   **Reason:** `# TODO: Jules CLI API changed in v0.1.x`
*   **Workflow:** `.github/workflows/Jules-Conflict-Fix.yml`
    *   **Status:** `if: false`
    *   **Reason:** `# TODO: Jules CLI API changed in v0.1.x - needs migration`

## Impact
*   **Maintenance:** Automated technical debt cleanup is paused.
*   **Resilience:** Automated merge conflict resolution is disabled.

## Recommended Action
Update the workflows to match the new Jules CLI v0.1.x API and re-enable them.
