---
title: Critical Workflow Failures - Jules CLI API Migration
labels: incomplete-implementation, critical, ci-cd
assignee: unassigned
---

## Description
The following CI/CD workflows are explicitly disabled or commented out due to breaking changes in the Jules CLI API (v0.1.x). This prevents automatic conflict resolution and technical stewardship tasks from running.

### Affected Workflows
1.  **`.github/workflows/Jules-Conflict-Fix.yml`**
    *   **Status:** Warning Only (Functionality Disabled)
    *   **Error:** `TODO: Jules CLI API changed in v0.1.x - needs migration`
2.  **`.github/workflows/Jules-Tech-Custodian.yml`**
    *   **Status:** Disabled
    *   **Error:** `TODO: Jules CLI API changed in v0.1.x`

## Required Actions
- [ ] Review the new Jules CLI v0.1.x API documentation.
- [ ] Update `Jules-Conflict-Fix.yml` to use the new authentication and command structure.
- [ ] Update `Jules-Tech-Custodian.yml` to use the new authentication and command structure.
- [ ] Re-enable the workflows and verify execution.
